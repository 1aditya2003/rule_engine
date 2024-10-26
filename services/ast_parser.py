import json
import re
import mariadb  # Make sure to have the mariadb package installed
from services.node import Node  # Assuming your Node class is defined here


def clean_ast(node):
    if node is None:
        return None

    # Clean the left and right nodes
    if node.node_type == "operator":
        node.left = clean_ast(node.left)
        node.right = clean_ast(node.right)

        # Ensure we return the operator node only if it has both children
        if node.left and node.right:
            return node

        # Return whichever child exists (left or right)
        return node.left if node.left else node.right

    # If it's an operand, return it directly
    return node

def parse_rule(rule_string):
    rule_string = rule_string.replace(" ", "")
    
    if rule_string.count('(') != rule_string.count(')'):
        raise ValueError("Rule string format is incorrect: Unmatched parentheses")

    # Regular expression to match conditions
    pattern = r"([a-zA-Z_]+)([<>]=?|=|!=)([0-9]+|'[a-zA-Z_]+'|\"[a-zA-Z_]+\")"

    def parse_expression(index):
        stack = []
        current_node = None

        while index < len(rule_string):
            char = rule_string[index]

            if char == '(':
                # Start a new group
                stack.append(current_node)
                current_node = Node(node_type='group')
                index += 1

            elif char == ')':
                # End the current group
                if stack:
                    previous_node = stack.pop()
                    if previous_node:
                        previous_node.right = current_node
                        current_node = previous_node
                index += 1

            elif rule_string.startswith("AND", index):
                # Handle AND operator
                current_node = Node(node_type='operator', value='AND', left=current_node)
                index += 3

            elif rule_string.startswith("OR", index):
                # Handle OR operator
                current_node = Node(node_type='operator', value='OR', left=current_node)
                index += 2

            else:
                # Match and parse expressions
                match = re.match(pattern, rule_string[index:])
                if match:
                    left_operand, operator, right_operand = match.groups()
                    new_node = Node(node_type='operand', value={
                        "left": left_operand,
                        "operator": operator,
                        "right": right_operand.strip("'\"")
                    })
                    if current_node is None:
                        current_node = new_node
                    else:
                        # Link the new node to the current node
                        current_node.right = new_node
                    index += len(match.group(0))
                else:
                    raise ValueError(f"Rule string format is incorrect at: {char}")

        if current_node is None:
            raise ValueError("Rule string format is incorrect: No valid expression found")

        return current_node

    # Start parsing from index 0
    return parse_expression(0)

def combine_rules(rules):
    if not rules or len(rules) == 0:
        raise ValueError("No rules provided")

    combined_root = None

    for rule_string in rules:
        rule_ast = parse_rule(rule_string)

        if combined_root is None:
            combined_root = rule_ast
        else:
            combined_root = Node(node_type="operator", left=combined_root, right=rule_ast, value="AND")

    return combined_root

# Function to evaluate the AST
def evaluate_rule(ast_dict, data):
    if ast_dict['node_type'] == "operator":
        if ast_dict['value'] == "AND":
            left_result = evaluate_rule(ast_dict['left'], data)
            right_result = evaluate_rule(ast_dict['right'], data)
            print(f"AND Evaluation: {left_result} AND {right_result}")
            return left_result and right_result
        elif ast_dict['value'] == "OR":
            left_result = evaluate_rule(ast_dict['left'], data)
            right_result = evaluate_rule(ast_dict['right'], data)
            print(f"OR Evaluation: {left_result} OR {right_result}")
            return left_result or right_result
    elif ast_dict['node_type'] == "operand":
        return eval_operand(ast_dict['value'], data)
    elif ast_dict['node_type'] == "group":
        return evaluate_rule(ast_dict['right'], data)

# Function to evaluate operands
def eval_operand(condition, data):
    try:
        field = condition['left']
        operator = condition['operator']
        value = condition['right']
        
        if field not in data:
            print(f"Field '{field}' not found in user data.")
            return False

        print(f"Comparing: {data[field]} {operator} {value}")

        # Convert to correct type for comparison
        if isinstance(data[field], str) and data[field].isdigit():
            data[field] = int(data[field])

        if isinstance(value, str) and value.isdigit():
            value = int(value)
        elif isinstance(value, str) and is_float(value):
            value = float(value)

        # Comparison based on operator
        if operator == '>':
            return data[field] > value
        elif operator == '<':
            return data[field] < value
        elif operator == '=':
            return data[field] == value
        elif operator == '>=':
            return data[field] >= value
        elif operator == '<=':
            return data[field] <= value
        elif operator == '!=':
            return data[field] != value
        else:
            raise ValueError(f"Unsupported operator: {operator}")
    except Exception as e:
        print(f"Error evaluating operand: {e}")
        return False

# Function to check if a string is a float
def is_float(value):
    try:
        float(value)
        return True
    except ValueError:
        return False

# Function to save rules to the database


# Example usage
rules = [
    "salary < 40000 AND experience >= 5",
    "age < 30 AND department != 'IT'"
]

# Combine the rules into a single AST
combined_ast = combine_rules(rules)

# Clean the AST to remove unnecessary structures
cleaned_ast = clean_ast(combined_ast)

# Convert cleaned_ast to a dictionary format to print or return as needed
def ast_to_dict(ast):
    if ast is None:
        return None
    result = {
        "node_type": ast.node_type,
        "value": ast.value,
        "left": ast_to_dict(ast.left),
        "right": ast_to_dict(ast.right)
    }
    return result

# Print the cleaned AST in dictionary format
cleaned_ast_dict = ast_to_dict(cleaned_ast)
print(cleaned_ast_dict)

# Sample user data for evaluation
user_data = {
    "salary": 35000,
    "experience": 5,
    "age": 29,
    "department": "HR"
}

# Evaluate the rule
evaluation_result = evaluate_rule(cleaned_ast_dict, user_data)
print(f"Evaluation Result: {evaluation_result}")

# Save the rule to the database
# services/ast_parser.py

def ast_to_string(ast):
    if ast is None:
        return ""

    # Operator nodes (AND, OR)
    if ast.node_type == "operator":
        left_str = ast_to_string(ast.left)
        right_str = ast_to_string(ast.right)
        # Return the format with parentheses around both sides
        return f"({left_str} {ast.value} {right_str})"

    # Operand nodes (conditions like age > 30)
    elif ast.node_type == "operand":
        condition = ast.value
        return f"{condition['left']} {condition['operator']} {condition['right']}"

    # If it's a group, process the right side (since groups hold expressions)
    elif ast.node_type == "group":
        return f"({ast_to_string(ast.right)})"
    
    return ""
