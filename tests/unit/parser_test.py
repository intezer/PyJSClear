"""Comprehensive unit tests for pyjsclear.parser."""

import re
import pytest

from pyjsclear.parser import parse, _fast_to_dict, _ASYNC_MAP


# ---------------------------------------------------------------------------
# _fast_to_dict – primitive pass-through
# ---------------------------------------------------------------------------

class TestFastToDictPrimitives:
    def test_string(self):
        assert _fast_to_dict("hello") == "hello"

    def test_int(self):
        assert _fast_to_dict(42) == 42

    def test_float(self):
        assert _fast_to_dict(3.14) == 3.14

    def test_bool_true(self):
        assert _fast_to_dict(True) is True

    def test_bool_false(self):
        assert _fast_to_dict(False) is False

    def test_none(self):
        assert _fast_to_dict(None) is None


# ---------------------------------------------------------------------------
# _fast_to_dict – list handling
# ---------------------------------------------------------------------------

class TestFastToDictLists:
    def test_empty_list(self):
        assert _fast_to_dict([]) == []

    def test_list_of_primitives(self):
        assert _fast_to_dict([1, "two", None]) == [1, "two", None]

    def test_nested_list(self):
        assert _fast_to_dict([[1, 2], [3]]) == [[1, 2], [3]]

    def test_list_of_dicts(self):
        result = _fast_to_dict([{"a": 1}, {"b": 2}])
        assert result == [{"a": 1}, {"b": 2}]


# ---------------------------------------------------------------------------
# _fast_to_dict – re.Pattern handling
# ---------------------------------------------------------------------------

class TestFastToDictRegex:
    def test_regex_pattern_returns_empty_dict(self):
        pattern = re.compile(r"\d+")
        assert _fast_to_dict(pattern) == {}


# ---------------------------------------------------------------------------
# _fast_to_dict – dict / object handling
# ---------------------------------------------------------------------------

class TestFastToDictDicts:
    def test_plain_dict(self):
        assert _fast_to_dict({"x": 1, "y": "z"}) == {"x": 1, "y": "z"}

    def test_nested_dict(self):
        result = _fast_to_dict({"a": {"b": {"c": 3}}})
        assert result == {"a": {"b": {"c": 3}}}

    def test_skips_underscore_keys(self):
        result = _fast_to_dict({"_private": 1, "public": 2})
        assert result == {"public": 2}

    def test_skips_multiple_underscore_keys(self):
        result = _fast_to_dict({"__dunder": 0, "_x": 1, "ok": 2})
        assert result == {"ok": 2}

    def test_skips_optional_false(self):
        result = _fast_to_dict({"optional": False, "name": "test"})
        assert result == {"name": "test"}

    def test_keeps_optional_true(self):
        result = _fast_to_dict({"optional": True, "name": "test"})
        assert result == {"optional": True, "name": "test"}

    def test_keeps_optional_none(self):
        result = _fast_to_dict({"optional": None, "name": "test"})
        assert result == {"optional": None, "name": "test"}

    def test_async_map_isAsync(self):
        result = _fast_to_dict({"isAsync": True})
        assert "async" in result
        assert "isAsync" not in result
        assert result["async"] is True

    def test_async_map_allowAwait(self):
        result = _fast_to_dict({"allowAwait": True})
        assert "await" in result
        assert "allowAwait" not in result
        assert result["await"] is True

    def test_async_map_values_preserved(self):
        result = _fast_to_dict({"isAsync": False, "allowAwait": False})
        assert result == {"async": False, "await": False}


class TestFastToDictObjects:
    """Test with objects that have __dict__ (simulating esprima nodes)."""

    def test_object_with_dict(self):
        class FakeNode:
            def __init__(self):
                self.type = "Identifier"
                self.name = "x"

        result = _fast_to_dict(FakeNode())
        assert result == {"type": "Identifier", "name": "x"}

    def test_object_skips_underscore_attrs(self):
        class FakeNode:
            def __init__(self):
                self._internal = "hidden"
                self.type = "Literal"

        result = _fast_to_dict(FakeNode())
        assert result == {"type": "Literal"}

    def test_object_optional_false_skipped(self):
        class FakeNode:
            def __init__(self):
                self.type = "MemberExpression"
                self.optional = False

        result = _fast_to_dict(FakeNode())
        assert result == {"type": "MemberExpression"}

    def test_object_with_nested_list(self):
        class FakeNode:
            def __init__(self):
                self.type = "Program"
                self.body = [{"type": "EmptyStatement"}]

        result = _fast_to_dict(FakeNode())
        assert result == {"type": "Program", "body": [{"type": "EmptyStatement"}]}


# ---------------------------------------------------------------------------
# _ASYNC_MAP constant
# ---------------------------------------------------------------------------

class TestAsyncMap:
    def test_async_map_contents(self):
        assert _ASYNC_MAP == {'isAsync': 'async', 'allowAwait': 'await'}


# ---------------------------------------------------------------------------
# parse() – empty input
# ---------------------------------------------------------------------------

class TestParseEmpty:
    def test_empty_string(self):
        result = parse("")
        assert result["type"] == "Program"
        assert result["body"] == []

    def test_whitespace_only(self):
        result = parse("   \n\t  ")
        assert result["type"] == "Program"
        assert result["body"] == []


# ---------------------------------------------------------------------------
# parse() – simple expressions
# ---------------------------------------------------------------------------

class TestParseExpressions:
    def test_numeric_addition(self):
        result = parse("1 + 2")
        assert result["type"] == "Program"
        assert len(result["body"]) == 1
        stmt = result["body"][0]
        assert stmt["type"] == "ExpressionStatement"
        expr = stmt["expression"]
        assert expr["type"] == "BinaryExpression"
        assert expr["operator"] == "+"
        assert expr["left"]["value"] == 1
        assert expr["right"]["value"] == 2

    def test_string_literal(self):
        result = parse('"hello"')
        stmt = result["body"][0]
        assert stmt["type"] == "ExpressionStatement"
        assert stmt["expression"]["type"] == "Literal"
        assert stmt["expression"]["value"] == "hello"

    def test_numeric_literal(self):
        result = parse("42")
        expr = result["body"][0]["expression"]
        assert expr["type"] == "Literal"
        assert expr["value"] == 42

    def test_boolean_literal(self):
        result = parse("true")
        expr = result["body"][0]["expression"]
        assert expr["type"] == "Literal"
        assert expr["value"] is True

    def test_null_literal(self):
        result = parse("null")
        expr = result["body"][0]["expression"]
        assert expr["type"] == "Literal"
        assert expr["value"] is None

    def test_identifier(self):
        result = parse("x")
        expr = result["body"][0]["expression"]
        assert expr["type"] == "Identifier"
        assert expr["name"] == "x"


# ---------------------------------------------------------------------------
# parse() – variable declarations
# ---------------------------------------------------------------------------

class TestParseVarDeclarations:
    def test_var_declaration(self):
        result = parse("var x = 10;")
        decl = result["body"][0]
        assert decl["type"] == "VariableDeclaration"
        assert decl["kind"] == "var"
        assert len(decl["declarations"]) == 1
        declarator = decl["declarations"][0]
        assert declarator["type"] == "VariableDeclarator"
        assert declarator["id"]["name"] == "x"
        assert declarator["init"]["value"] == 10

    def test_let_declaration(self):
        result = parse("let y = 'abc';")
        decl = result["body"][0]
        assert decl["type"] == "VariableDeclaration"
        assert decl["kind"] == "let"

    def test_const_declaration(self):
        result = parse("const z = true;")
        decl = result["body"][0]
        assert decl["type"] == "VariableDeclaration"
        assert decl["kind"] == "const"

    def test_multiple_declarators(self):
        result = parse("var a = 1, b = 2;")
        decl = result["body"][0]
        assert len(decl["declarations"]) == 2


# ---------------------------------------------------------------------------
# parse() – function declarations
# ---------------------------------------------------------------------------

class TestParseFunctions:
    def test_function_declaration(self):
        result = parse("function foo(a, b) { return a + b; }")
        func = result["body"][0]
        assert func["type"] == "FunctionDeclaration"
        assert func["id"]["name"] == "foo"
        assert len(func["params"]) == 2
        assert func["params"][0]["name"] == "a"
        assert func["params"][1]["name"] == "b"

    def test_function_body(self):
        result = parse("function f() { return 1; }")
        func = result["body"][0]
        body = func["body"]
        assert body["type"] == "BlockStatement"
        assert len(body["body"]) == 1
        assert body["body"][0]["type"] == "ReturnStatement"


# ---------------------------------------------------------------------------
# parse() – control flow statements
# ---------------------------------------------------------------------------

class TestParseControlFlow:
    def test_if_statement(self):
        result = parse("if (x) { y; }")
        stmt = result["body"][0]
        assert stmt["type"] == "IfStatement"
        assert stmt["test"]["type"] == "Identifier"
        assert stmt["test"]["name"] == "x"
        assert stmt["consequent"]["type"] == "BlockStatement"

    def test_if_else_statement(self):
        result = parse("if (x) { y; } else { z; }")
        stmt = result["body"][0]
        assert stmt["type"] == "IfStatement"
        assert stmt["alternate"] is not None
        assert stmt["alternate"]["type"] == "BlockStatement"

    def test_while_statement(self):
        result = parse("while (true) { break; }")
        stmt = result["body"][0]
        assert stmt["type"] == "WhileStatement"
        assert stmt["test"]["value"] is True
        assert stmt["body"]["type"] == "BlockStatement"

    def test_for_statement(self):
        result = parse("for (var i = 0; i < 10; i++) { }")
        stmt = result["body"][0]
        assert stmt["type"] == "ForStatement"
        assert stmt["init"]["type"] == "VariableDeclaration"
        assert stmt["test"]["type"] == "BinaryExpression"
        assert stmt["update"]["type"] == "UpdateExpression"


# ---------------------------------------------------------------------------
# parse() – async / await (async mapping in real AST)
# ---------------------------------------------------------------------------

class TestParseAsync:
    def test_async_function_declaration(self):
        result = parse("async function f() { await x; }")
        func = result["body"][0]
        assert func["type"] == "FunctionDeclaration"
        assert func["id"]["name"] == "f"
        # The isAsync key should be mapped to "async"
        assert "async" in func
        assert func["async"] is True
        # Original key should not be present
        assert "isAsync" not in func

    def test_await_expression(self):
        result = parse("async function f() { await x; }")
        func = result["body"][0]
        body_stmts = func["body"]["body"]
        assert len(body_stmts) == 1
        expr_stmt = body_stmts[0]
        assert expr_stmt["type"] == "ExpressionStatement"
        # The await expression node
        expr = expr_stmt["expression"]
        assert expr["type"] == "AwaitExpression"


# ---------------------------------------------------------------------------
# parse() – member expressions and call expressions
# ---------------------------------------------------------------------------

class TestParseComplexExpressions:
    def test_member_expression(self):
        result = parse("a.b")
        expr = result["body"][0]["expression"]
        assert expr["type"] == "MemberExpression"
        assert expr["object"]["name"] == "a"
        assert expr["property"]["name"] == "b"
        assert expr["computed"] is False

    def test_computed_member_expression(self):
        result = parse("a[0]")
        expr = result["body"][0]["expression"]
        assert expr["type"] == "MemberExpression"
        assert expr["computed"] is True
        assert expr["property"]["value"] == 0

    def test_call_expression(self):
        result = parse("foo(1, 2)")
        expr = result["body"][0]["expression"]
        assert expr["type"] == "CallExpression"
        assert expr["callee"]["name"] == "foo"
        assert len(expr["arguments"]) == 2
        assert expr["arguments"][0]["value"] == 1
        assert expr["arguments"][1]["value"] == 2

    def test_chained_call(self):
        result = parse("a.b(c)")
        expr = result["body"][0]["expression"]
        assert expr["type"] == "CallExpression"
        assert expr["callee"]["type"] == "MemberExpression"

    def test_arrow_function(self):
        result = parse("var f = (x) => x + 1;")
        decl = result["body"][0]
        init = decl["declarations"][0]["init"]
        assert init["type"] == "ArrowFunctionExpression"
        assert len(init["params"]) == 1
        assert init["params"][0]["name"] == "x"

    def test_arrow_function_body_expression(self):
        result = parse("var f = x => x;")
        init = result["body"][0]["declarations"][0]["init"]
        assert init["type"] == "ArrowFunctionExpression"
        assert init["body"]["type"] == "Identifier"

    def test_arrow_function_block_body(self):
        result = parse("var f = (x) => { return x; };")
        init = result["body"][0]["declarations"][0]["init"]
        assert init["type"] == "ArrowFunctionExpression"
        assert init["body"]["type"] == "BlockStatement"


# ---------------------------------------------------------------------------
# parse() – misc expressions
# ---------------------------------------------------------------------------

class TestParseMisc:
    def test_ternary_expression(self):
        result = parse("x ? 1 : 2")
        expr = result["body"][0]["expression"]
        assert expr["type"] == "ConditionalExpression"

    def test_assignment_expression(self):
        result = parse("x = 5")
        expr = result["body"][0]["expression"]
        assert expr["type"] == "AssignmentExpression"
        assert expr["operator"] == "="
        assert expr["left"]["name"] == "x"
        assert expr["right"]["value"] == 5

    def test_logical_expression(self):
        result = parse("a && b")
        expr = result["body"][0]["expression"]
        assert expr["type"] == "LogicalExpression"
        assert expr["operator"] == "&&"

    def test_unary_expression(self):
        result = parse("!x")
        expr = result["body"][0]["expression"]
        assert expr["type"] == "UnaryExpression"
        assert expr["operator"] == "!"

    def test_array_expression(self):
        result = parse("[1, 2, 3]")
        expr = result["body"][0]["expression"]
        assert expr["type"] == "ArrayExpression"
        assert len(expr["elements"]) == 3

    def test_object_expression(self):
        result = parse("({a: 1, b: 2})")
        expr = result["body"][0]["expression"]
        assert expr["type"] == "ObjectExpression"
        assert len(expr["properties"]) == 2

    def test_multiple_statements(self):
        result = parse("var x = 1; var y = 2; x + y;")
        assert len(result["body"]) == 3


# ---------------------------------------------------------------------------
# parse() – top-level structure
# ---------------------------------------------------------------------------

class TestParseStructure:
    def test_returns_dict(self):
        result = parse("1")
        assert isinstance(result, dict)

    def test_has_type_program(self):
        result = parse("1")
        assert result["type"] == "Program"

    def test_has_body_list(self):
        result = parse("1")
        assert isinstance(result["body"], list)

    def test_has_sourceType(self):
        result = parse("1")
        assert result["sourceType"] == "script"

    def test_no_underscore_keys_in_output(self):
        """Ensure no keys starting with underscore appear anywhere in the AST."""
        result = parse("function foo(x) { return x + 1; }")
        _assert_no_underscore_keys(result)

    def test_optional_false_not_in_member_expression(self):
        """MemberExpression nodes have optional=False which should be stripped."""
        result = parse("a.b.c")
        expr = result["body"][0]["expression"]
        assert expr["type"] == "MemberExpression"
        assert "optional" not in expr


def _assert_no_underscore_keys(obj):
    """Recursively check that no dict keys start with underscore."""
    if isinstance(obj, dict):
        for key, value in obj.items():
            assert not key.startswith("_"), f"Found underscore key: {key}"
            _assert_no_underscore_keys(value)
    elif isinstance(obj, list):
        for item in obj:
            _assert_no_underscore_keys(item)


# ---------------------------------------------------------------------------
# parse() – syntax errors
# ---------------------------------------------------------------------------

class TestParseSyntaxErrors:
    def test_invalid_syntax_raises(self):
        with pytest.raises(SyntaxError, match="Failed to parse JavaScript"):
            parse("function (")

    def test_unclosed_brace(self):
        with pytest.raises(SyntaxError):
            parse("function f() {")

    def test_unexpected_token(self):
        with pytest.raises(SyntaxError):
            parse("var = ;")

    def test_error_message_contains_detail(self):
        with pytest.raises(SyntaxError, match="Failed to parse JavaScript"):
            parse("if if if")

    def test_error_chains_original(self):
        with pytest.raises(SyntaxError) as exc_info:
            parse("<<<")
        assert exc_info.value.__cause__ is not None
