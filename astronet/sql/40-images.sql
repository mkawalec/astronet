CREATE TABLE images (
    id BIGSERIAL PRIMARY KEY,
    author bigint REFERENCES users(id),
    title varchar(300) NOT NULL,
    source varchar(600) NOT NULL, -- Increased the size, 
    -- remember we will deal with google maps links:D
    description varchar(500) NOT NULL, -- The description doesn't need to be unique
    body varchar,


    string_id varchar(12) NOT NULL UNIQUE, -- 'dorosły' obrazek
    timestamp timestamp DEFAULT now()
);
