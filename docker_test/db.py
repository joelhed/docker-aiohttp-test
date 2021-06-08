import aiosqlite


def create_connection(app):
    file_loc = app["config"]["sqlite"]["file"]
    return aiosqlite.connect(file_loc)
