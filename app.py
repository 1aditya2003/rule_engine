from flask import Flask, render_template
from flask_cors import CORS  # Import CORS
from routes.rule_routes import rule_bp

app = Flask(__name__)

# Enable CORS for all routes
CORS(app, resources={r"/api/*": {"origins": "*"}})  # Allow all origins for API routes

# Register blueprint
app.register_blueprint(rule_bp, url_prefix='/api')  # Optional: prefix for your API routes

# Add a route for the homepage
@app.route('/')
def home():
    return render_template('index.html')  # Ensure 'index.html' exists in the 'templates' folder

if __name__ == '__main__':
    app.run(debug=True)
