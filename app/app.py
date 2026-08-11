import os

import psycopg2
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

app = FastAPI(title="DevOps Challenge API")


class User(BaseModel):
    name: str


def get_db_connection():
    return psycopg2.connect(
        host=os.getenv("DB_HOST", "postgres"),
        port=os.getenv("DB_PORT", "5432"),
        database=os.getenv("DB_NAME", "appdb"),
        user=os.getenv("DB_USER", "appuser"),
        password=os.getenv("DB_PASSWORD"),
    )


@app.get("/")
def home():
    return {
        "application": "DevOps Challenge API",
        "status": "running"
    }


@app.get("/health")
def health():
    return {"status": "healthy"}


@app.get("/ready")
def ready():
    try:
        connection = get_db_connection()
        connection.close()

        return {
            "status": "ready",
            "database": "connected"
        }

    except Exception as e:
        raise HTTPException(
            status_code=503,
            detail={
                "status": "not ready",
                "database": "disconnected",
                "error": str(e)
            }
        )


@app.get("/users")
def get_users():
    try:
        connection = get_db_connection()
        cursor = connection.cursor()

        cursor.execute(
            "SELECT id, name FROM users ORDER BY id"
        )

        rows = cursor.fetchall()

        cursor.close()
        connection.close()

        return [
            {"id": row[0], "name": row[1]}
            for row in rows
        ]

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/users")
def create_user(user: User):
    try:
        connection = get_db_connection()
        cursor = connection.cursor()

        cursor.execute(
            "INSERT INTO users (name) VALUES (%s) RETURNING id",
            (user.name,)
        )

        user_id = cursor.fetchone()[0]

        connection.commit()

        cursor.close()
        connection.close()

        return {
            "id": user_id,
            "name": user.name
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))