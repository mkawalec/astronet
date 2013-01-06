CREATE TABLE comments (
    id BIGSERIAL PRIMARY KEY,
    string_id varchar(12) NOT NULL UNIQUE,
    author bigint REFERENCES users(id),
    parent varchar REFERENCES comments(string_id),
    post varchar REFERENCES posts(string_id),

    body varchar(1000), -- Is it a good limit?
    timestamp timestamp DEFAULT now()
);
