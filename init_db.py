import sqlite3

from docker_test.settings import config


def run_sql_script(name):
    db_loc = config["sqlite"]["file"]
    conn = sqlite3.connect(db_loc)

    with open(f"sql_scripts/{name}.sql") as f:
        sql_script = f.read()

    conn.executescript(sql_script)
    conn.commit()

    conn.close()


if __name__ == "__main__":
    run_sql_script("drop_db")
    run_sql_script("init_db")
    run_sql_script("sample_data")
