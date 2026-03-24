from .sensor import sensor_bp
from .control import control_bp
from .data import data_bp


def register_blueprints(app):
    # Keep route registration centralized in one place.
    app.register_blueprint(sensor_bp)
    app.register_blueprint(control_bp)
    app.register_blueprint(data_bp)
