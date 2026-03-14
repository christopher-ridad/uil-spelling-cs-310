USE sys;


DROP DATABASE IF EXISTS spellingapp;
CREATE DATABASE spellingapp;


USE spellingapp;


DROP TABLE IF EXISTS user_history;
DROP TABLE IF EXISTS words;
DROP TABLE IF EXISTS users;


CREATE TABLE words
(
    word_id      int not null AUTO_INCREMENT,
    word         varchar(100) not null,
    definition   TEXT,
    created_at   TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (word_id),
    UNIQUE      (word)
);


CREATE TABLE users
(
    user_id      int not null AUTO_INCREMENT,
    username     varchar(50) not null,
    created_at   TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY  (user_id),
    UNIQUE       (username)
);


CREATE TABLE user_history
(
    row_id            int not null AUTO_INCREMENT,
    user_id           int not null,
    word_id           int not null,
    correct           int DEFAULT 0,
    total_attempts    int DEFAULT 0,
    last_seen         TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    created_at        TIMESTAMP DEFAULT CURRENT_TIMESTAMP, 
    PRIMARY KEY (row_id),
    FOREIGN KEY (user_id) REFERENCES users(user_id),
    FOREIGN KEY (word_id) REFERENCES words(word_id),
    UNIQUE (user_id, word_id)
);


CREATE USER 'app_user' IDENTIFIED BY 'password123';


GRANT SELECT, INSERT, UPDATE, DELETE
ON spellingapp.*
TO 'app_user';


FLUSH PRIVILEGES;
