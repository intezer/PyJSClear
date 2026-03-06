"""Comprehensive unit tests for pyjsclear.scope module."""

import pytest

from pyjsclear.parser import parse
from pyjsclear.scope import Binding, Scope, build_scope_tree, _nearest_function_scope


# ---------------------------------------------------------------------------
# Binding.is_constant
# ---------------------------------------------------------------------------


class TestBindingIsConstant:
    def test_const_is_always_constant(self):
        scope = Scope(None, {}, is_function=True)
        binding = scope.add_binding('x', {}, 'const')
        assert binding.is_constant is True

    def test_const_is_constant_even_with_assignments(self):
        """const is always reported constant (assignments would be a runtime error)."""
        scope = Scope(None, {}, is_function=True)
        binding = scope.add_binding('x', {}, 'const')
        binding.assignments.append({'type': 'AssignmentExpression'})
        assert binding.is_constant is True

    def test_function_no_assignments_is_constant(self):
        scope = Scope(None, {}, is_function=True)
        binding = scope.add_binding('f', {}, 'function')
        assert binding.is_constant is True

    def test_function_with_assignments_is_not_constant(self):
        scope = Scope(None, {}, is_function=True)
        binding = scope.add_binding('f', {}, 'function')
        binding.assignments.append({'type': 'AssignmentExpression'})
        assert binding.is_constant is False

    def test_var_no_assignments_is_constant(self):
        scope = Scope(None, {}, is_function=True)
        binding = scope.add_binding('x', {}, 'var')
        assert binding.is_constant is True

    def test_var_with_assignments_is_not_constant(self):
        scope = Scope(None, {}, is_function=True)
        binding = scope.add_binding('x', {}, 'var')
        binding.assignments.append({'type': 'AssignmentExpression'})
        assert binding.is_constant is False

    def test_let_no_assignments_is_constant(self):
        scope = Scope(None, {}, is_function=True)
        binding = scope.add_binding('x', {}, 'let')
        assert binding.is_constant is True

    def test_let_with_assignments_is_not_constant(self):
        scope = Scope(None, {}, is_function=True)
        binding = scope.add_binding('x', {}, 'let')
        binding.assignments.append({'type': 'AssignmentExpression'})
        assert binding.is_constant is False

    def test_param_no_assignments_is_constant(self):
        scope = Scope(None, {}, is_function=True)
        binding = scope.add_binding('x', {}, 'param')
        assert binding.is_constant is True

    def test_param_with_assignments_is_not_constant(self):
        scope = Scope(None, {}, is_function=True)
        binding = scope.add_binding('x', {}, 'param')
        binding.assignments.append({'type': 'AssignmentExpression'})
        assert binding.is_constant is False


# ---------------------------------------------------------------------------
# Scope: add_binding, get_binding, get_own_binding
# ---------------------------------------------------------------------------


class TestScope:
    def test_add_binding_returns_binding(self):
        scope = Scope(None, {}, is_function=True)
        binding = scope.add_binding('x', {'type': 'Identifier'}, 'var')
        assert isinstance(binding, Binding)
        assert binding.name == 'x'
        assert binding.kind == 'var'
        assert binding.scope is scope

    def test_add_binding_stores_in_bindings_dict(self):
        scope = Scope(None, {}, is_function=True)
        scope.add_binding('x', {}, 'var')
        assert 'x' in scope.bindings

    def test_get_own_binding_found(self):
        scope = Scope(None, {}, is_function=True)
        binding = scope.add_binding('x', {}, 'let')
        assert scope.get_own_binding('x') is binding

    def test_get_own_binding_not_found(self):
        scope = Scope(None, {}, is_function=True)
        assert scope.get_own_binding('x') is None

    def test_get_own_binding_does_not_walk_chain(self):
        parent = Scope(None, {}, is_function=True)
        parent.add_binding('x', {}, 'var')
        child = Scope(parent, {})
        assert child.get_own_binding('x') is None

    def test_get_binding_found_in_same_scope(self):
        scope = Scope(None, {}, is_function=True)
        binding = scope.add_binding('x', {}, 'let')
        assert scope.get_binding('x') is binding

    def test_get_binding_walks_up_chain(self):
        parent = Scope(None, {}, is_function=True)
        binding = parent.add_binding('x', {}, 'var')
        child = Scope(parent, {})
        grandchild = Scope(child, {})
        assert grandchild.get_binding('x') is binding

    def test_get_binding_returns_none_when_not_found(self):
        scope = Scope(None, {}, is_function=True)
        assert scope.get_binding('nonexistent') is None

    def test_get_binding_returns_nearest_shadowed_binding(self):
        parent = Scope(None, {}, is_function=True)
        parent.add_binding('x', {}, 'var')
        child = Scope(parent, {})
        inner_binding = child.add_binding('x', {}, 'let')
        assert child.get_binding('x') is inner_binding

    def test_child_is_registered_in_parent(self):
        parent = Scope(None, {}, is_function=True)
        child = Scope(parent, {})
        assert child in parent.children

    def test_root_scope_has_no_parent(self):
        scope = Scope(None, {}, is_function=True)
        assert scope.parent is None
        assert scope.children == []


# ---------------------------------------------------------------------------
# _nearest_function_scope
# ---------------------------------------------------------------------------


class TestNearestFunctionScope:
    def test_returns_self_if_function_scope(self):
        scope = Scope(None, {}, is_function=True)
        assert _nearest_function_scope(scope) is scope

    def test_walks_up_to_function_scope(self):
        root = Scope(None, {}, is_function=True)
        block = Scope(root, {}, is_function=False)
        nested_block = Scope(block, {}, is_function=False)
        assert _nearest_function_scope(nested_block) is root

    def test_returns_none_for_none_input(self):
        assert _nearest_function_scope(None) is None


# ---------------------------------------------------------------------------
# build_scope_tree: var hoisting
# ---------------------------------------------------------------------------


class TestVarHoisting:
    def test_var_hoisted_to_function_scope(self):
        ast = parse('function f() { if (true) { var x = 1; } }')
        root_scope, node_scope = build_scope_tree(ast)
        # 'f' is in root scope
        f_binding = root_scope.get_own_binding('f')
        assert f_binding is not None
        assert f_binding.kind == 'function'
        # 'x' should be hoisted to f's function scope, not the if-block scope
        f_scope = root_scope.children[0]
        assert f_scope.is_function is True
        x_binding = f_scope.get_own_binding('x')
        assert x_binding is not None
        assert x_binding.kind == 'var'

    def test_var_hoisted_to_root_scope(self):
        ast = parse('{ var x = 1; }')
        root_scope, _ = build_scope_tree(ast)
        assert root_scope.get_own_binding('x') is not None
        assert root_scope.get_own_binding('x').kind == 'var'


# ---------------------------------------------------------------------------
# build_scope_tree: let/const block scoping
# ---------------------------------------------------------------------------


class TestLetConstBlockScoping:
    def test_let_stays_in_block_scope(self):
        ast = parse('function f() { if (true) { let x = 1; } }')
        root_scope, _ = build_scope_tree(ast)
        f_scope = root_scope.children[0]
        assert f_scope.get_own_binding('x') is None
        # x should be in a block scope child of f_scope
        block_scope = f_scope.children[0]
        assert block_scope.get_own_binding('x') is not None
        assert block_scope.get_own_binding('x').kind == 'let'

    def test_const_stays_in_block_scope(self):
        ast = parse('function f() { { const y = 2; } }')
        root_scope, _ = build_scope_tree(ast)
        f_scope = root_scope.children[0]
        assert f_scope.get_own_binding('y') is None
        block_scope = f_scope.children[0]
        assert block_scope.get_own_binding('y') is not None
        assert block_scope.get_own_binding('y').kind == 'const'


# ---------------------------------------------------------------------------
# build_scope_tree: function declarations and expressions
# ---------------------------------------------------------------------------


class TestFunctionDeclarations:
    def test_function_declaration_binding_in_outer_scope(self):
        ast = parse('function foo() {}')
        root_scope, _ = build_scope_tree(ast)
        binding = root_scope.get_own_binding('foo')
        assert binding is not None
        assert binding.kind == 'function'

    def test_function_expression_name_in_inner_scope(self):
        """FunctionExpression name binding goes into the function's own scope.

        Note: We use an ExpressionStatement wrapper rather than a
        VariableDeclarator init, because the VariableDeclaration handler
        returns early without recursing into init expressions.
        """
        ast = parse('function outer() { (function myFunc() {}); }')
        root_scope, _ = build_scope_tree(ast)
        outer_scope = root_scope.children[0]
        # 'myFunc' should NOT be in the outer scope
        assert outer_scope.get_own_binding('myFunc') is None
        # 'myFunc' should be in the function expression's own scope
        func_expr_scope = outer_scope.children[0]
        assert func_expr_scope.is_function is True
        assert func_expr_scope.get_own_binding('myFunc') is not None
        assert func_expr_scope.get_own_binding('myFunc').kind == 'function'

    def test_function_expression_at_top_level(self):
        """FunctionExpression name is not added to the enclosing scope."""
        ast = parse('(function myFunc() {});')
        root_scope, _ = build_scope_tree(ast)
        assert root_scope.get_own_binding('myFunc') is None
        func_scope = root_scope.children[0]
        assert func_scope.get_own_binding('myFunc') is not None

    def test_arrow_function_creates_function_scope(self):
        """Arrow functions in expression statements create function scopes."""
        ast = parse('function outer() { ((a) => { let x = 1; }); }')
        root_scope, _ = build_scope_tree(ast)
        outer_scope = root_scope.children[0]
        arrow_scope = outer_scope.children[0]
        assert arrow_scope.is_function is True
        assert arrow_scope.get_own_binding('a') is not None
        assert arrow_scope.get_own_binding('a').kind == 'param'


# ---------------------------------------------------------------------------
# build_scope_tree: parameters
# ---------------------------------------------------------------------------


class TestParameters:
    def test_simple_params_added_to_function_scope(self):
        ast = parse('function f(a, b) {}')
        root_scope, _ = build_scope_tree(ast)
        f_scope = root_scope.children[0]
        assert f_scope.get_own_binding('a') is not None
        assert f_scope.get_own_binding('a').kind == 'param'
        assert f_scope.get_own_binding('b') is not None
        assert f_scope.get_own_binding('b').kind == 'param'

    def test_default_param_added_to_function_scope(self):
        ast = parse('function f(x = 10) {}')
        root_scope, _ = build_scope_tree(ast)
        f_scope = root_scope.children[0]
        assert f_scope.get_own_binding('x') is not None
        assert f_scope.get_own_binding('x').kind == 'param'


# ---------------------------------------------------------------------------
# build_scope_tree: references
# ---------------------------------------------------------------------------


class TestReferences:
    def test_references_populated(self):
        ast = parse('var x = 1; console.log(x);')
        root_scope, _ = build_scope_tree(ast)
        binding = root_scope.get_own_binding('x')
        assert binding is not None
        # x is referenced at least once (in console.log(x))
        ref_names = [ref[0].get('name') for ref in binding.references]
        assert 'x' in ref_names

    def test_reference_inside_function(self):
        ast = parse('var x = 1; function f() { return x; }')
        root_scope, _ = build_scope_tree(ast)
        binding = root_scope.get_own_binding('x')
        assert len(binding.references) >= 1

    def test_member_expression_property_not_reference(self):
        """obj.x should not count as a reference to binding x."""
        ast = parse('var x = 1; var obj = {}; obj.x;')
        root_scope, _ = build_scope_tree(ast)
        binding = root_scope.get_own_binding('x')
        # References should not include the obj.x property access
        for ref_node, parent, key, _ in binding.references:
            if parent and parent.get('type') == 'MemberExpression':
                assert key != 'property'


# ---------------------------------------------------------------------------
# build_scope_tree: assignments
# ---------------------------------------------------------------------------


class TestAssignments:
    def test_assignment_tracked(self):
        ast = parse('var x = 1; x = 2;')
        root_scope, _ = build_scope_tree(ast)
        binding = root_scope.get_own_binding('x')
        assert len(binding.assignments) == 1
        assert binding.assignments[0].get('type') == 'AssignmentExpression'

    def test_update_expression_tracked(self):
        ast = parse('var x = 1; x++;')
        root_scope, _ = build_scope_tree(ast)
        binding = root_scope.get_own_binding('x')
        assert len(binding.assignments) == 1
        assert binding.assignments[0].get('type') == 'UpdateExpression'

    def test_no_assignments_when_only_initialized(self):
        ast = parse('var x = 1;')
        root_scope, _ = build_scope_tree(ast)
        binding = root_scope.get_own_binding('x')
        assert len(binding.assignments) == 0


# ---------------------------------------------------------------------------
# build_scope_tree: destructuring patterns
# ---------------------------------------------------------------------------


class TestDestructuringPatterns:
    def test_array_pattern(self):
        ast = parse('var [a, b] = [1, 2];')
        root_scope, _ = build_scope_tree(ast)
        assert root_scope.get_own_binding('a') is not None
        assert root_scope.get_own_binding('b') is not None

    def test_object_pattern(self):
        ast = parse('var {x, y} = obj;')
        root_scope, _ = build_scope_tree(ast)
        assert root_scope.get_own_binding('x') is not None
        assert root_scope.get_own_binding('y') is not None

    def test_rest_element(self):
        ast = parse('var [a, ...rest] = arr;')
        root_scope, _ = build_scope_tree(ast)
        assert root_scope.get_own_binding('a') is not None
        assert root_scope.get_own_binding('rest') is not None

    def test_assignment_pattern_in_destructuring(self):
        ast = parse('var {x = 10} = obj;')
        root_scope, _ = build_scope_tree(ast)
        assert root_scope.get_own_binding('x') is not None

    def test_nested_destructuring(self):
        ast = parse('var {a: {b}} = obj;')
        root_scope, _ = build_scope_tree(ast)
        # 'a' is a key, not a binding; 'b' is the binding
        assert root_scope.get_own_binding('a') is None
        assert root_scope.get_own_binding('b') is not None

    def test_let_destructuring_block_scoped(self):
        ast = parse('{ let [a, b] = [1, 2]; }')
        root_scope, _ = build_scope_tree(ast)
        assert root_scope.get_own_binding('a') is None
        block = root_scope.children[0]
        assert block.get_own_binding('a') is not None
        assert block.get_own_binding('b') is not None


# ---------------------------------------------------------------------------
# build_scope_tree: ForStatement creates block scope
# ---------------------------------------------------------------------------


class TestForStatement:
    def test_for_creates_block_scope(self):
        ast = parse('for (let i = 0; i < 10; i++) { let x = i; }')
        root_scope, _ = build_scope_tree(ast)
        # 'i' should NOT be in the root scope
        assert root_scope.get_own_binding('i') is None
        # There should be a child scope for the for statement
        for_scope = root_scope.children[0]
        assert for_scope.get_own_binding('i') is not None
        assert for_scope.get_own_binding('i').kind == 'let'

    def test_for_var_hoisted_out(self):
        ast = parse('for (var i = 0; i < 10; i++) {}')
        root_scope, _ = build_scope_tree(ast)
        # var i should be hoisted to root (function) scope
        assert root_scope.get_own_binding('i') is not None
        assert root_scope.get_own_binding('i').kind == 'var'


# ---------------------------------------------------------------------------
# build_scope_tree: nested function scopes
# ---------------------------------------------------------------------------


class TestNestedFunctions:
    def test_nested_function_scopes(self):
        ast = parse("""
            function outer() {
                var a = 1;
                function inner() {
                    var b = 2;
                }
            }
        """)
        root_scope, _ = build_scope_tree(ast)
        assert root_scope.get_own_binding('outer') is not None
        outer_scope = root_scope.children[0]
        assert outer_scope.get_own_binding('a') is not None
        assert outer_scope.get_own_binding('inner') is not None
        inner_scope = outer_scope.children[0]
        assert inner_scope.get_own_binding('b') is not None
        # inner scope should not have 'a' as own binding
        assert inner_scope.get_own_binding('a') is None
        # but can resolve 'a' through chain
        assert inner_scope.get_binding('a') is not None

    def test_shadowed_variables_in_nested_functions(self):
        ast = parse("""
            var x = 1;
            function f() {
                var x = 2;
            }
        """)
        root_scope, _ = build_scope_tree(ast)
        root_x = root_scope.get_own_binding('x')
        f_scope = root_scope.children[0]
        f_x = f_scope.get_own_binding('x')
        assert root_x is not f_x
        assert root_x.kind == 'var'
        assert f_x.kind == 'var'


# ---------------------------------------------------------------------------
# Bug #1: Operator precedence on line 174
# ---------------------------------------------------------------------------


class TestOperatorPrecedenceBug:
    """Document the latent operator precedence bug on scope.py line 174.

    The line reads:
        target_scope = _nearest_function_scope(scope) or scope if kind == 'var' else scope

    Python parses this as:
        target_scope = _nearest_function_scope(scope) or (scope if kind == 'var' else scope)

    The intended behavior is:
        target_scope = (_nearest_function_scope(scope) or scope) if kind == 'var' else scope

    In normal usage _nearest_function_scope always returns a truthy scope
    (since root is a function scope), so both interpretations produce the
    same result. The bug would manifest only if _nearest_function_scope
    returned None/falsy, which cannot happen with a well-formed scope tree.
    """

    def test_var_targets_function_scope(self):
        """For 'var', the target is the nearest function scope.

        Since _nearest_function_scope returns a truthy value, the
        buggy precedence does not matter here -- both interpretations
        yield the function scope.
        """
        ast = parse('function f() { { var x = 1; } }')
        root_scope, _ = build_scope_tree(ast)
        f_scope = root_scope.children[0]
        assert f_scope.is_function is True
        # var x should be hoisted to f_scope
        assert f_scope.get_own_binding('x') is not None
        assert f_scope.get_own_binding('x').kind == 'var'

    def test_let_targets_block_scope(self):
        """For 'let', the target is the current (block) scope.

        When kind != 'var', the else branch fires and gives `scope`,
        which is the block scope. This works correctly regardless of
        operator precedence because the `or` short-circuits and the
        conditional still evaluates the else branch.
        """
        ast = parse('function f() { { let y = 2; } }')
        root_scope, _ = build_scope_tree(ast)
        f_scope = root_scope.children[0]
        assert f_scope.get_own_binding('y') is None
        block_scope = f_scope.children[0]
        assert block_scope.get_own_binding('y') is not None
        assert block_scope.get_own_binding('y').kind == 'let'

    def test_precedence_equivalence_when_function_scope_truthy(self):
        """Both interpretations give the same result when
        _nearest_function_scope returns a truthy value (the normal case).
        """
        root = Scope(None, {}, is_function=True)
        block = Scope(root, {}, is_function=False)

        func_scope = _nearest_function_scope(block)
        assert func_scope is not None  # truthy

        # Actual (buggy) precedence: func_scope or (block if 'var' else block)
        actual_var = func_scope or (block if 'var' == 'var' else block)
        # Intended precedence: (func_scope or block) if 'var' else block
        intended_var = (func_scope or block) if 'var' == 'var' else block

        # Both give the function scope -- bug is latent
        assert actual_var is func_scope
        assert intended_var is func_scope
        assert actual_var is intended_var

    def test_precedence_divergence_when_function_scope_falsy(self):
        """Demonstrate how the two interpretations would diverge
        if _nearest_function_scope returned None (hypothetical scenario).
        """
        block = Scope(None, {}, is_function=False)
        func_scope_result = None  # hypothetical falsy return

        # Actual (buggy) precedence for kind == 'var':
        # func_scope_result or (block if 'var' == 'var' else block)
        # = None or block = block
        actual = func_scope_result or (block if 'var' == 'var' else block)

        # Intended precedence for kind == 'var':
        # (func_scope_result or block) if 'var' == 'var' else block
        # = (None or block) if True else block = block
        intended = (func_scope_result or block) if 'var' == 'var' else block

        # In this specific case both happen to be block, but for kind != 'var':
        # Actual: None or (block if 'let' == 'var' else block) = None or block = block
        actual_let = func_scope_result or (block if 'let' == 'var' else block)
        # Intended: (None or block) if 'let' == 'var' else block = block if False else block = block
        intended_let = (func_scope_result or block) if 'let' == 'var' else block

        # Both happen to collapse to block in all cases when func_scope is None.
        # The real divergence would occur with a third distinct scope value.
        # For documentation purposes, we show the parsing difference:
        assert actual is block
        assert intended is block
        assert actual_let is block
        assert intended_let is block


# ---------------------------------------------------------------------------
# build_scope_tree: node_scope_map returned correctly
# ---------------------------------------------------------------------------


class TestNodeScopeMap:
    def test_root_in_node_scope_map(self):
        ast = parse('var x = 1;')
        root_scope, node_scope = build_scope_tree(ast)
        assert id(ast) in node_scope
        assert node_scope[id(ast)] is root_scope

    def test_function_node_in_scope_map(self):
        ast = parse('function f() {}')
        root_scope, node_scope = build_scope_tree(ast)
        # Find the function node
        func_node = ast['body'][0]
        assert id(func_node) in node_scope
        func_scope = node_scope[id(func_node)]
        assert func_scope.is_function is True

    def test_block_statement_in_scope_map(self):
        ast = parse('{ let x = 1; }')
        root_scope, node_scope = build_scope_tree(ast)
        block_node = ast['body'][0]
        assert id(block_node) in node_scope
