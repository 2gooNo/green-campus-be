from dotenv import load_dotenv
from flask import Flask
from flask_cors import CORS

# Load environment variables before importing modules that use DB config.
load_dotenv()

from routes import register_blueprints

# Create and configure the Flask app.
app = Flask(__name__)
CORS(app)

# Register grouped route blueprints.
register_blueprints(app)


if __name__ == "__main__":
    app.run(debug=True)