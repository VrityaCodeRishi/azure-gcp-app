import os

import psycopg
from flask import Flask, jsonify

app = Flask(__name__)


def connect():
    # The Cloud SQL Auth Proxy sidecar listens on localhost and handles TLS and
    # IAM authentication, so no password or SSL is needed on this hop.
    return psycopg.connect(
        host=os.environ.get("DB_HOST", "127.0.0.1"),
        port=int(os.environ.get("DB_PORT", "5432")),
        dbname=os.environ["DB_NAME"],
        user=os.environ["DB_USER"],
        sslmode="disable",
        connect_timeout=5,
    )


@app.get("/")
def index():
    return jsonify(message="Hello from GKE, deployed by Azure DevOps")


@app.get("/healthz")
def healthz():
    return jsonify(status="ok")


@app.get("/db")
def db():
    try:
        with connect() as conn:
            row = conn.execute("SELECT current_user, current_database(), now()").fetchone()
    except Exception as exc:
        return jsonify(status="error", error=str(exc)), 500
    return jsonify(status="ok", user=row[0], database=row[1], time=row[2].isoformat())
