CREATE TABLE reports(
    id BIGSERIAL PRIMARY KEY,
    author bigint REFERENCES users(id),
    type varchar(20), --typo, link not active, lie, grammar...

    body varchar,
    done boolean DEFAULT FALSE,

    string_id varchar(12) NOT NULL UNIQUE,
    timestamp timestamp DEFAULT now(),
    deleted boolean DEFAULT FALSE,
);
