import json
import sys
from pprint import pprint


def read_ast(path: str) -> dict:
    with open(path, "r") as f:
        data = json.load(f)
    return data


def evaluate(param, env):
    if param["kind"] == "Print":
        to_print = evaluate(param["value"], env)
        if isinstance(to_print, bool):
            print("true" if to_print else "false")
        else:
            print(to_print)
        return

    if param["kind"] == "Let":
        value = evaluate(param["value"], env)
        if param["name"]["text"] != "_":
            env[param["name"]["text"]] = value
        if param["next"]:
            return evaluate(param["next"], env)

    if param["kind"] == "Binary":
        lhs = evaluate(param["lhs"], env)
        rhs = evaluate(param["rhs"], env)
        if param["op"] == "Add":
            return lhs + rhs
        if param["op"] == "Sub":
            return lhs - rhs
        if param["op"] == "Mul":
            return lhs * rhs
        if param["op"] == "Div":
            return lhs / rhs
        if param["op"] == "Mod":
            return lhs % rhs
        if param["op"] == "Eq":
            return lhs == rhs
        if param["op"] == "Neq":
            return lhs != rhs
        if param["op"] == "Lt":
            return lhs < rhs
        if param["op"] == "Gt":
            return lhs > rhs
        if param["op"] == "Lte":
            return lhs <= rhs
        if param["op"] == "Gte":
            return lhs >= rhs
        if param["op"] == "And":
            return lhs and rhs
        if param["op"] == "Or":
            return lhs or rhs

    if param["kind"] == "If":
        if evaluate(param["condition"], env):
            return evaluate(param["then"], env)
        else:
            return evaluate(param["otherwise"], env)

    if param["kind"] == "Var":
        return env[param["text"]]

    if param["kind"] == "Str":
        return str(param["value"])

    if param["kind"] == "Int":
        return int(param["value"])

    if param["kind"] == "Bool":
        return bool(param["value"])

    if param["kind"] == "Tuple":
        return (
            evaluate(param["first"], env),
            evaluate(param["second"], env),
        )

    if param["kind"] == "First":
        return evaluate(param["value"]["first"], env)

    if param["kind"] == "Second":
        return evaluate(param["value"]["second"], env)

    if param["kind"] == "Function":
        raise Exception("Function not implemented")

    if param["kind"] == "Call":
        raise Exception("Call not implemented")

    else:
        raise Exception("unknown kind " + param["kind"])


if __name__ == "__main__":
    ast = read_ast(sys.argv[1])
    # pprint(ast)

    env = {}
    evaluate(ast["expression"], env)
