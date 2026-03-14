"""Remove dead class property assignments.

After ClassStringDecoder inlines decoded constants, assignments like:
    _0x3bb8cb.prop = "value";
    _0x279589.XXX = "literal";

become dead code. This transform detects class variables and removes
their property assignments when the properties are dead.

Uses two strategies:
1. Properties that are written but never read are dead.
2. If a class variable is only referenced in its own property assignments
   and inside class bodies (never passed around or called), all its
   properties are considered dead.
"""

from __future__ import annotations

from ..traverser import REMOVE
from ..traverser import simple_traverse
from ..traverser import traverse
from ..utils.ast_helpers import get_member_names
from ..utils.ast_helpers import is_identifier
from ..utils.ast_helpers import is_string_literal
from .base import Transform


class DeadClassPropRemover(Transform):
    """Remove dead property assignments on class variables."""

    def execute(self) -> bool:
        """Detect and remove dead class property assignments."""
        class_variables, class_aliases, reverse_aliases, class_node_to_name = self._find_class_declarations()

        if not class_variables:
            return False

        def normalize(object_name: str) -> str:
            """Resolve class aliases to their canonical (outer) name."""
            return class_aliases.get(object_name, object_name)

        def has_standalone_reference(name: str) -> bool:
            """Check if a class variable has any standalone (non-member) references."""
            if standalone_references.get(name, 0) > 0:
                return True
            canonical = class_aliases.get(name, name)
            if standalone_references.get(canonical, 0) > 0:
                return True
            for inner_name in reverse_aliases.get(name, ()):
                if standalone_references.get(inner_name, 0) > 0:
                    return True
            return False

        member_references, standalone_references, this_property_reads = self._classify_references(
            class_variables,
            class_node_to_name,
            class_aliases,
        )

        classes_with_this = self._find_classes_with_this_reads(
            this_property_reads,
            class_aliases,
        )

        fully_dead_classes = {
            variable
            for variable in class_variables
            if not has_standalone_reference(variable) and variable not in classes_with_this
        }

        escaped_classes = {normalize(variable) for variable in class_variables if has_standalone_reference(variable)}

        dead_properties = self._find_dead_properties(
            class_variables,
            class_aliases,
            fully_dead_classes,
            escaped_classes,
            this_property_reads,
            normalize,
        )

        if not dead_properties:
            return False

        self._remove_dead_statements(dead_properties, normalize)
        return self.has_changed()

    def _find_class_declarations(
        self,
    ) -> tuple[set[str], dict[str, str], dict[str, set[str]], dict[int, str]]:
        """Scan AST for class declarations and their aliases.

        Returns (class_variables, class_aliases, reverse_aliases, class_node_to_name).
        """
        class_variables: set[str] = set()
        class_aliases: dict[str, str] = {}
        reverse_aliases: dict[str, set[str]] = {}
        class_node_to_name: dict[int, str] = {}

        def register_class(
            outer_name: str,
            class_expression: dict,
        ) -> None:
            """Register a class variable and its inner alias if present."""
            class_variables.add(outer_name)
            class_node_to_name[id(class_expression)] = outer_name
            class_identifier = class_expression.get('id')
            if not (class_identifier and is_identifier(class_identifier)):
                return
            inner_name = class_identifier['name']
            if inner_name == outer_name:
                return
            class_variables.add(inner_name)
            class_aliases[inner_name] = outer_name
            reverse_aliases.setdefault(outer_name, set()).add(inner_name)

        def visitor(node: dict, _parent: dict | None) -> None:
            """Find class expressions assigned to variables."""
            match node.get('type'):
                case 'VariableDeclarator':
                    initializer = node.get('init')
                    if not (initializer and initializer.get('type') == 'ClassExpression'):
                        return
                    declarator_identifier = node.get('id')
                    if declarator_identifier and is_identifier(declarator_identifier):
                        register_class(declarator_identifier['name'], initializer)
                case 'AssignmentExpression':
                    right_side = node.get('right')
                    if not (right_side and right_side.get('type') == 'ClassExpression'):
                        return
                    left_side = node.get('left')
                    if left_side and is_identifier(left_side):
                        register_class(left_side['name'], right_side)

        simple_traverse(self.ast, visitor)
        return class_variables, class_aliases, reverse_aliases, class_node_to_name

    def _classify_references(
        self,
        class_variables: set[str],
        class_node_to_name: dict[int, str],
        class_aliases: dict[str, str],
    ) -> tuple[dict[str, int], dict[str, int], set[tuple[str, str]]]:
        """Classify identifier references and collect this.prop reads.

        Returns (member_references, standalone_references, this_property_reads).
        """
        member_references: dict[str, int] = {variable: 0 for variable in class_variables}
        standalone_references: dict[str, int] = {variable: 0 for variable in class_variables}
        this_property_reads: set[tuple[str, str]] = set()

        def collect_this_reads_in_class(class_node: dict, class_name: str) -> None:
            """Walk a class body and record this.prop reads."""

            def visit_member(node: dict, _parent: dict | None) -> None:
                """Check if node is a this.prop member expression."""
                if node.get('type') != 'MemberExpression':
                    return
                object_node = node.get('object')
                if not object_node or object_node.get('type') != 'ThisExpression':
                    return
                property_node = node.get('property')
                if not property_node:
                    return
                if node.get('computed'):
                    if is_string_literal(property_node):
                        this_property_reads.add((class_name, property_node['value']))
                elif is_identifier(property_node):
                    this_property_reads.add((class_name, property_node['name']))

            simple_traverse(class_node.get('body', {}), visit_member)

        def classify_node(node: dict, parent: dict | None) -> None:
            """Classify each identifier as member-access or standalone reference."""
            # Collect this.prop reads inside class bodies
            if node.get('type') == 'ClassExpression':
                class_name = class_node_to_name.get(id(node))
                if class_name:
                    collect_this_reads_in_class(node, class_name)
                return

            if not is_identifier(node):
                return
            name = node.get('name')
            if name not in class_variables:
                return

            if self._is_declaration_site(node, parent):
                return

            # Object of a member expression -> member reference
            if parent and parent.get('type') == 'MemberExpression' and node is parent.get('object'):
                member_references[name] = member_references.get(name, 0) + 1
                return

            # RHS of member assignment (X.prop = classVar) means the class escapes
            if (
                parent
                and parent.get('type') == 'AssignmentExpression'
                and node is parent.get('right')
                and parent.get('left', {}).get('type') == 'MemberExpression'
            ):
                standalone_references[name] = standalone_references.get(name, 0) + 1
                return

            standalone_references[name] = standalone_references.get(name, 0) + 1

        simple_traverse(self.ast, classify_node)
        return member_references, standalone_references, this_property_reads

    @staticmethod
    def _is_declaration_site(node: dict, parent: dict | None) -> bool:
        """Check if this identifier is at a declaration/class-expression-id site."""
        if not parent:
            return False
        match parent.get('type'):
            case 'VariableDeclarator' if node is parent.get('id'):
                return True
            case 'AssignmentExpression' if (
                node is parent.get('left') and parent.get('right', {}).get('type') == 'ClassExpression'
            ):
                return True
            case 'ClassExpression' if node is parent.get('id'):
                return True
        return False

    @staticmethod
    def _find_classes_with_this_reads(
        this_property_reads: set[tuple[str, str]],
        class_aliases: dict[str, str],
    ) -> set[str]:
        """Return set of class names that read their own properties via this."""
        classes_with_this: set[str] = set()
        for name, _property in this_property_reads:
            classes_with_this.add(name)
            classes_with_this.add(class_aliases.get(name, name))
        return classes_with_this

    def _find_dead_properties(
        self,
        class_variables: set[str],
        class_aliases: dict[str, str],
        fully_dead_classes: set[str],
        escaped_classes: set[str],
        this_property_reads: set[tuple[str, str]],
        normalize: callable,
    ) -> set[tuple[str, str]]:
        """Identify properties that are written but never read."""
        write_set: set[tuple[str, str]] = set()
        read_set: set[tuple[str, str]] = set()

        def count_property_references(node: dict, _parent: dict | None) -> None:
            """Count reads and writes per (class, property) pair."""
            if node.get('type') != 'MemberExpression':
                return
            object_name, property_name = get_member_names(node)
            if not object_name or object_name not in class_variables:
                return
            canonical = normalize(object_name)
            if canonical in fully_dead_classes or canonical in escaped_classes:
                return

            reference_pair = (canonical, property_name)
            if _parent and _parent.get('type') == 'AssignmentExpression' and node is _parent.get('left'):
                write_set.add(reference_pair)
            else:
                read_set.add(reference_pair)

        simple_traverse(self.ast, count_property_references)
        read_set |= {(normalize(name), property_name) for name, property_name in this_property_reads}

        dead_properties: set[tuple[str, str]] = {
            written_pair for written_pair in write_set if written_pair not in read_set
        }

        if fully_dead_classes:
            fully_dead_canonical = {normalize(variable) for variable in fully_dead_classes} | fully_dead_classes

            def collect_fully_dead(node: dict, _parent: dict | None) -> None:
                """Collect all property assignments on fully dead classes."""
                if node.get('type') != 'AssignmentExpression' or node.get('operator') != '=':
                    return
                object_name, property_name = get_member_names(node.get('left'))
                if object_name and object_name in fully_dead_canonical:
                    dead_properties.add((normalize(object_name), property_name))

            simple_traverse(self.ast, collect_fully_dead)

        return dead_properties

    def _remove_dead_statements(
        self,
        dead_properties: set[tuple[str, str]],
        normalize: callable,
    ) -> None:
        """Remove expression statements that assign to dead properties."""

        def is_dead_property(object_name: str, property_name: str) -> bool:
            """Check if a (class, property) pair is dead."""
            canonical = normalize(object_name)
            return (canonical, property_name) in dead_properties or (object_name, property_name) in dead_properties

        def remove_visitor(
            node: dict,
            _parent: dict | None,
            _key: str | None,
            _index: int | None,
        ) -> object | None:
            """Remove or trim dead assignment statements."""
            if node.get('type') != 'ExpressionStatement':
                return None
            expression = node.get('expression')
            if not expression:
                return None

            if expression.get('type') == 'AssignmentExpression' and expression.get('operator') == '=':
                object_name, property_name = get_member_names(expression.get('left'))
                if object_name and is_dead_property(object_name, property_name):
                    self.set_changed()
                    return REMOVE

            if expression.get('type') != 'SequenceExpression':
                return None

            sub_expressions = expression.get('expressions', [])
            remaining = []
            for sub_expression in sub_expressions:
                if sub_expression.get('type') == 'AssignmentExpression' and sub_expression.get('operator') == '=':
                    object_name, property_name = get_member_names(sub_expression.get('left'))
                    if object_name and is_dead_property(object_name, property_name):
                        self.set_changed()
                        continue
                remaining.append(sub_expression)

            if not remaining:
                return REMOVE
            if len(remaining) < len(sub_expressions):
                if len(remaining) == 1:
                    node['expression'] = remaining[0]
                else:
                    expression['expressions'] = remaining
            return None

        traverse(self.ast, {'enter': remove_visitor})
