import subprocess
import time
import sys

POSTGRES_SERVICE_NAME = "postgres"
FOLLOWUP_SCRIPT = "py create_database.py"
MAX_RETRIES = 20
SLEEP_SECONDS = 1

def run_command(
    cmd: str,
    check: bool = True,
    capture_output: bool = False,
    **kwargs: dict
) -> subprocess.CompletedProcess:
    try:
        return subprocess.run(cmd, shell=True, check=check, capture_output=capture_output, text=True, **kwargs)
    except subprocess.CalledProcessError as e:
        print(f"Command '{cmd}' failed: {e}")
        sys.exit(1)

def get_postgres_container_id() -> str:
    result = run_command(f"docker-compose ps -q {POSTGRES_SERVICE_NAME}", capture_output=True)
    container_id = result.stdout.strip()
    if not container_id:
        print("Error: Could not find Postgres container.")
        sys.exit(1)
    return container_id

def wait_for_postgres(container_id: str) -> None:
    print("Waiting for Postgres to be ready...")
    for i in range(MAX_RETRIES):
        try:
            run_command(f"docker exec {container_id} pg_isready -U postgres", check=True)
            print("Postgres is ready!")
            return
        except subprocess.CalledProcessError as e:
            print(f"Still waiting... ({i + 1}/{MAX_RETRIES}) Exit code: {e.returncode}")
            print(f"Output: {e.output if hasattr(e, 'output') else 'N/A'}")
            time.sleep(SLEEP_SECONDS)
    print("Postgres did not become ready in time.")
    sys.exit(1)

def main() -> None:
    print("Stopping Docker Compose...")
    run_command("docker-compose down")

    print("Starting Docker Compose...")
    run_command("docker-compose up -d")

    container_id = get_postgres_container_id()
    wait_for_postgres(container_id)

    print("Running follow-up script...")
    run_command(FOLLOWUP_SCRIPT)

if __name__ == "__main__":
    main()
