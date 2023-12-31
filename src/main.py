import copy
import json
import sys

USE_MEMOIZE = True

IMPURE_FUNCTIONS = []
MEMOIZED_FUNCTIONS = {}


def read_ast(path: str) -> dict:
    with open(path, "r") as f:
        data = json.load(f)
    return data


def get_func_id(location, parameters):
    fn_id = (
        location["start"],
        location["end"],
    ) + tuple(parameters)
    return fn_id


def get_memoization_key(fn_id, arguments):
    memo_key = fn_id
    for arg in arguments:
        if isinstance(arg, tuple) and callable(arg[1]):
            memo_key += (arg[2],)
        else:
            memo_key += (arg,)
    return memo_key


def evaluate(node, scope):
    global IMPURE_FUNCTIONS

    if "expression" in node:
        return evaluate(node["expression"], scope)

    if node["kind"] == "Print":
        if "#fn_id" in scope:
            IMPURE_FUNCTIONS.append(scope["#fn_id"])

        content = evaluate(node["value"], scope)
        if isinstance(content, bool):
            print("true" if content else "false")
        elif isinstance(content, tuple) and callable(content[1]):
            print("<#closure>")
        else:
            print(content)
        return content

    if node["kind"] == "Let":
        value = evaluate(node["value"], scope)
        if node["name"]["text"] != "_":
            scope[node["name"]["text"]] = value
        if node["next"]:
            return evaluate(node["next"], scope)

    if node["kind"] == "Binary":
        lhs = evaluate(node["lhs"], scope)
        rhs = evaluate(node["rhs"], scope)
        if node["op"] == "Add":
            if isinstance(lhs, str) or isinstance(rhs, str):
                return str(lhs) + str(rhs)
            return lhs + rhs
        if node["op"] == "Sub":
            return lhs - rhs
        if node["op"] == "Mul":
            return lhs * rhs
        if node["op"] == "Div":
            return lhs / rhs
        if node["op"] == "Mod":
            return lhs % rhs
        if node["op"] == "Eq":
            return lhs == rhs
        if node["op"] == "Neq":
            return lhs != rhs
        if node["op"] == "Lt":
            return lhs < rhs
        if node["op"] == "Gt":
            return lhs > rhs
        if node["op"] == "Lte":
            return lhs <= rhs
        if node["op"] == "Gte":
            return lhs >= rhs
        if node["op"] == "And":
            return lhs and rhs
        if node["op"] == "Or":
            return lhs or rhs

    if node["kind"] == "If":
        if evaluate(node["condition"], scope):
            return evaluate(node["then"], scope)
        else:
            return evaluate(node["otherwise"], scope)

    if node["kind"] == "Var":
        return scope[node["text"]]

    if node["kind"] == "Str":
        return str(node["value"])

    if node["kind"] == "Int":
        return int(node["value"])

    if node["kind"] == "Bool":
        return bool(node["value"])

    if node["kind"] == "Tuple":
        return (
            evaluate(node["first"], scope),
            evaluate(node["second"], scope),
        )

    if node["kind"] == "First":
        return evaluate(node["value"]["first"], scope)

    if node["kind"] == "Second":
        return evaluate(node["value"]["second"], scope)

    if node["kind"] == "Function":
        parameters = [p["text"] for p in node["parameters"]]

        current_scope = copy.deepcopy(scope)

        fn_id = get_func_id(node["location"], parameters)

        fn = lambda args: evaluate(
            node["value"], current_scope | args | {"#fn_id": fn_id}
        )

        return parameters, fn, fn_id

    if node["kind"] == "Call":
        parameters, fn, fn_id = evaluate(node["callee"], scope)
        arguments = [evaluate(a, scope) for a in node["arguments"]]

        kwargs = dict(zip(parameters, arguments))
        if "text" in node["callee"]:
            kwargs[node["callee"]["text"]] = scope[node["callee"]["text"]]

        memoization_key = None
        if USE_MEMOIZE:
            memoization_key = get_memoization_key(fn_id, arguments)
            if memoization_key in MEMOIZED_FUNCTIONS:
                return MEMOIZED_FUNCTIONS[memoization_key]

        result = fn(kwargs)

        if USE_MEMOIZE and fn_id not in IMPURE_FUNCTIONS:
            MEMOIZED_FUNCTIONS[memoization_key] = result

        return result

    raise Exception("Unknown kind " + node["kind"])


if __name__ == "__main__":
    ast = read_ast(sys.argv[1])
    # pprint(ast)

    # print(sys.getrecursionlimit())
    sys.setrecursionlimit(10000)

    global_scope = {}
    evaluate(ast, global_scope)

    print("\n\nImpure functions:")
    print(IMPURE_FUNCTIONS)
