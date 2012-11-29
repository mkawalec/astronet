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
    -- Default locale for the user
    -- Will be used for specifying search locale
    locale varchar(10) DEFAULT 'pl',
    -- This will define user's role
    role varchar(5) DEFAULT 'user'
);
