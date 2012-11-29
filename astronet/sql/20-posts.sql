CREATE TABLE posts (
    id BIGSERIAL PRIMARY KEY,
    author bigint REFERENCES users(id),
    title varchar(300) NOT NULL UNIQUE,
    lead varchar(500) NOT NULL UNIQUE,
    body varchar,
    draft boolean DEFAULT FALSE,

    timestamp timestamp DEFAULT now()
);
