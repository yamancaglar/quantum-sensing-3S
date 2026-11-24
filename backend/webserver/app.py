"""Quantum-sensing webserver: read-only JSON API for the UI."""
import os
from pathlib import Path

from flask import Flask, jsonify
from flask_cors import CORS
from werkzeug.exceptions import HTTPException

import db
from routes import bp

HERE = Path(__file__).resolve().parent


def create_app(config=None):
    app = Flask(__name__)
    app.config["DB_PATH"] = os.environ.get("DB_PATH", str(HERE.parent / "mock.db"))
    if config:
        app.config.update(config)
    origins = os.environ.get("CORS_ORIGINS", "*").split(",")
    CORS(app, resources={r"/api/*": {"origins": origins}})
    app.teardown_appcontext(db.close_db)
    app.register_blueprint(bp)

    @app.errorhandler(HTTPException)
    def json_error(e):
        return jsonify(error=e.description), e.code

    return app


app = create_app()
