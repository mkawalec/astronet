CREATE TABLE users (
    id BIGSERIAL PRIMARY KEY,
    -- User email - some additional constraints here
    email varchar(50) UNIQUE,
    -- The 'real' name of the user
    real_name varchar(50),
    -- User password
    passwd varchar,
    -- Salt, user-variable
    salt varchar(10), 
    disabled boolean DEFAULT FALSE,
    -- This will define user's role
    role varchar(5) DEFAULT 'user',

    timestamp timestamp DEFAULT now()
);

ALTER TABLE users ADD reset_hash varchar(10);
ALTER TABLE users ADD string_id varchar(12);
