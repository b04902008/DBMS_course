```mysql
CREATE DATABASE volleyball_gamerecoder;
USE volleyball_gamerecoder

################################
CREATE TABLE team (
    teamID INTEGER,
    name VARCHAR(30) NOT NULL,
    gender ENUM('m', 'f') NOT NULL DEFAULT 'f',
    PRIMARY KEY (teamID)
);
INSERT INTO team VALUES (1, 'girlteam1', 'f');
INSERT INTO team VALUES (2, 'boyteam1', 'm');
INSERT INTO team VALUES (3, 'girlteam2', 'f');
INSERT INTO team VALUES (4, 'boyteam2', 'm');

################################
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
INSERT INTO member VALUES (1, 'F123456788', 'Melody', 'univ-dept-2', 'blocker', 1);
INSERT INTO member VALUES (1, 'F123456777', 'Jessica', 'univ-dept-4', 'coach', NULL);
INSERT INTO member VALUES (1, 'F123456666', 'Silvia', 'univ-dept-3', 'setter', 11);
INSERT INTO member VALUES (1, 'F123455555', 'Kathy', 'univ-dept-2', 'spiker', 2);
INSERT INTO member VALUES (1, 'F123456789', 'Monica', 'univ-dept-2', 'manager', NULL);
INSERT INTO member VALUES (1, 'F123333333', 'Richie', 'univ-dept-2', 'manager', NULL);
INSERT INTO member VALUES (2, 'F122222222', 'Charles', 'univ-dept-2', 'spiker', 16);
INSERT INTO member VALUES (2, 'F111111111', 'Paula', 'univ-dept-1', 'manager', NULL);

################################
CREATE TABLE competition (
    name VARCHAR(30),
    date DATE NOT NULL CHECK (date >= DATE'2018-1-1'),
    site VARCHAR(30) NOT NULL DEFAULT 'univ',
    fee INTEGER NOT NULL,
    PRIMARY KEY (name)
);
INSERT INTO competition VALUES ('2018-hsiao-nei-carnival', DATE'2018-1-1', DEFAULT, 3800);
INSERT INTO competition VALUES ('2018-da-zi-bei', DATE'2018-2-2', DEFAULT, 3000);
INSERT INTO competition VALUES ('2018-da-dian-bei', DATE'2018-3-3', DEFAULT, 3000);
INSERT INTO competition VALUES ('2018-hsiao-wai-bei', DATE'2018-4-4', DEFAULT, 1200);

################################
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
INSERT INTO game VALUES ('2018-hsiao-nei-carnival', 1, 2, 1, TIME'13:00:00', 1, DEFAULT);
INSERT INTO game VALUES ('2018-hsiao-nei-carnival', 3, 4, 2, TIME'13:00:00', 2, DEFAULT);
INSERT INTO game VALUES ('2018-hsiao-nei-carnival', 1, 3, 3, TIME'14:00:00', 1, DEFAULT);
INSERT INTO game VALUES ('2018-hsiao-nei-carnival', 2, 4, 4, TIME'14:00:00', 2, DEFAULT);
INSERT INTO game VALUES ('2018-hsiao-nei-carnival', 1, 4, 5, TIME'15:00:00', 1, DEFAULT);
INSERT INTO game VALUES ('2018-hsiao-nei-carnival', 2, 3, 6, TIME'15:00:00', 2, DEFAULT);

################################
CREATE TABLE record (
    gameID INTEGER NOT NULL,
    FOREIGN KEY (gameID) REFERENCES game(gameID) ON DELETE CASCADE ON UPDATE CASCADE,

    ballID VARCHAR(30) NOT NULL,
    scorer CHAR(10) NOT NULL,
    cause ENUM('ace', 'attack', 'block', 'set', 'tip') NOT NULL DEFAULT 'attack',
    PRIMARY KEY (gameID, ballID)
);
INSERT INTO record VALUES (1, '1-0-1', 'F123456788', 'block');
INSERT INTO record VALUES (1, '1-0-2', 'F123455555', 'ace');
INSERT INTO record VALUES (1, '1-0-3', 'F123456666', 'set');
INSERT INTO record VALUES (1, '1-0-4', 'F123456788', 'attack');
INSERT INTO record VALUES (1, '1-1-1', 'F122222222', 'attack');
INSERT INTO record VALUES (3, '1-0-1', 'F123456788', 'ace');
INSERT INTO record VALUES (3, '1-0-2', 'F123444444', 'ace');

################################
CREATE TABLE enroll(
    competitionID VARCHAR(30) NOT NULL,
    teamID INTEGER NOT NULL,
    FOREIGN KEY (competitionID) REFERENCES competition(name) ON DELETE CASCADE ON UPDATE CASCADE,
    FOREIGN KEY (teamID) REFERENCES team(teamID) ON DELETE CASCADE ON UPDATE CASCADE
);
INSERT INTO enroll VALUES ('2018-hsiao-nei-carnival', 1);
INSERT INTO enroll VALUES ('2018-hsiao-nei-carnival', 2);
INSERT INTO enroll VALUES ('2018-hsiao-nei-carnival', 3);
INSERT INTO enroll VALUES ('2018-hsiao-nei-carnival', 4);
INSERT INTO enroll VALUES ('2018-da-zi-bei', 1);
INSERT INTO enroll VALUES ('2018-da-zi-bei', 2);
INSERT INTO enroll VALUES ('2018-da-dian-bei', 3);
INSERT INTO enroll VALUES ('2018-da-dian-bei', 4);
INSERT INTO enroll VALUES ('2018-hsiao-wai-bei', 1);
INSERT INTO enroll VALUES ('2018-hsiao-wai-bei', 3);

################################
CREATE TABLE depend(
    gameID_early INTEGER NOT NULL,
    gameID_late INTEGER NOT NULL,
    FOREIGN KEY (gameID_early) REFERENCES game(gameID) ON DELETE CASCADE ON UPDATE CASCADE,
    FOREIGN KEY (gameID_late) REFERENCES game(gameID) ON DELETE CASCADE ON UPDATE CASCADE
);
INSERT INTO depend VALUES (1, 2);
INSERT INTO depend VALUES (2, 3);
INSERT INTO depend VALUES (3, 4);

TEE hw3.log
SELECT database();
SHOW TABLES FROM volleyball_gamerecoder;

# basic select
SELECT *
FROM member
WHERE teamID=1 AND (NOT (role='coach' OR role='manager'));
# basic projection
SELECT name, role
FROM member;
# basic rename
SELECT m.teamID AS team, m.jersey_number, m.name AS player
FROM member AS m
WHERE NOT (m.role='coach' OR m.role='manager')
ORDER BY team, m.jersey_number;

# union
(SELECT teamID, name FROM team)
UNION
(SELECT teamID, name FROM member)
ORDER BY teamID;
# equijoin
SELECT team.name AS team, member.name AS member
FROM team JOIN member ON team.teamID=member.teamID
ORDER BY team;
# natural join
SELECT name AS team, member
FROM team NATURAL JOIN (SELECT teamID, name AS member FROM member) AS m
ORDER BY team;
# theta join
SELECT A.competitionID, A.court, A.gameID AS early_game, B.gameID AS later_game
FROM game as A, game AS B
WHERE A.competitionID=B.competitionID AND A.court=B.court AND A.start_time<B.start_time
ORDER BY A.court, early_game, later_game;

# three table join
SELECT competition.name AS competition, game.gameID AS game, ballID AS ball, scorer
FROM competition, game, record
WHERE competition.name=game.competitionID AND game.gameID=record.gameID
ORDER BY competition, game, ball;
# aggregate (max, min, count)
SELECT team.teamID, COUNT(*) AS member_num, MIN(jersey_number), MAX(jersey_number)
FROM team, member
WHERE team.teamID=member.teamID
GROUP BY team.teamID
ORDER BY team.teamID;
# aggregate (avg, sum, count)
SELECT teamID, COUNT(*) AS competition_num, SUM(fee), AVG(fee)
FROM competition JOIN enroll ON name=competitionID
GROUP BY teamID
ORDER BY teamID;
# in (explicit set value)
SELECT teamID, jersey_number, name AS player, role
FROM member
WHERE role IN ('spiker', 'blocker', 'setter', 'libero')
ORDER BY teamID, jersey_number;
# in (dynamic set value)
SELECT gameID, name AS player, ballID, cause
FROM (record JOIN member ON record.scorer=member.IDnumber)
WHERE scorer in
	(SELECT IDnumber
    FROM member
    WHERE teamID=1);
# correlated nested query (in)
SELECT gameID, ballID, scorer
FROM record
WHERE scorer in
	(SELECT IDnumber
    FROM member
    WHERE role='blocker' AND record.cause='block');
# correlated nested query (exist)
SELECT competitionID, teamID_1, teamID_2
FROM game
WHERE EXISTS
	(SELECT *
    FROM member
    WHERE (teamID=teamID_1 OR teamID=teamID_2) AND NOT (role='coach' OR role='manager'));

# bonus1 (left outer join)
SELECT team.name AS team, member.name AS member
FROM team LEFT OUTER JOIN member ON team.teamID=member.teamID
ORDER BY team;
# bonus2 (full outer join)
(SELECT name, gameID, ballID, cause
FROM member LEFT OUTER JOIN record ON IDnumber=scorer)
UNION
(SELECT name, gameID, ballID, cause
FROM member RIGHT OUTER JOIN record ON IDnumber=scorer);
# bonus3 (having clause)
SELECT teamID, COUNT(*) AS competition_num, SUM(fee), AVG(fee)
FROM competition JOIN enroll ON name=competitionID
GROUP BY teamID
HAVING competition_num>2
ORDER BY teamID;
# bonus4 (not exist)
SELECT competitionID, teamID_1, teamID_2
FROM game
WHERE NOT EXISTS
	(SELECT *
    FROM member
    WHERE (teamID=teamID_1 OR teamID=teamID_2) AND NOT (role='coach' OR role='manager'));
NOTEE
```

