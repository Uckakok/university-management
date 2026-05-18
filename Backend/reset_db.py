import subprocess
import os
from pathlib import Path


def reset():
    mysql_path = r"c:/xampp/mysql/bin/mysql.exe"  # TODO: make portable
    user = "root"
    db_name = "university"
    script_path = os.path.join(os.path.dirname(__file__), "SetupScript.sql")

    env_path = Path(__file__).parent / ".env"
    if env_path.exists():
        with open(env_path) as f:
            for line in f:
                if "=" in line and not line.startswith("#"):
                    key, value = line.strip().split("=", 1)
                    os.environ[key] = value

    student_pass = os.getenv("DB_STUDENT_PASSWORD", "temp_student_pass")
    admin_pass = os.getenv("DB_ADMIN_PASSWORD", "temp_admin_pass")
    guest_pass = os.getenv("DB_GUEST_PASSWORD", "temp_guest_pass")

    try:
        print("Dropping and recreating database...")
        subprocess.run(
            [
                mysql_path,
                "-u",
                user,
                "-e",
                f"DROP DATABASE IF EXISTS {db_name}; CREATE DATABASE {db_name};",
            ],
            check=True,
        )

        print(f"Running {script_path}...")
        shell_command = f'type "{script_path}" | "{mysql_path}" -u {user} {db_name}'
        subprocess.run(shell_command, shell=True, check=True)

        print("Setting application user passwords...")
        password_commands = [
            f"ALTER USER 'app_student'@'localhost' IDENTIFIED BY '{student_pass}';",
            f"ALTER USER 'app_admin'@'localhost' IDENTIFIED BY '{admin_pass}';",
            f"ALTER USER 'app_guest'@'localhost' IDENTIFIED BY '{guest_pass}';",
            "FLUSH PRIVILEGES;",
        ]

        for cmd in password_commands:
            subprocess.run([mysql_path, "-u", user, db_name, "-e", cmd], check=True)

        print("Database reset successfully!")

    except subprocess.CalledProcessError as e:
        print(f"Error during reset: {e}")
    except Exception as e:
        print(f"General Error: {e}")


if __name__ == "__main__":
    reset()
