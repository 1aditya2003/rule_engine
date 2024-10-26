from flask import Blueprint, request, jsonify
from services.ast_parser import parse_rule, combine_rules, evaluate_rule
from services.db_service import save_rule, get_all_rules

rule_bp = Blueprint('rule_bp', __name__)

@rule_bp.route('/create_rule', methods=['POST'])
def create_rule():
    data = request.json
    rule_string = data.get('rule_string', '')

    if not rule_string:
        return jsonify({'error': 'No rule string provided'}), 400

    try:
        ast = parse_rule(rule_string)
        # Save the rule to the database
        save_rule(rule_string)
        return jsonify({'ast': ast.to_dict(), 'message': 'Rule created successfully.'}), 201
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@rule_bp.route('/combine_rules', methods=['POST'])
@rule_bp.route('/combine_rules', methods=['POST'])
def combine_rule():
    data = request.json
    rule_strings = data.get('rules', [])

    if not rule_strings or len(rule_strings) < 2:
        return jsonify({'error': 'Two rules are required for combining'}), 400

    try:
        # Combine the rules into a single AST
        combined_ast = combine_rules(rule_strings)

        # Save both rules and their combination to the database
        save_rule(rule_strings[0], second_rule_string=rule_strings[1], combined_rule=combined_ast)

        return jsonify({'ast': combined_ast.to_dict(), 'message': 'Rules combined and saved successfully.'}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@rule_bp.route('/evaluate_rule', methods=['POST'])
def evaluate_rule():
    data = request.get_json()
    print("Received data:", data)  # Log the incoming data for debugging

    combined_ast = data.get("ast")
    user_data = data.get("user_data")

    if not combined_ast or not user_data:
        return jsonify({"error": "Missing AST or user data"}), 400

    try:
        # Assuming evaluate_rule function in ast_parser.py
        result = evaluate_rule(combined_ast, user_data)
        return jsonify({"result": result}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500 # Return 500 for server errors


@rule_bp.route('/rules', methods=['GET'])
def fetch_rules():
    rules = get_all_rules()
    return jsonify({'rules': [{'id': rule[0], 'rule_string': rule[1]} for rule in rules]}), 200    