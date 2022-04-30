CREATE DATABASE shopping;
CREATE TABLE shopping.list (
id int AUTO_INCREMENT PRIMARY KEY,
description char(200),
notes char(100),
ticked bool default FALSE
);

INSERT INTO shopping.list VALUES 
(NULL, "Bagels", "Plain, of course.", NULL);

INSERT INTO shopping.list VALUES
(NULL, "Jelly", "Grape, please!", NULL);

INSERT INTO shopping.list VALUES
(NULL, "Milk", "2%", True);

INSERT INTO shopping.list VALUES
(NULL, "Lunch meat", "Suprise me.", NULL);

INSERT INTO shopping.list VALUES
(NULL, "Paper towels", "", NULL);
