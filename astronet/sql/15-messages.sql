CREATE TABLE messages (
    id BIGSERIAL PRIMARY KEY,
    string_id varchar(12) NOT NULL UNIQUE,
    timestamp timestamp DEFAULT now(),

    source bigint REFERENCES users(id),
    conversation varchar(12),
    message varchar(1000),
    reply_to varchar(12)
);
