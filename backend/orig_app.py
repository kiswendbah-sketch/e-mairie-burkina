"""
Backup of original root app.py moved into backend.
"""

from flask_bcrypt import Bcrypt
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required
from flask import Flask, request, jsonify
import sqlite3

app = Flask(__name__)

bcrypt = Bcrypt(app)
login_manager = LoginManager()
login_manager.init_app(app)


@app.after_request
def after_request(response):
    response.headers["Access-Control-Allow-Origin"] = "*"
    response.headers["Access-Control-Allow-Headers"] = "Content-Type"
    response.headers["Access-Control-Allow-Methods"] = "GET, POST, OPTIONS"
    return response


@app.route("/")
def accueil():
    return "e-Mairie Burkina fonctionne !"

# (rest omitted in backup)
