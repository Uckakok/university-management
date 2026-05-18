import pytest
import mysql.connector
import subprocess
import os

TEST_DB_NAME = "university_test"


@pytest.fixture(scope="session", autouse=True)
def test_db_setup():
    os.environ["DATABASE_NAME"] = TEST_DB_NAME
    admin_conn = mysql.connector.connect(host="localhost", user="root", password="")
    cursor = admin_conn.cursor()
    cursor.execute(f"DROP DATABASE IF EXISTS {TEST_DB_NAME}")
    cursor.execute(f"CREATE DATABASE {TEST_DB_NAME}")
    cursor.close()
    admin_conn.close()

    script_path = os.path.abspath(
        os.path.join(os.path.dirname(__file__), "..", "SetupScript.sql")
    )
    populate_script_path = os.path.abspath(
        os.path.join(os.path.dirname(__file__), "..", "TestData.sql")
    )
    add_admin_path = os.path.abspath(
        os.path.join(os.path.dirname(__file__), "..", "AddAdmin.sql")
    )
    mysql_path = r"c:/xampp/mysql/bin/mysql.exe"

    shell_command = f'type "{script_path}" | "{mysql_path}" -u root {TEST_DB_NAME}'
    subprocess.run(shell_command, shell=True, check=True)

    new_shell_command = (
        f'type "{populate_script_path}" | "{mysql_path}" -u root {TEST_DB_NAME}'
    )
    subprocess.run(new_shell_command, shell=True, check=True)

    admin_shell_command = (
        f'type "{add_admin_path}" | "{mysql_path}" -u root {TEST_DB_NAME}'
    )
    subprocess.run(admin_shell_command, shell=True, check=True)

    yield

    admin_conn = mysql.connector.connect(host="localhost", user="root", password="")
    cursor = admin_conn.cursor()
    cursor.execute(f"DROP DATABASE {TEST_DB_NAME}")
    cursor.close()
    admin_conn.close()
