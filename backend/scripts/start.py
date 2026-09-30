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


def find_frontend_standalone():
    """Look for compiled Next.js standalone server.js."""
    candidates = [
        os.path.join(BACKEND_DIR, "..", "frontend", ".next", "standalone", "server.js"),
        os.path.join(BACKEND_DIR, "frontend", ".next", "standalone", "server.js"),
        "/code/frontend/.next/standalone/server.js",
        "/app/frontend/.next/standalone/server.js",
    ]
    for path in candidates:
        norm = os.path.abspath(path)
        if os.path.isfile(norm):
            return norm
    return None


def start_server():
    public_port = os.environ.get("PORT", "8000")
    standalone_server = find_frontend_standalone()

    if not standalone_server:
        print(f"[INFO] Frontend standalone not found. Launching FastAPI on 0.0.0.0:{public_port}...")
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
                public_port,
            ],
        )
        return

    # Dual-service mode: FastAPI on 127.0.0.1:8000, Next.js on 0.0.0.0:$PORT
    print("=" * 70)
    print("Starting Unified CivicPulse Server (Next.js Frontend + FastAPI Backend)")
    print(f"Public Port (Next.js): {public_port}")
    print("Internal Port (FastAPI): 8000")
    print("=" * 70)

    import signal
    import urllib.request

    print("[INFO] Launching FastAPI backend on 127.0.0.1:8000...")
    fastapi_proc = subprocess.Popen(
        [
            sys.executable,
            "-m",
            "uvicorn",
            "app.main:app",
            "--host",
            "127.0.0.1",
            "--port",
            "8000",
        ],
        cwd=BACKEND_DIR,
    )

    # Wait for FastAPI to be responsive
    for attempt in range(1, 20):
        try:
            with urllib.request.urlopen("http://127.0.0.1:8000/health", timeout=1) as resp:
                if resp.status == 200:
                    print(f"[OK] FastAPI backend verified on attempt {attempt}.")
                    break
        except Exception:
            time.sleep(0.5)

    standalone_dir = os.path.dirname(standalone_server)
    frontend_env = os.environ.copy()
    frontend_env["PORT"] = public_port
    frontend_env["HOSTNAME"] = "0.0.0.0"
    frontend_env["BACKEND_URL"] = "http://127.0.0.1:8000"
    frontend_env["NEXT_PUBLIC_API_URL"] = "/api/proxy"

    print(f"[INFO] Launching Next.js frontend on 0.0.0.0:{public_port}...")
    nextjs_proc = subprocess.Popen(
        ["node", "server.js"],
        cwd=standalone_dir,
        env=frontend_env,
    )

    def shutdown(signum=None, frame=None):
        print("\n[INFO] Shutting down services...")
        try:
            nextjs_proc.terminate()
        except Exception:
            pass
        try:
            fastapi_proc.terminate()
        except Exception:
            pass
        sys.exit(0)

    signal.signal(signal.SIGTERM, shutdown)
    signal.signal(signal.SIGINT, shutdown)

    try:
        while True:
            if fastapi_proc.poll() is not None:
                print(f"[WARN] FastAPI backend process exited (code {fastapi_proc.returncode}).")
                shutdown()
                break
            if nextjs_proc.poll() is not None:
                print(f"[WARN] Next.js frontend process exited (code {nextjs_proc.returncode}).")
                shutdown()
                break
            time.sleep(1)
    except KeyboardInterrupt:
        shutdown()


if __name__ == "__main__":
    try:
        check_and_prepare_database()
    except Exception as exc:
        print(f"[WARN] Error during startup database prep: {exc}")
    start_server()
