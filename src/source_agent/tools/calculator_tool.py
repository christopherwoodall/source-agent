import ast
import math
import operator
from typing import Union
from .tool_registry import registry


# --- Configuration for Safe Evaluation ---
# Whitelist of allowed AST operator types mapping to Python's operator functions
SAFE_OPERATORS = {
    ast.Add: operator.add,
    ast.Sub: operator.sub,
    ast.Mult: operator.mul,
    ast.Div: operator.truediv,  # True division (e.g., 5 / 2 = 2.5)
    ast.FloorDiv: operator.floordiv,  # Floor division (e.g., 5 // 2 = 2)
    ast.Pow: operator.pow,  # Exponentiation (e.g., 2**3 = 8)
    ast.Mod: operator.mod,  # Modulo (e.g., 5 % 2 = 1)
    ast.USub: operator.neg,  # Unary negation (e.g., -5)
    ast.UAdd: operator.pos,  # Unary positive (e.g., +5)
}

# Whitelist of allowed functions and constants
SAFE_FUNCTIONS = {
    "abs": abs,
    "round": round,
    "max": max,
    "min": min,
    "sum": sum,
    "sqrt": math.sqrt,
    "sin": math.sin,
    "cos": math.cos,
    "tan": math.tan,
    "log": math.log,
    "log10": math.log10,
    "exp": math.exp,
    "ceil": math.ceil,
    "floor": math.floor,
    "fmod": math.fmod,
    "radians": math.radians,
    "degrees": math.degrees,
    # Constants
    "pi": math.pi,
    "e": math.e,
}


# --- Helper for Safe AST Evaluation ---
def _evaluate_expression_node(node):
    """Safely evaluates an AST node based on whitelisted operators and functions."""
    if isinstance(
        node, ast.Constant
    ):  # Handles numbers and strings (though we only expect numbers)
        return node.value
    elif isinstance(
        node, ast.Name
    ):  # Handles variables/constants (like 'pi', 'e') or function names
        if node.id in SAFE_FUNCTIONS:
            return SAFE_FUNCTIONS[node.id]
        else:
            raise ValueError(f"Unsupported name/constant: {node.id}")
    elif isinstance(node, ast.BinOp):  # Binary operations (e.g., a + b)
        left = _evaluate_expression_node(node.left)
        right = _evaluate_expression_node(node.right)
        op_type = type(node.op)
        if op_type in SAFE_OPERATORS:
            # Handle potential division by zero
            if op_type in (ast.Div, ast.FloorDiv, ast.Mod) and right == 0:
                raise ValueError("Division or modulo by zero is not allowed.")
            return SAFE_OPERATORS[op_type](left, right)
        else:
            raise ValueError(f"Unsupported binary operation: {op_type.__name__}")
    elif isinstance(node, ast.UnaryOp):  # Unary operations (e.g., -a, +a)
        operand = _evaluate_expression_node(node.operand)
        op_type = type(node.op)
        if op_type in SAFE_OPERATORS:
            return SAFE_OPERATORS[op_type](operand)
        else:
            raise ValueError(f"Unsupported unary operation: {op_type.__name__}")
    elif isinstance(node, ast.Call):  # Function calls (e.g., sqrt(16))
        func_node = node.func
        if isinstance(
            func_node, ast.Name
        ):  # Ensure it's a function name from our whitelist
            func_name = func_node.id
            if func_name in SAFE_FUNCTIONS and callable(SAFE_FUNCTIONS[func_name]):
                func = SAFE_FUNCTIONS[func_name]
                args = [_evaluate_expression_node(arg) for arg in node.args]
                return func(*args)
            else:
                raise ValueError(f"Unsupported or non-callable function: {func_name}")
        else:
            raise ValueError(f"Unsupported function call type: {type(func_node)}")
    else:
        # Prevent evaluation of other AST node types that could be malicious
        raise ValueError(f"Unsupported expression component: {type(node).__name__}")


@registry.register(
    name="calculate_expression",
    description="Evaluates a mathematical expression string (e.g., '2 * (3 + 4)', 'sqrt(16) + pi').",
    parameters={
        "type": "object",
        "properties": {
            "expression": {
                "type": "string",
                "description": "The mathematical expression string to evaluate.",
            }
        },
        "required": ["expression"],
    },
)
def calculate_expression_tool(expression: str) -> Union[int, float, str]:
    """
    Evaluates a mathematical expression safely using AST parsing.

    Args:
        expression (str): The mathematical expression to evaluate.

    Returns:
        Union[int, float, str]: The numerical result of the expression, or an error string.
    """
    try:
        # Parse the expression string into an AST.
        # mode='eval' ensures only valid expressions (not full Python code) are parsed.
        tree = ast.parse(expression, mode="eval")

        # Safely evaluate the parsed AST
        result = _evaluate_expression_node(tree.body)

        # Return the result as a number
        return result

    except SyntaxError as e:
        return f"Error: Invalid expression syntax. {e}"
    except ValueError as e:
        return f"Error: {e}"
    except TypeError as e:
        return f"Error: Type error in expression. {e}"
    except Exception as e:
        return f"An unexpected error occurred during calculation: {e}"
