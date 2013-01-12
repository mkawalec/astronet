CREATE TABLE messages (
    id BIGSERIAL PRIMARY KEY,
    timestamp timestamp DEFAULT now(),

    source bigint REFERENCES users(id),
    target bigint REFERENCES users(id),
    conversation varchar(12),
    message varchar(1000)
);
