from dotenv import load_dotenv
from flask import Flask
from flask_cors import CORS

load_dotenv()

from routes import register_blueprints

app = Flask(__name__)
CORS(app)

register_blueprints(app)


if __name__ == "__main__":
    app.run(debug=True)