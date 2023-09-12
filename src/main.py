import copy
import json
import sys
from pprint import pprint


def read_ast(path: str) -> dict:
    with open(path, "r") as f:
        data = json.load(f)
    return data


def evaluate(node, env):
    if "expression" in node:
        return evaluate(node["expression"], env)

    if node["kind"] == "Print":
        to_print = evaluate(node["value"], env)
        if isinstance(to_print, bool):
            print("true" if to_print else "false")
        elif isinstance(to_print, tuple) and callable(to_print[1]):
            print("<#closure>")
        else:
            print(to_print)
        return

    if node["kind"] == "Let":
        value = evaluate(node["value"], env)
        if node["name"]["text"] != "_":
            env[node["name"]["text"]] = value
        if node["next"]:
            return evaluate(node["next"], env)

    if node["kind"] == "Binary":
        lhs = evaluate(node["lhs"], env)
        rhs = evaluate(node["rhs"], env)
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
        if evaluate(node["condition"], env):
            return evaluate(node["then"], env)
        else:
            return evaluate(node["otherwise"], env)

    if node["kind"] == "Var":
        return env[node["text"]]

    if node["kind"] == "Str":
        return str(node["value"])

    if node["kind"] == "Int":
        return int(node["value"])

    if node["kind"] == "Bool":
        return bool(node["value"])

    if node["kind"] == "Tuple":
        return (
            evaluate(node["first"], env),
            evaluate(node["second"], env),
        )

    if node["kind"] == "First":
        return evaluate(node["value"]["first"], env)

    if node["kind"] == "Second":
        return evaluate(node["value"]["second"], env)

    if node["kind"] == "Function":
        parameters = [p["text"] for p in node["parameters"]]
        fn = lambda fn_env: evaluate(node["value"], fn_env)
        return parameters, fn

    if node["kind"] == "Call":
        fn_env = copy.deepcopy(env)

        parameters, fn = evaluate(node["callee"], env)
        arguments = [evaluate(a, env) for a in node["arguments"]]
        for name, value in zip(parameters, arguments):
            fn_env[name] = value

        return fn(fn_env)
    else:
        raise Exception("unknown kind " + node["kind"])


if __name__ == "__main__":
    ast = read_ast(sys.argv[1])
    # pprint(ast)

    env = {}
    evaluate(ast, env)
