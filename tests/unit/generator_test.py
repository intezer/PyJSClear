"""Comprehensive unit tests for pyjsclear.generator.generate()."""

import pytest

from pyjsclear.generator import generate
from pyjsclear.parser import parse


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _lit(value, raw=None):
    """Shorthand for a Literal node."""
    node = {"type": "Literal", "value": value}
    if raw is not None:
        node["raw"] = raw
    return node


def _id(name):
    """Shorthand for an Identifier node."""
    return {"type": "Identifier", "name": name}


def _program(*stmts):
    return {"type": "Program", "sourceType": "script", "body": list(stmts)}


def _expr_stmt(expr):
    return {"type": "ExpressionStatement", "expression": expr}


def _block(*stmts):
    return {"type": "BlockStatement", "body": list(stmts)}


def _var(kind, name, init=None):
    decl = {"type": "VariableDeclarator", "id": _id(name)}
    if init is not None:
        decl["init"] = init
    return {"type": "VariableDeclaration", "declarations": [decl], "kind": kind}


# ===========================================================================
# 1. Literals
# ===========================================================================

class TestLiterals:
    def test_string_double_quoted(self):
        assert generate(_lit("hello", '"hello"')) == '"hello"'

    def test_string_single_quoted(self):
        assert generate(_lit("hello", "'hello'")) == "'hello'"

    def test_string_escaping_newline(self):
        assert generate(_lit("a\nb", '"a\\nb"')) == '"a\\nb"'

    def test_string_escaping_tab(self):
        assert generate(_lit("a\tb", '"a\\tb"')) == '"a\\tb"'

    def test_string_escaping_backslash(self):
        assert generate(_lit("a\\b", '"a\\\\b"')) == '"a\\\\b"'

    def test_string_escaping_quote_in_string(self):
        result = generate(_lit('say "hi"', None))
        # No raw hint, defaults to double quote, must escape inner double quotes
        assert result == '"say \\"hi\\""'

    def test_string_no_raw_defaults_double(self):
        assert generate(_lit("foo", None)) == '"foo"'

    def test_integer(self):
        assert generate(_lit(42, "42")) == "42"

    def test_integer_via_raw(self):
        assert generate(_lit(0xFF, "0xFF")) == "0xFF"

    def test_float(self):
        assert generate(_lit(3.14, "3.14")) == "3.14"

    def test_float_whole_number(self):
        # float that equals its int counterpart, no raw -> converts to int string
        assert generate(_lit(5.0)) == "5"

    def test_negative_float(self):
        assert generate(_lit(-1.5)) == "-1.5"

    def test_boolean_true(self):
        assert generate(_lit(True, "true")) == "true"

    def test_boolean_false(self):
        assert generate(_lit(False, "false")) == "false"

    def test_boolean_true_no_raw(self):
        assert generate(_lit(True)) == "true"

    def test_boolean_false_no_raw(self):
        assert generate(_lit(False)) == "false"

    def test_null(self):
        assert generate(_lit(None, "null")) == "null"

    def test_null_no_raw(self):
        assert generate(_lit(None)) == "null"

    def test_raw_value_used(self):
        # When value is not a string and raw is present, raw takes priority
        assert generate(_lit(10, "0xA")) == "0xA"


# ===========================================================================
# 2. Identifiers
# ===========================================================================

class TestIdentifiers:
    def test_simple_name(self):
        assert generate(_id("foo")) == "foo"

    def test_this(self):
        assert generate({"type": "ThisExpression"}) == "this"

    def test_empty_name(self):
        assert generate(_id("")) == ""


# ===========================================================================
# 3. Expressions
# ===========================================================================

class TestBinaryExpressions:
    def test_simple_add(self):
        node = {
            "type": "BinaryExpression",
            "operator": "+",
            "left": _lit(1, "1"),
            "right": _lit(2, "2"),
        }
        assert generate(node) == "1 + 2"

    def test_precedence_mul_over_add(self):
        # 1 + 2 * 3 -> no parens needed
        node = {
            "type": "BinaryExpression",
            "operator": "+",
            "left": _lit(1, "1"),
            "right": {
                "type": "BinaryExpression",
                "operator": "*",
                "left": _lit(2, "2"),
                "right": _lit(3, "3"),
            },
        }
        assert generate(node) == "1 + 2 * 3"

    def test_precedence_add_inside_mul_needs_parens(self):
        # (1 + 2) * 3
        node = {
            "type": "BinaryExpression",
            "operator": "*",
            "left": {
                "type": "BinaryExpression",
                "operator": "+",
                "left": _lit(1, "1"),
                "right": _lit(2, "2"),
            },
            "right": _lit(3, "3"),
        }
        assert generate(node) == "(1 + 2) * 3"

    def test_right_associativity_parens_for_minus(self):
        # 1 - (2 - 3) needs parens on right because - is left-assoc
        node = {
            "type": "BinaryExpression",
            "operator": "-",
            "left": _lit(1, "1"),
            "right": {
                "type": "BinaryExpression",
                "operator": "-",
                "left": _lit(2, "2"),
                "right": _lit(3, "3"),
            },
        }
        assert generate(node) == "1 - (2 - 3)"

    def test_commutative_no_parens_for_plus(self):
        # + is commutative, right child at same precedence does NOT get parens
        node = {
            "type": "BinaryExpression",
            "operator": "+",
            "left": _lit(1, "1"),
            "right": {
                "type": "BinaryExpression",
                "operator": "+",
                "left": _lit(2, "2"),
                "right": _lit(3, "3"),
            },
        }
        assert generate(node) == "1 + 2 + 3"

    def test_instanceof(self):
        node = {
            "type": "BinaryExpression",
            "operator": "instanceof",
            "left": _id("x"),
            "right": _id("Array"),
        }
        assert generate(node) == "x instanceof Array"

    def test_logical_and(self):
        node = {
            "type": "LogicalExpression",
            "operator": "&&",
            "left": _id("a"),
            "right": _id("b"),
        }
        assert generate(node) == "a && b"

    def test_logical_or(self):
        node = {
            "type": "LogicalExpression",
            "operator": "||",
            "left": _id("a"),
            "right": _id("b"),
        }
        assert generate(node) == "a || b"

    def test_nullish_coalescing(self):
        node = {
            "type": "LogicalExpression",
            "operator": "??",
            "left": _id("a"),
            "right": _id("b"),
        }
        assert generate(node) == "a ?? b"


class TestUnaryExpressions:
    def test_typeof(self):
        node = {
            "type": "UnaryExpression",
            "operator": "typeof",
            "prefix": True,
            "argument": _id("x"),
        }
        assert generate(node) == "typeof x"

    def test_void(self):
        node = {
            "type": "UnaryExpression",
            "operator": "void",
            "prefix": True,
            "argument": _lit(0, "0"),
        }
        assert generate(node) == "void 0"

    def test_delete(self):
        node = {
            "type": "UnaryExpression",
            "operator": "delete",
            "prefix": True,
            "argument": {
                "type": "MemberExpression",
                "object": _id("obj"),
                "property": _id("key"),
                "computed": False,
            },
        }
        assert generate(node) == "delete obj.key"

    def test_not(self):
        node = {
            "type": "UnaryExpression",
            "operator": "!",
            "prefix": True,
            "argument": _id("x"),
        }
        assert generate(node) == "!x"

    def test_negate(self):
        node = {
            "type": "UnaryExpression",
            "operator": "-",
            "prefix": True,
            "argument": _id("x"),
        }
        assert generate(node) == "-x"

    def test_bitwise_not(self):
        node = {
            "type": "UnaryExpression",
            "operator": "~",
            "prefix": True,
            "argument": _id("x"),
        }
        assert generate(node) == "~x"

    def test_unary_wraps_lower_precedence(self):
        # typeof (a + b) -- binary has lower prec than unary
        node = {
            "type": "UnaryExpression",
            "operator": "typeof",
            "prefix": True,
            "argument": {
                "type": "BinaryExpression",
                "operator": "+",
                "left": _id("a"),
                "right": _id("b"),
            },
        }
        assert generate(node) == "typeof (a + b)"


class TestUpdateExpressions:
    def test_postfix_increment(self):
        node = {
            "type": "UpdateExpression",
            "operator": "++",
            "prefix": False,
            "argument": _id("x"),
        }
        assert generate(node) == "x++"

    def test_prefix_increment(self):
        node = {
            "type": "UpdateExpression",
            "operator": "++",
            "prefix": True,
            "argument": _id("x"),
        }
        assert generate(node) == "++x"

    def test_postfix_decrement(self):
        node = {
            "type": "UpdateExpression",
            "operator": "--",
            "prefix": False,
            "argument": _id("x"),
        }
        assert generate(node) == "x--"

    def test_prefix_decrement(self):
        node = {
            "type": "UpdateExpression",
            "operator": "--",
            "prefix": True,
            "argument": _id("x"),
        }
        assert generate(node) == "--x"


class TestMemberExpressions:
    def test_dot_access(self):
        node = {
            "type": "MemberExpression",
            "object": _id("obj"),
            "property": _id("prop"),
            "computed": False,
        }
        assert generate(node) == "obj.prop"

    def test_computed_access(self):
        node = {
            "type": "MemberExpression",
            "object": _id("arr"),
            "property": _lit(0, "0"),
            "computed": True,
        }
        assert generate(node) == "arr[0]"

    def test_numeric_literal_dot_access_gets_parens(self):
        node = {
            "type": "MemberExpression",
            "object": _lit(1, "1"),
            "property": _id("toString"),
            "computed": False,
        }
        assert generate(node) == "(1).toString"

    def test_numeric_literal_computed_no_parens(self):
        node = {
            "type": "MemberExpression",
            "object": _lit(1, "1"),
            "property": _lit(0, "0"),
            "computed": True,
        }
        # Computed access on a literal doesn't need parens
        assert generate(node) == "1[0]"


class TestCallExpressions:
    def test_simple_call(self):
        node = {
            "type": "CallExpression",
            "callee": _id("foo"),
            "arguments": [],
        }
        assert generate(node) == "foo()"

    def test_call_with_args(self):
        node = {
            "type": "CallExpression",
            "callee": _id("foo"),
            "arguments": [_lit(1, "1"), _id("x")],
        }
        assert generate(node) == "foo(1, x)"

    def test_iife_wraps_function_expression(self):
        node = {
            "type": "CallExpression",
            "callee": {
                "type": "FunctionExpression",
                "id": None,
                "params": [],
                "body": _block(),
                "async": False,
                "generator": False,
            },
            "arguments": [],
        }
        assert generate(node) == "(function () {})()"

    def test_call_wraps_arrow(self):
        node = {
            "type": "CallExpression",
            "callee": {
                "type": "ArrowFunctionExpression",
                "params": [],
                "body": _block(),
                "async": False,
            },
            "arguments": [],
        }
        assert generate(node) == "(() => {})()"


class TestNewExpression:
    def test_new_no_args(self):
        node = {
            "type": "NewExpression",
            "callee": _id("Foo"),
            "arguments": [],
        }
        assert generate(node) == "new Foo()"

    def test_new_with_args(self):
        node = {
            "type": "NewExpression",
            "callee": _id("Foo"),
            "arguments": [_lit(1, "1"), _lit(2, "2")],
        }
        assert generate(node) == "new Foo(1, 2)"


class TestConditionalExpression:
    def test_ternary(self):
        node = {
            "type": "ConditionalExpression",
            "test": _id("a"),
            "consequent": _id("b"),
            "alternate": _id("c"),
        }
        assert generate(node) == "a ? b : c"

    def test_ternary_wraps_sequence_in_branches(self):
        seq = {
            "type": "SequenceExpression",
            "expressions": [_id("x"), _id("y")],
        }
        node = {
            "type": "ConditionalExpression",
            "test": _id("a"),
            "consequent": seq,
            "alternate": _id("c"),
        }
        result = generate(node)
        assert "(x, y)" in result


class TestSequenceExpression:
    def test_sequence(self):
        node = {
            "type": "SequenceExpression",
            "expressions": [_id("a"), _id("b"), _id("c")],
        }
        assert generate(node) == "a, b, c"


class TestAssignmentExpression:
    def test_simple_assignment(self):
        node = {
            "type": "AssignmentExpression",
            "operator": "=",
            "left": _id("x"),
            "right": _lit(5, "5"),
        }
        assert generate(node) == "x = 5"

    def test_compound_assignment(self):
        node = {
            "type": "AssignmentExpression",
            "operator": "+=",
            "left": _id("x"),
            "right": _lit(1, "1"),
        }
        assert generate(node) == "x += 1"


# ===========================================================================
# 4. Statements
# ===========================================================================

class TestVariableDeclarations:
    def test_var(self):
        node = _var("var", "x", _lit(1, "1"))
        assert generate(node) == "var x = 1"

    def test_let(self):
        node = _var("let", "x", _lit(1, "1"))
        assert generate(node) == "let x = 1"

    def test_const(self):
        node = _var("const", "x", _lit(1, "1"))
        assert generate(node) == "const x = 1"

    def test_uninitialized(self):
        node = _var("var", "x")
        assert generate(node) == "var x"

    def test_multiple_declarators(self):
        node = {
            "type": "VariableDeclaration",
            "kind": "var",
            "declarations": [
                {"type": "VariableDeclarator", "id": _id("a"), "init": _lit(1, "1")},
                {"type": "VariableDeclarator", "id": _id("b"), "init": _lit(2, "2")},
            ],
        }
        assert generate(node) == "var a = 1, b = 2"


class TestIfStatement:
    def test_if_block(self):
        node = {
            "type": "IfStatement",
            "test": _id("x"),
            "consequent": _block(_expr_stmt(_id("a"))),
            "alternate": None,
        }
        result = generate(node)
        assert result.startswith("if (x) {")
        assert "a;" in result

    def test_if_else(self):
        node = {
            "type": "IfStatement",
            "test": _id("x"),
            "consequent": _block(_expr_stmt(_id("a"))),
            "alternate": _block(_expr_stmt(_id("b"))),
        }
        result = generate(node)
        assert "if (x)" in result
        assert "else" in result

    def test_if_else_if_chain(self):
        inner_if = {
            "type": "IfStatement",
            "test": _id("y"),
            "consequent": _block(_expr_stmt(_id("b"))),
            "alternate": None,
        }
        node = {
            "type": "IfStatement",
            "test": _id("x"),
            "consequent": _block(_expr_stmt(_id("a"))),
            "alternate": inner_if,
        }
        result = generate(node)
        assert "else if (y)" in result


class TestWhileStatement:
    def test_while(self):
        node = {
            "type": "WhileStatement",
            "test": _id("x"),
            "body": _block(),
        }
        assert generate(node) == "while (x) {}"


class TestDoWhileStatement:
    def test_do_while(self):
        node = {
            "type": "DoWhileStatement",
            "test": _id("x"),
            "body": _block(),
        }
        assert generate(node) == "do {} while (x)"


class TestForStatement:
    def test_for_full(self):
        node = {
            "type": "ForStatement",
            "init": _var("var", "i", _lit(0, "0")),
            "test": {
                "type": "BinaryExpression",
                "operator": "<",
                "left": _id("i"),
                "right": _lit(10, "10"),
            },
            "update": {
                "type": "UpdateExpression",
                "operator": "++",
                "prefix": False,
                "argument": _id("i"),
            },
            "body": _block(),
        }
        result = generate(node)
        assert result.startswith("for (var i = 0; i < 10; i++)")

    def test_for_empty_parts(self):
        node = {
            "type": "ForStatement",
            "init": None,
            "test": None,
            "update": None,
            "body": _block(),
        }
        assert generate(node) == "for (; ; ) {}"


class TestForInStatement:
    def test_for_in(self):
        node = {
            "type": "ForInStatement",
            "left": _var("var", "k"),
            "right": _id("obj"),
            "body": _block(),
        }
        result = generate(node)
        assert "for (var k in obj)" in result


class TestForOfStatement:
    def test_for_of(self):
        node = {
            "type": "ForOfStatement",
            "left": _var("const", "item"),
            "right": _id("arr"),
            "body": _block(),
        }
        result = generate(node)
        assert "for (const item of arr)" in result


class TestSwitchStatement:
    def test_switch_case_default(self):
        node = {
            "type": "SwitchStatement",
            "discriminant": _id("x"),
            "cases": [
                {
                    "type": "SwitchCase",
                    "test": _lit(1, "1"),
                    "consequent": [
                        _expr_stmt(_id("a")),
                        {"type": "BreakStatement", "label": None},
                    ],
                },
                {
                    "type": "SwitchCase",
                    "test": None,
                    "consequent": [_expr_stmt(_id("b"))],
                },
            ],
        }
        result = generate(node)
        assert "switch (x)" in result
        assert "case 1:" in result
        assert "default:" in result
        assert "break;" in result


class TestTryCatchFinally:
    def test_try_catch(self):
        node = {
            "type": "TryStatement",
            "block": _block(_expr_stmt(_id("a"))),
            "handler": {
                "type": "CatchClause",
                "param": _id("e"),
                "body": _block(_expr_stmt(_id("b"))),
            },
            "finalizer": None,
        }
        result = generate(node)
        assert "try {" in result
        assert "catch (e)" in result

    def test_try_finally(self):
        node = {
            "type": "TryStatement",
            "block": _block(_expr_stmt(_id("a"))),
            "handler": None,
            "finalizer": _block(_expr_stmt(_id("c"))),
        }
        result = generate(node)
        assert "try {" in result
        assert "finally {" in result

    def test_try_catch_finally(self):
        node = {
            "type": "TryStatement",
            "block": _block(_expr_stmt(_id("a"))),
            "handler": {
                "type": "CatchClause",
                "param": _id("e"),
                "body": _block(_expr_stmt(_id("b"))),
            },
            "finalizer": _block(_expr_stmt(_id("c"))),
        }
        result = generate(node)
        assert "catch (e)" in result
        assert "finally {" in result

    def test_catch_without_param(self):
        node = {
            "type": "TryStatement",
            "block": _block(),
            "handler": {
                "type": "CatchClause",
                "param": None,
                "body": _block(),
            },
            "finalizer": None,
        }
        result = generate(node)
        assert "catch {}" in result


class TestThrowStatement:
    def test_throw(self):
        node = {
            "type": "ThrowStatement",
            "argument": {
                "type": "NewExpression",
                "callee": _id("Error"),
                "arguments": [_lit("oops", "'oops'")],
            },
        }
        result = generate(node)
        assert result == "throw new Error('oops')"


class TestBreakContinue:
    def test_break(self):
        assert generate({"type": "BreakStatement", "label": None}) == "break"

    def test_break_with_label(self):
        node = {"type": "BreakStatement", "label": _id("outer")}
        assert generate(node) == "break outer"

    def test_continue(self):
        assert generate({"type": "ContinueStatement", "label": None}) == "continue"

    def test_continue_with_label(self):
        node = {"type": "ContinueStatement", "label": _id("outer")}
        assert generate(node) == "continue outer"


class TestLabeledStatement:
    def test_labeled(self):
        node = {
            "type": "LabeledStatement",
            "label": _id("outer"),
            "body": {
                "type": "WhileStatement",
                "test": _lit(True, "true"),
                "body": _block(),
            },
        }
        result = generate(node)
        assert result.startswith("outer:\n")
        assert "while (true)" in result


class TestReturnStatement:
    def test_return_value(self):
        node = {"type": "ReturnStatement", "argument": _lit(42, "42")}
        assert generate(node) == "return 42"

    def test_return_void(self):
        node = {"type": "ReturnStatement", "argument": None}
        assert generate(node) == "return"


class TestEmptyStatement:
    def test_empty(self):
        assert generate({"type": "EmptyStatement"}) == ";"


# ===========================================================================
# 5. Functions
# ===========================================================================

class TestFunctions:
    def test_function_declaration(self):
        node = {
            "type": "FunctionDeclaration",
            "id": _id("foo"),
            "params": [_id("a"), _id("b")],
            "body": _block({"type": "ReturnStatement", "argument": _id("a")}),
            "async": False,
            "generator": False,
        }
        result = generate(node)
        assert result.startswith("function foo(a, b) {")
        assert "return a;" in result

    def test_function_expression_named(self):
        node = {
            "type": "FunctionExpression",
            "id": _id("bar"),
            "params": [],
            "body": _block(),
            "async": False,
            "generator": False,
        }
        assert generate(node) == "function bar() {}"

    def test_function_expression_anonymous(self):
        node = {
            "type": "FunctionExpression",
            "id": None,
            "params": [],
            "body": _block(),
            "async": False,
            "generator": False,
        }
        assert generate(node) == "function () {}"

    def test_arrow_block_body(self):
        node = {
            "type": "ArrowFunctionExpression",
            "params": [_id("x")],
            "body": _block({"type": "ReturnStatement", "argument": _id("x")}),
            "async": False,
        }
        result = generate(node)
        assert result.startswith("(x) => {")

    def test_arrow_expression_body(self):
        node = {
            "type": "ArrowFunctionExpression",
            "params": [_id("x")],
            "body": _id("x"),
            "async": False,
        }
        assert generate(node) == "(x) => x"

    def test_arrow_object_body_wrapping(self):
        node = {
            "type": "ArrowFunctionExpression",
            "params": [],
            "body": {"type": "ObjectExpression", "properties": []},
            "async": False,
        }
        assert generate(node) == "() => ({})"

    def test_async_function(self):
        node = {
            "type": "FunctionDeclaration",
            "id": _id("foo"),
            "params": [],
            "body": _block(),
            "async": True,
            "generator": False,
        }
        assert generate(node).startswith("async function foo()")

    def test_generator_function(self):
        node = {
            "type": "FunctionDeclaration",
            "id": _id("gen"),
            "params": [],
            "body": _block(),
            "async": False,
            "generator": True,
        }
        assert generate(node).startswith("function* gen()")

    def test_async_arrow(self):
        node = {
            "type": "ArrowFunctionExpression",
            "params": [_id("x")],
            "body": _id("x"),
            "async": True,
        }
        assert generate(node) == "async (x) => x"


# ===========================================================================
# 6. Classes
# ===========================================================================

class TestClasses:
    def test_class_declaration(self):
        node = {
            "type": "ClassDeclaration",
            "id": _id("Foo"),
            "superClass": None,
            "body": {"type": "ClassBody", "body": []},
        }
        assert generate(node) == "class Foo {}"

    def test_class_with_extends(self):
        node = {
            "type": "ClassDeclaration",
            "id": _id("Foo"),
            "superClass": _id("Bar"),
            "body": {"type": "ClassBody", "body": []},
        }
        assert generate(node) == "class Foo extends Bar {}"

    def test_class_expression_anonymous(self):
        node = {
            "type": "ClassExpression",
            "id": None,
            "superClass": None,
            "body": {"type": "ClassBody", "body": []},
        }
        assert generate(node) == "class {}"

    def test_constructor(self):
        method = {
            "type": "MethodDefinition",
            "key": _id("constructor"),
            "kind": "constructor",
            "static": False,
            "computed": False,
            "value": {
                "type": "FunctionExpression",
                "params": [_id("x")],
                "body": _block(),
            },
        }
        node = {
            "type": "ClassDeclaration",
            "id": _id("Foo"),
            "superClass": None,
            "body": {"type": "ClassBody", "body": [method]},
        }
        result = generate(node)
        assert "constructor(x) {}" in result

    def test_method(self):
        method = {
            "type": "MethodDefinition",
            "key": _id("bar"),
            "kind": "method",
            "static": False,
            "computed": False,
            "value": {
                "type": "FunctionExpression",
                "params": [],
                "body": _block(),
            },
        }
        result = generate(method)
        assert result == "bar() {}"

    def test_getter(self):
        method = {
            "type": "MethodDefinition",
            "key": _id("val"),
            "kind": "get",
            "static": False,
            "computed": False,
            "value": {
                "type": "FunctionExpression",
                "params": [],
                "body": _block(),
            },
        }
        result = generate(method)
        assert result == "get val() {}"

    def test_setter(self):
        method = {
            "type": "MethodDefinition",
            "key": _id("val"),
            "kind": "set",
            "static": False,
            "computed": False,
            "value": {
                "type": "FunctionExpression",
                "params": [_id("v")],
                "body": _block(),
            },
        }
        result = generate(method)
        assert result == "set val(v) {}"

    def test_static_method(self):
        method = {
            "type": "MethodDefinition",
            "key": _id("create"),
            "kind": "method",
            "static": True,
            "computed": False,
            "value": {
                "type": "FunctionExpression",
                "params": [],
                "body": _block(),
            },
        }
        result = generate(method)
        assert result == "static create() {}"


# ===========================================================================
# 7. Patterns
# ===========================================================================

class TestPatterns:
    def test_array_pattern(self):
        node = {
            "type": "ArrayPattern",
            "elements": [_id("a"), _id("b")],
        }
        assert generate(node) == "[a, b]"

    def test_array_pattern_with_hole(self):
        node = {
            "type": "ArrayPattern",
            "elements": [_id("a"), None, _id("b")],
        }
        assert generate(node) == "[a, , b]"

    def test_object_pattern(self):
        node = {
            "type": "ObjectPattern",
            "properties": [
                {
                    "type": "Property",
                    "key": _id("x"),
                    "value": _id("x"),
                    "shorthand": True,
                },
            ],
        }
        result = generate(node)
        assert "x" in result

    def test_object_pattern_renamed(self):
        node = {
            "type": "ObjectPattern",
            "properties": [
                {
                    "type": "Property",
                    "key": _id("x"),
                    "value": _id("y"),
                    "shorthand": False,
                },
            ],
        }
        result = generate(node)
        assert "x: y" in result

    def test_rest_element(self):
        node = {
            "type": "RestElement",
            "argument": _id("rest"),
        }
        assert generate(node) == "...rest"

    def test_assignment_pattern(self):
        node = {
            "type": "AssignmentPattern",
            "left": _id("x"),
            "right": _lit(10, "10"),
        }
        assert generate(node) == "x = 10"

    def test_spread_element(self):
        node = {
            "type": "SpreadElement",
            "argument": _id("arr"),
        }
        assert generate(node) == "...arr"


# ===========================================================================
# 8. Templates
# ===========================================================================

class TestTemplateLiterals:
    def test_simple_template(self):
        node = {
            "type": "TemplateLiteral",
            "quasis": [
                {"type": "TemplateElement", "value": {"raw": "hello "}, "tail": False},
                {"type": "TemplateElement", "value": {"raw": "!"}, "tail": True},
            ],
            "expressions": [_id("name")],
        }
        assert generate(node) == "`hello ${name}!`"

    def test_template_no_expressions(self):
        node = {
            "type": "TemplateLiteral",
            "quasis": [
                {"type": "TemplateElement", "value": {"raw": "plain"}, "tail": True},
            ],
            "expressions": [],
        }
        assert generate(node) == "`plain`"

    def test_tagged_template(self):
        node = {
            "type": "TaggedTemplateExpression",
            "tag": _id("html"),
            "quasi": {
                "type": "TemplateLiteral",
                "quasis": [
                    {"type": "TemplateElement", "value": {"raw": "<p>"}, "tail": False},
                    {"type": "TemplateElement", "value": {"raw": "</p>"}, "tail": True},
                ],
                "expressions": [_id("text")],
            },
        }
        assert generate(node) == "html`<p>${text}</p>`"


# ===========================================================================
# 9. Other
# ===========================================================================

class TestYieldAwait:
    def test_yield(self):
        node = {
            "type": "YieldExpression",
            "argument": _lit(1, "1"),
            "delegate": False,
        }
        assert generate(node) == "yield 1"

    def test_yield_no_argument(self):
        node = {
            "type": "YieldExpression",
            "argument": None,
            "delegate": False,
        }
        assert generate(node) == "yield"

    def test_yield_delegate(self):
        node = {
            "type": "YieldExpression",
            "argument": _id("iter"),
            "delegate": True,
        }
        assert generate(node) == "yield* iter"

    def test_await(self):
        node = {
            "type": "AwaitExpression",
            "argument": _id("promise"),
        }
        assert generate(node) == "await promise"


class TestUnknownNodeType:
    def test_unknown_produces_comment(self):
        node = {"type": "SomeNewNode"}
        assert generate(node) == "/* unknown: SomeNewNode */"

    def test_empty_type(self):
        node = {"type": ""}
        assert generate(node) == "/* unknown:  */"

    def test_none_returns_empty(self):
        assert generate(None) == ""

    def test_non_dict_returns_str(self):
        assert generate(42) == "42"
        assert generate("hello") == "hello"


class TestArrayExpression:
    def test_empty_array(self):
        node = {"type": "ArrayExpression", "elements": []}
        assert generate(node) == "[]"

    def test_array_with_elements(self):
        node = {"type": "ArrayExpression", "elements": [_lit(1, "1"), _lit(2, "2")]}
        assert generate(node) == "[1, 2]"

    def test_array_with_hole(self):
        node = {"type": "ArrayExpression", "elements": [_lit(1, "1"), None, _lit(3, "3")]}
        assert generate(node) == "[1, , 3]"


class TestObjectExpression:
    def test_empty_object(self):
        node = {"type": "ObjectExpression", "properties": []}
        assert generate(node) == "{}"

    def test_object_with_shorthand(self):
        node = {
            "type": "ObjectExpression",
            "properties": [
                {
                    "type": "Property",
                    "key": _id("x"),
                    "value": _id("x"),
                    "kind": "init",
                    "shorthand": True,
                    "computed": False,
                    "method": False,
                },
            ],
        }
        result = generate(node)
        # shorthand property should just be the name
        assert "x" in result

    def test_object_method(self):
        node = {
            "type": "ObjectExpression",
            "properties": [
                {
                    "type": "Property",
                    "key": _id("foo"),
                    "value": {
                        "type": "FunctionExpression",
                        "params": [],
                        "body": _block(),
                    },
                    "kind": "init",
                    "shorthand": False,
                    "computed": False,
                    "method": True,
                },
            ],
        }
        result = generate(node)
        assert "foo() {}" in result

    def test_object_getter(self):
        node = {
            "type": "ObjectExpression",
            "properties": [
                {
                    "type": "Property",
                    "key": _id("val"),
                    "value": {
                        "type": "FunctionExpression",
                        "params": [],
                        "body": _block(),
                    },
                    "kind": "get",
                    "shorthand": False,
                    "computed": False,
                    "method": False,
                },
            ],
        }
        result = generate(node)
        assert "get val() {}" in result

    def test_object_setter(self):
        node = {
            "type": "ObjectExpression",
            "properties": [
                {
                    "type": "Property",
                    "key": _id("val"),
                    "value": {
                        "type": "FunctionExpression",
                        "params": [_id("v")],
                        "body": _block(),
                    },
                    "kind": "set",
                    "shorthand": False,
                    "computed": False,
                    "method": False,
                },
            ],
        }
        result = generate(node)
        assert "set val(v) {}" in result

    def test_object_computed_key(self):
        node = {
            "type": "ObjectExpression",
            "properties": [
                {
                    "type": "Property",
                    "key": _id("sym"),
                    "value": _lit(1, "1"),
                    "kind": "init",
                    "shorthand": False,
                    "computed": True,
                    "method": False,
                },
            ],
        }
        result = generate(node)
        assert "[sym]: 1" in result

    def test_object_spread(self):
        node = {
            "type": "ObjectExpression",
            "properties": [
                {
                    "type": "SpreadElement",
                    "argument": _id("other"),
                },
            ],
        }
        result = generate(node)
        assert "...other" in result


# ===========================================================================
# 10. Bug #4: Identifier keys in object properties are single-quoted
# ===========================================================================

class TestBug4IdentifierKeyQuoting:
    """Document current behavior: non-computed Identifier keys in object
    properties are always single-quoted (e.g. 'foo': 1 instead of foo: 1).
    This is a known quirk (Bug #4)."""

    def test_identifier_key_is_single_quoted(self):
        node = {
            "type": "ObjectExpression",
            "properties": [
                {
                    "type": "Property",
                    "key": {"type": "Identifier", "name": "foo"},
                    "value": {"type": "Literal", "value": 1, "raw": "1"},
                    "kind": "init",
                    "shorthand": False,
                    "computed": False,
                    "method": False,
                },
            ],
        }
        result = generate(node)
        assert "foo: 1" in result
        # Bug #4 fixed: identifier keys are no longer single-quoted
        assert "'foo'" not in result

    def test_multiple_identifier_keys_not_quoted(self):
        node = {
            "type": "ObjectExpression",
            "properties": [
                {
                    "type": "Property",
                    "key": {"type": "Identifier", "name": "a"},
                    "value": {"type": "Literal", "value": 1, "raw": "1"},
                    "kind": "init",
                    "shorthand": False,
                    "computed": False,
                    "method": False,
                },
                {
                    "type": "Property",
                    "key": {"type": "Identifier", "name": "b"},
                    "value": {"type": "Literal", "value": 2, "raw": "2"},
                    "kind": "init",
                    "shorthand": False,
                    "computed": False,
                    "method": False,
                },
            ],
        }
        result = generate(node)
        assert "a: 1" in result
        assert "b: 2" in result
        assert "'a'" not in result
        assert "'b'" not in result

    def test_string_literal_key_keeps_its_quotes(self):
        node = {
            "type": "ObjectExpression",
            "properties": [
                {
                    "type": "Property",
                    "key": {"type": "Literal", "value": "key", "raw": "'key'"},
                    "value": {"type": "Literal", "value": 1, "raw": "1"},
                    "kind": "init",
                    "shorthand": False,
                    "computed": False,
                    "method": False,
                },
            ],
        }
        result = generate(node)
        assert "'key': 1" in result

    def test_computed_identifier_key_not_quoted(self):
        """Computed keys use brackets, no quoting applied."""
        node = {
            "type": "ObjectExpression",
            "properties": [
                {
                    "type": "Property",
                    "key": {"type": "Identifier", "name": "foo"},
                    "value": {"type": "Literal", "value": 1, "raw": "1"},
                    "kind": "init",
                    "shorthand": False,
                    "computed": True,
                    "method": False,
                },
            ],
        }
        result = generate(node)
        assert "[foo]: 1" in result
        assert "'foo'" not in result


# ===========================================================================
# 11. Roundtrip tests (parse then generate)
# ===========================================================================

class TestRoundtrip:
    """Parse JavaScript with parse(), then generate back, and verify output."""

    def _roundtrip(self, code):
        ast = parse(code)
        return generate(ast)

    def test_var_declaration(self):
        result = self._roundtrip("var x = 1;")
        assert "var x = 1;" in result

    def test_let_const(self):
        result = self._roundtrip("let a = 1; const b = 2;")
        assert "let a = 1;" in result
        assert "const b = 2;" in result

    def test_function_declaration(self):
        result = self._roundtrip("function foo(a) { return a; }")
        assert "function foo(a)" in result
        assert "return a;" in result

    def test_if_else(self):
        result = self._roundtrip("if (x) { a(); } else { b(); }")
        assert "if (x)" in result
        assert "else" in result

    def test_for_loop(self):
        result = self._roundtrip("for (var i = 0; i < 10; i++) {}")
        assert "for (" in result
        assert "i < 10" in result

    def test_while_loop(self):
        result = self._roundtrip("while (true) { break; }")
        assert "while (true)" in result
        assert "break;" in result

    def test_arrow_function(self):
        result = self._roundtrip("var f = (x) => x + 1;")
        assert "=>" in result

    def test_class(self):
        result = self._roundtrip("class Foo extends Bar { constructor() {} }")
        assert "class Foo extends Bar" in result
        assert "constructor()" in result

    def test_template_literal(self):
        result = self._roundtrip("var s = `hello ${name}`;")
        assert "`hello ${name}`" in result

    def test_try_catch(self):
        result = self._roundtrip("try { a(); } catch (e) { b(); }")
        assert "try {" in result
        assert "catch (e)" in result

    def test_switch(self):
        result = self._roundtrip("switch (x) { case 1: break; default: break; }")
        assert "switch (x)" in result
        assert "case 1:" in result
        assert "default:" in result

    def test_do_while(self):
        result = self._roundtrip("do { x++; } while (x < 10);")
        assert "do {" in result
        assert "while (x < 10)" in result

    def test_spread_in_call(self):
        result = self._roundtrip("foo(...args);")
        assert "...args" in result

    def test_object_destructuring(self):
        result = self._roundtrip("var { a, b } = obj;")
        assert "a" in result
        assert "b" in result

    def test_array_destructuring(self):
        result = self._roundtrip("var [a, b] = arr;")
        assert "a" in result
        assert "b" in result


# ===========================================================================
# Program-level tests
# ===========================================================================

class TestProgram:
    def test_program_joins_statements(self):
        prog = _program(
            _expr_stmt(_id("a")),
            _expr_stmt(_id("b")),
        )
        result = generate(prog)
        assert "a;" in result
        assert "b;" in result

    def test_program_skips_none_and_empty(self):
        prog = _program(
            None,
            {"type": "EmptyStatement"},
            _expr_stmt(_id("a")),
        )
        result = generate(prog)
        assert result.strip() == "a;"

    def test_directive_followed_by_blank_line(self):
        prog = _program(
            _expr_stmt(_lit("use strict", "'use strict'")),
            _expr_stmt(_id("a")),
        )
        result = generate(prog)
        lines = result.split("\n")
        # There should be a blank line after the directive
        assert "" in lines


class TestBlockStatement:
    def test_empty_block(self):
        assert generate(_block()) == "{}"

    def test_block_with_statements(self):
        result = generate(_block(_expr_stmt(_id("a"))))
        assert result.startswith("{")
        assert "a;" in result
        assert result.rstrip().endswith("}")
