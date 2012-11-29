CREATE TABLE posts (
    id BIGSERIAL PRIMARY KEY,
    author bigint REFERENCES users(id),
    title varchar(300) NOT NULL UNIQUE,
    contents varchar,
    draft boolean DEFAULT FALSE
);
