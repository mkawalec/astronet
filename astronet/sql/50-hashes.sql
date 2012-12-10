CREATE TABLE hashes(
    id BIGSERIAL PRIMARY KEY,
    hash_value varchar(10),
    owner bigint REFERENCES users(id),
    timestamp timestamp DEFAULT now()
);