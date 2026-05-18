import subprocess
import os


def populate_test_data():
    mysql_path = r"c:/xampp/mysql/bin/mysql.exe"  # TODO: make portable
    user = "root"
    db_name = "university"
    script_path = os.path.join(
        os.path.dirname(__file__), "TestData.sql"
    )  # TODO: make portable

    try:
        print("Inserting test data into db...")
        shell_command = f'type "{script_path}" | "{mysql_path}" -u {user} {db_name}'

        subprocess.run(shell_command, shell=True, check=True)

        print("✅ Database filled with data successfully!")

    except subprocess.CalledProcessError as e:
        print(f"❌ Error during data population: {e}")
    except Exception as e:
        print(f"❌ General Error: {e}")


if __name__ == "__main__":
    populate_test_data()
