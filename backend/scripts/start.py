"""Container startup entrypoint: checks database, runs migrations/seed, starts uvicorn."""

import os
import subprocess
import sys
import time

# Ensure working directory and sys.path point to the directory containing alembic.ini and app
BACKEND_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
os.chdir(BACKEND_DIR)
if BACKEND_DIR not in sys.path:
    sys.path.insert(0, BACKEND_DIR)
parent_dir = os.path.dirname(BACKEND_DIR)
if parent_dir not in sys.path:
    sys.path.insert(1, parent_dir)


def check_and_prepare_database():
    from app.core.config import get_settings

    settings = get_settings()
    db_url = settings.DATABASE_URL
    is_localhost = "localhost" in db_url or "127.0.0.1" in db_url

    print("=" * 70)
    print("CivicPulse Backend Starting...")
    print(f"Target Database: {db_url.split('@')[-1] if '@' in db_url else 'configured'}")
    print("=" * 70)

    if is_localhost and (os.environ.get("RENDER") or os.environ.get("APP_ENV") == "production"):
        print("\n" + "!" * 70)
        print("NOTICE: DATABASE_URL is pointing to 'localhost'.")
        print("On Render, PostgreSQL runs as a separate managed service.")
        print("Please set DATABASE_URL in your Render Web Service Environment tab.")
        print("!" * 70 + "\n")

    # Try connecting to the database with retries
    from sqlalchemy import create_engine, text

    db_ready = False
    for attempt in range(1, 6):
        try:
            engine = create_engine(db_url, pool_pre_ping=True)
            with engine.connect() as conn:
                conn.execute(text("SELECT 1"))
            db_ready = True
            print(f"[OK] Database connection verified on attempt {attempt}.")
            break
        except Exception as e:
            if attempt == 1 and is_localhost and os.environ.get("RENDER"):
                print(f"[WARN] Localhost database connection failed: {e}")
                break
            print(f"[WAIT] Database connection attempt {attempt}/5: {e}. Retrying in 2s...")
            time.sleep(2)

    if db_ready:
        print("[INFO] Running database migrations (alembic upgrade head)...")
        res = subprocess.run([sys.executable, "-m", "alembic", "upgrade", "head"])
        if res.returncode == 0:
            print("[INFO] Seeding database with BRICS synthetic data...")
            subprocess.run([sys.executable, "-m", "app.db.seed"])
        else:
            print("[WARN] Alembic migrations returned non-zero code. Skipping seed.")
    else:
        print("\n" + "-" * 70)
        print("[WARN] Database is currently unavailable or not configured.")
        print("Starting API server (health check /health will remain operational).")
        print("To enable full database features, add DATABASE_URL in Render Dashboard.")
        print("-" * 70 + "\n")


def start_server():
    port = os.environ.get("PORT", "8000")
    print(f"[INFO] Launching Uvicorn on 0.0.0.0:{port}...")
    os.execvp(
        sys.executable,
        [
            sys.executable,
            "-m",
            "uvicorn",
            "app.main:app",
            "--host",
            "0.0.0.0",
            "--port",
            port,
        ],
    )


if __name__ == "__main__":
    try:
        check_and_prepare_database()
    except Exception as exc:
        print(f"[WARN] Error during startup database prep: {exc}")
    start_server()
