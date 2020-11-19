```mysql
CREATE DATABASE volleyball_gamerecoder;
USE volleyball_gamerecoder

TEE hw2.log
SELECT database();

CREATE TABLE team (
    teamID INTEGER,
    name VARCHAR(30) NOT NULL,
    gender ENUM('m', 'f') NOT NULL DEFAULT 'f',
    PRIMARY KEY (teamID)
);
INSERT INTO team VALUES (1, 'girlteam1', 'f');
INSERT INTO team VALUES (2, 'girlteam2', 'f');
INSERT INTO team VALUES (3, 'girlteam3', 'f');
INSERT INTO team VALUES (4, 'girlteam4', 'f');

CREATE TABLE member (
    teamID INTEGER NOT NULL,
    FOREIGN KEY (teamID) REFERENCES team(teamID) ON DELETE CASCADE ON UPDATE CASCADE,

    IDnumber CHAR(10),
    name VARCHAR(30) NOT NULL,
    degree VARCHAR(100) NOT NULL,
    role ENUM('coach', 'manager', 'newbie', 'spiker', 'blocker', 'setter', 'libero') NOT NULL DEFAULT 'newbie',
    jersey_number TINYINT CHECK (jersey_number > 0 AND jersey_number < 100),
    PRIMARY KEY (IDnumber)
);
INSERT INTO member VALUES (1, 'F123456788', 'Melody', 'univ-dept-1-A12345678', 'blocker', 1);
INSERT INTO member VALUES (2, 'F123456777', 'Jessica', 'univ-dept-4-B87654321', 'coach', DEFAULT);
INSERT INTO member VALUES (3, 'F123456666', 'Silvia', 'univ-dept-3-C11111111', 'setter', 11);
INSERT INTO member VALUES (4, 'F123455555', 'Kathy', 'univ-dept-2-D99999999', 'spiker', 2);

CREATE TABLE competition (
    name VARCHAR(30),
    date DATE NOT NULL CHECK (date >= DATE'2018-1-1'),
    site VARCHAR(30) NOT NULL DEFAULT 'univ',
    PRIMARY KEY (name)
);
INSERT INTO competition VALUES ('2018-competition1', DATE'2018-1-1', DEFAULT);
INSERT INTO competition VALUES ('2018-competition2', DATE'2018-2-2', DEFAULT);
INSERT INTO competition VALUES ('2018-competition3', DATE'2018-3-3', DEFAULT);

CREATE TABLE game (
    competitionID VARCHAR(30) NOT NULL,
    FOREIGN KEY (competitionID) REFERENCES competition(name) ON DELETE CASCADE ON UPDATE CASCADE,
    teamID_1 INTEGER NOT NULL,
    FOREIGN KEY (teamID_1) REFERENCES team(teamID) ON DELETE CASCADE ON UPDATE CASCADE,
    teamID_2 INTEGER NOT NULL,
    FOREIGN KEY (teamID_2) REFERENCES team(teamID) ON DELETE CASCADE ON UPDATE CASCADE,

    gameID INTEGER,
    start_time TIME NOT NULL,
    court INTEGER NOT NULL,
    set_number TINYINT NOT NULL DEFAULT 3 CHECK (set_number >= 1 AND set_number <= 5),
    PRIMARY KEY (gameID)
);
INSERT INTO game VALUES ('2018-competition1', 1, 2, 1, TIME'13:00:00', 1, DEFAULT);
INSERT INTO game VALUES ('2018-competition1', 3, 4, 2, TIME'13:00:00', 2, DEFAULT);
INSERT INTO game VALUES ('2018-competition1', 1, 3, 3, TIME'15:00:00', 1, DEFAULT);
INSERT INTO game VALUES ('2018-competition1', 2, 4, 4, TIME'15:00:00', 2, DEFAULT);

CREATE TABLE record (
    gameID INTEGER NOT NULL,
    FOREIGN KEY (gameID) REFERENCES game(gameID) ON DELETE CASCADE ON UPDATE CASCADE,

    ballID VARCHAR(30) NOT NULL,
    scorer CHAR(10) NOT NULL,
    cause ENUM('ace', 'attack', 'block', 'set', 'tip') NOT NULL DEFAULT 'attack',
    PRIMARY KEY (gameID, ballID)
);
INSERT INTO record VALUES (1, '1-0-1', 'F123456788', 'block');
INSERT INTO record VALUES (2, '1-1-1', 'F123455555', 'ace');
INSERT INTO record VALUES (3, '1-1-1', 'F123456666', 'set');
INSERT INTO record VALUES (4, '1-0-1', 'F123456788', DEFAULT);

CREATE TABLE enroll(
    competitionID VARCHAR(30) NOT NULL,
    teamID INTEGER NOT NULL,
    FOREIGN KEY (competitionID) REFERENCES competition(name) ON DELETE CASCADE ON UPDATE CASCADE,
    FOREIGN KEY (teamID) REFERENCES team(teamID) ON DELETE CASCADE ON UPDATE CASCADE
);
INSERT INTO enroll VALUES ('2018-competition1', 1);
INSERT INTO enroll VALUES ('2018-competition1', 2);
INSERT INTO enroll VALUES ('2018-competition1', 3);
INSERT INTO enroll VALUES ('2018-competition1', 4);
INSERT INTO enroll VALUES ('2018-competition2', 1);
INSERT INTO enroll VALUES ('2018-competition2', 2);
INSERT INTO enroll VALUES ('2018-competition2', 3);
INSERT INTO enroll VALUES ('2018-competition2', 4);
INSERT INTO enroll VALUES ('2018-competition3', 1);
INSERT INTO enroll VALUES ('2018-competition3', 2);
INSERT INTO enroll VALUES ('2018-competition3', 3);
INSERT INTO enroll VALUES ('2018-competition3', 4);

CREATE TABLE depend(
    gameID_early INTEGER NOT NULL,
    gameID_late INTEGER NOT NULL,
    FOREIGN KEY (gameID_early) REFERENCES game(gameID) ON DELETE CASCADE ON UPDATE CASCADE,
    FOREIGN KEY (gameID_late) REFERENCES game(gameID) ON DELETE CASCADE ON UPDATE CASCADE
);
INSERT INTO depend VALUES (1, 2);
INSERT INTO depend VALUES (2, 3);
INSERT INTO depend VALUES (3, 4);

SHOW TABLES FROM volleyball_gamerecoder;
SHOW CREATE TABLE team;
SELECT * FROM team;
SHOW CREATE TABLE member;
SELECT * FROM member;
SHOW CREATE TABLE competition;
SELECT * FROM competition;
SHOW CREATE TABLE game;
SELECT * FROM game;
SHOW CREATE TABLE record;
SELECT * FROM record;
SHOW CREATE TABLE enroll;
SELECT * FROM enroll;
SHOW CREATE TABLE depend;
SELECT * FROM depend;
NOTEE
```

