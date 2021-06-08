CREATE TABLE question (
    id INTEGER PRIMARY KEY,
    question_text TEXT NOT NULL,
    pub_date TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE choice (
    id INTEGER PRIMARY KEY,
    choice_text TEXT NOT NULL,
    votes INTEGER DEFAULT 0,
    question_id INTEGER,
    FOREIGN KEY (question_id) REFERENCES question(id) ON DELETE CASCADE
);
