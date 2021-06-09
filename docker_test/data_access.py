"""This is a module for the data access layer."""
from sqlite3 import Row


async def get_question_count(conn):
    """Get the number of questions."""
    async with conn.cursor() as cur:
        await cur.execute("SELECT COUNT(*) FROM question;")
        question_count, = await cur.fetchone()

    return question_count


async def get_all_questions(conn):
    """Get a list of all questions."""
    conn.row_factory = Row

    async with conn.cursor() as cur:
        await cur.execute("SELECT * FROM question;")
        data = await cur.fetchall()
        questions = [dict(row) for row in data]

    return questions


async def create_question(conn, question_text, choices):
    """Create a question.

    Returns the id of the newly created question.
    """
    async with conn.cursor() as cur:
        await cur.execute(
            "INSERT INTO question (question_text) VALUES (?);",
            (question_text, )
        )
        question_id = cur.lastrowid

        await cur.executemany(
            "INSERT INTO choice (choice_text, question_id) VALUES (?, ?);",
            [(choice_text, question_id) for choice_text in choices],
        )

        await conn.commit()

    return question_id


async def get_question(conn, question_id):
    """Get a question by id."""
    conn.row_factory = Row

    async with conn.cursor() as cur:
        cur = await cur.execute("SELECT * FROM question WHERE id=?", (question_id, ))
        res = await cur.fetchone()
        question = dict(res) if res is not None else None

    return question


async def get_choices(conn, question_id):
    """Get all choices of a question by the question id."""
    conn.row_factory = Row

    async with conn.cursor() as cur:
        await cur.execute(
            "SELECT id, choice_text, votes FROM choice WHERE question_id=?",
            (question_id, )
        )
        res = await cur.fetchall()
        choices = [dict(choice) for choice in res]

    return choices


async def get_question_with_choices(conn, question_id):
    """Get a question with all its choices by id."""
    question = await get_question(conn, question_id)

    if question is not None:
        choices = await get_choices(conn, question_id)
        question["choices"] = choices

    return question


async def get_vote_count(conn, question_id):
    """Get the total amount of votes on a given question."""
    # This is not actually used currently, since it's faster, i.e. saves io, to do it in the
    # application code rather than in the database. -- 2021-06-09
    async with conn.cursor() as cur:
        await cur.execute("SELECT SUM(votes) FROM choice WHERE question_id=?;", (question_id, ))
        vote_count, = await cur.fetchone()

    return vote_count


async def get_choice(conn, question_id, choice_id):
    """Get a choice by question and choice id."""
    conn.row_factory = Row

    async with conn.cursor() as cur:
        await cur.execute(
            "SELECT * FROM choice WHERE question_id=? AND id=?;",
            (question_id, choice_id),
        )
        res = await cur.fetchone()
        choice = dict(res) if res is not None else None

    return choice


async def vote_on_choice(conn, question_id, choice_id):
    """Vote on the choice of the question, by question and choice id.

    Returns nothing, regardless of whether the action works or not, in the case that the
    choice doesn't exists on the given question.
    """
    async with conn.cursor() as cur:
        await cur.execute(
            "UPDATE choice SET votes = votes + 1 WHERE question_id=? AND id=?;",
            (question_id, choice_id),
        )

    await conn.commit()
