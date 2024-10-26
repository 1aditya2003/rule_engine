from flask import json
import mariadb
import os
from dotenv import load_dotenv
import json
from  services.ast_parser import ast_to_string
import mysql.connector


# Load environment variables from .env file
load_dotenv()

def get_db_connection():
    try:
        conn = mariadb.connect(
            user=os.getenv('DB_USER'),
            password=os.getenv('DB_PASSWORD'),
            host=os.getenv('DB_HOST'),
            database=os.getenv('DB_NAME')
        )
        return conn
    except mariadb.Error as e:
        print(f"Error connecting to MariaDB: {e}")
        return None
def get_latest_rule():
    # Assuming you're fetching the latest rule from the rules table
    conn = get_db_connection()
    if conn is None:
        print("Failed to establish database connection.")
        return None

    try:
        cursor = conn.cursor()
        # Fetch the latest rule based on the created_at timestamp
        query = "SELECT id, rule_string, combined_rule, user_data FROM rules ORDER BY created_at DESC LIMIT 1"
        cursor.execute(query)
        latest_rule = cursor.fetchone()
        cursor.close()
        # Return rule data if found
        if latest_rule:
            return {
                'id': latest_rule[0],
                'rule_string': latest_rule[1],
                'combined_rule': latest_rule[2],
                'user_data': json.loads(latest_rule[3]) if latest_rule[3] else None
            }
        return None
    except mariadb.Error as e:
        print(f"Error fetching latest rule: {e}")
        return None
    finally:
        conn.close()


def save_rule(rule_string, second_rule_string=None, combined_rule=None, user_data=None):
    combined_rule_string = ast_to_string(combined_rule) if combined_rule else None
    user_data_json = json.dumps(user_data) if user_data else None

    print(f"Saving first rule: {rule_string}")
    if second_rule_string:
        print(f"Saving second rule: {second_rule_string}")
    print(f"Combined rule before saving: {combined_rule_string}")
    print(f"User data before saving: {user_data_json}")

    conn = get_db_connection()
    if conn is None:
        print("Failed to establish database connection.")
        return False

    try:
        cursor = conn.cursor()

        # Insert the first rule
        cursor.execute(
            "INSERT INTO rules (rule_string, combined_rule, user_data) VALUES (%s, %s, %s)",
            (rule_string, combined_rule_string, user_data_json)
        )

        # Insert the second rule if provided
        if second_rule_string:
            cursor.execute(
                "INSERT INTO rules (rule_string, combined_rule, user_data) VALUES (%s, %s, %s)",
                (second_rule_string, combined_rule_string, user_data_json)
            )

        conn.commit()
        cursor.close()
        print("Rules saved successfully.")
        return True
    except mariadb.Error as e:
        print(f"Error saving rule: {e}")
        return False
    finally:
        conn.close()

def get_all_rules():
    conn = get_db_connection()
    if conn is None:
        print("Failed to establish database connection.")
        return []

    try:
        cursor = conn.cursor()
        cursor.execute("SELECT id, rule_string, combined_rule, user_data FROM rules")
        rules = cursor.fetchall()
        cursor.close()
        # Convert JSON strings back to Python dictionaries
        return [{'id': rule[0], 'rule_string': rule[1], 'combined_rule': rule[2], 
                 'user_data': json.loads(rule[3]) if rule[3] else None} for rule in rules]
    except mariadb.Error as e:
        print(f"Error fetching rules: {e}")
        return []
    finally:
        conn.close()
        
save_rule("Combined Salary and Experience Rule")

import mysql.connector

def get_rules():
    connection = mysql.connector.connect(
        host=os.getenv('DB_HOST'),
        user=os.getenv('DB_USER'),
        password=os.getenv('DB_PASSWORD'),
        database=os.getenv('DB_NAME')
    )
    cursor = connection.cursor()
    cursor.execute("SELECT rule_string, combined_rule FROM rules")
    rules = cursor.fetchall()
    cursor.close()
    connection.close()
    return rules  