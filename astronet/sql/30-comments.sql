CREATE TABLE comments (
    id BIGSERIAL PRIMARY KEY,
    string_id varchar(12) NOT NULL UNIQUE,
    author bigint REFERENCES users(id),
    parent bigint REFERENCES comments(id),
    post bigint REFERENCES posts(id),

    body varchar(1000) -- Is it a good limit?
)
