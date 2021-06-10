import pathlib
import sqlite3

from docker_test.settings import config


def run_sql_script(name):
    db_loc = pathlib.Path(config["sqlite"]["file"])

    if not db_loc.parent.is_dir():
        db_loc.parent.mkdir()

    conn = sqlite3.connect(db_loc)

    with open(f"sql_scripts/{name}.sql") as f:
        sql_script = f.read()

    conn.executescript(sql_script)
    conn.commit()

    conn.close()


def init_db_with_sample_data():
    run_sql_script("drop_db")
    run_sql_script("init_db")
    run_sql_script("sample_data")


if __name__ == "__main__":
    init_db_with_sample_data()
