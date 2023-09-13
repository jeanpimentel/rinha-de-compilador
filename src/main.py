import copy
import json
import sys


def read_ast(path: str) -> dict:
    with open(path, "r") as f:
        data = json.load(f)
    return data


def evaluate(node, scope):
    if "expression" in node:
        return evaluate(node["expression"], scope)

    if node["kind"] == "Print":
        to_print = evaluate(node["value"], scope)
        if isinstance(to_print, bool):
            print("true" if to_print else "false")
        elif isinstance(to_print, tuple) and callable(to_print[1]):
            print("<#closure>")
        else:
            print(to_print)
        return

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
        fn = lambda fn_scope: evaluate(node["value"], fn_scope)
        return parameters, fn

    if node["kind"] == "Call":
        fn_scope = copy.deepcopy(scope)

        parameters, fn = evaluate(node["callee"], scope)
        arguments = [evaluate(a, scope) for a in node["arguments"]]
        for name, value in zip(parameters, arguments):
            fn_scope[name] = value

        return fn(fn_scope)

    raise Exception("Unknown kind " + node["kind"])


if __name__ == "__main__":
    ast = read_ast(sys.argv[1])
    # pprint(ast)

    global_scope = {}
    evaluate(ast, global_scope)
