CREATE TABLE users (
    id BIGSERIAL PRIMARY KEY,
    string_id varchar(12) NOT NULL UNIQUE,
    -- User email - some additional constraints here
    email varchar(50) UNIQUE,
    -- The 'real' name of the user
    real_name varchar(50) DEFAULT 'None',
    -- User password
    passwd varchar,
    -- Salt, user-variable
    salt varchar(12), 
    disabled boolean DEFAULT FALSE,
    -- This will define user's role
    role varchar(10) DEFAULT 'user',

    timestamp timestamp DEFAULT now()
);
