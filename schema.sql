CREATE TABLE users (
    id INTEGER PRIMARY KEY,
    username TEXT UNIQUE,
    password_hash TEXT
);

CREATE TABLE files (
    id INTEGER PRIMARY KEY,
    filename  TEXT,
    filepath TEXT,
    owner_id INTEGER REFERENCES users,
    public INTEGER
);

CREATE TABLE comments (
    id INTEGER PRIMARY KEY,
    file_id INTEGER REFERENCES files(id),
    user_id INTEGER REFERENCES users(id),
    message TEXT
);