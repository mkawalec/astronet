CREATE TABLE images (
    id BIGSERIAL PRIMARY KEY,
    author bigint REFERENCES users(id),
    title varchar(300) NOT NULL,
    source varchar(300) NOT NULL,
    description varchar(500) NOT NULL UNIQUE, --?
    body varchar,


    string_id varchar(12) NOT NULL UNIQUE, -- 'dorosły' obrazek
    string_min_id varchar(12) NOT NULL UNIQUE, -- minaturka
    timestamp timestamp DEFAULT now()
);
