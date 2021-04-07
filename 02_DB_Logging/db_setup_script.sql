/* DB Setup Football Logging Server */

/* 
Setup on raspberry pi logging server

1.	sudo apt-get install mariadb-server

2.	in file /etc/mysql/mariadb.conf.d/50-server.cnf
	modify bind-address = 127.0.0.1 to bind-address = 0.0.0.0
	in order to activate access from remote clients
	
Useful aliases:
	- db_start
	- db_stop
	- db_restart
	- db_status
	
	
Setup on rasperry pi logging clients

1. sudo apt-get install -y libmariadb-dev
2. sudo pip3 install mariadb
*/

CREATE DATABASE football;

CREATE USER 'server'@'localhost' IDENTIFIED BY 'password';
CREATE USER 'manfred'@'localhost' IDENTIFIED BY 'password';
CREATE USER 'fattuesday'@'localhost' IDENTIFIED BY 'password';
CREATE USER 'bob'@'localhost' IDENTIFIED BY 'password';
CREATE USER 'timo'@'localhost' IDENTIFIED BY 'password';

GRANT ALL ON football.* to 'server'@'192.168.%' IDENTIFIED BY 'password' WITH GRANT OPTION;
GRANT ALL ON football.* to 'manfred'@'192.168.%' IDENTIFIED BY 'password' WITH GRANT OPTION;
GRANT ALL ON football.* to 'fattuesday'@'192.168.%' IDENTIFIED BY 'password' WITH GRANT OPTION;
GRANT ALL ON football.* to 'bob'@'192.168.%' IDENTIFIED BY 'password' WITH GRANT OPTION;
GRANT ALL ON football.* to 'timo'@'192.168.%' IDENTIFIED BY 'password' WITH GRANT OPTION;



CREATE TABLE football.game_data (
  id int(11) NOT NULL AUTO_INCREMENT,
  time float NOT NULL,
  player_id int(3) NOT NULL,
  mate_id int(3) NOT NULL,
  team_id int(3) NOT NULL,
  decision varchar(255),
  decision_count int(10),
  goal_team_1 int(3) NOT NULL,
  goal_team_2 int(3) NOT NULL,
  goal_1_post_1_x float NOT NULL,
  goal_1_post_1_y float NOT NappULL,
  goal_1_post_2_x float NOT NULL,
  goal_1_post_2_y float NOT NULL,
  goal_2_post_1_x float NOT NULL,
  goal_2_post_1_y float NOT NULL,
  goal_2_post_2_x float NOT NULL,
  goal_2_post_2_y float NOT NULL,
  player_1_x float NOT NULL,
  player_1_y float NOT NULL,
  player_1_alpha float NOT NULL,
  player_2_x float NOT NULL,
  player_2_y float NOT NULL,
  player_2_alpha float NOT NULL,
  player_3_x float NOT NULL,
  player_3_y float NOT NULL,
  player_3_alpha float NOT NULL,
  player_4_x float NOT NULL,
  player_4_y float NOT NULL,
  player_4_alpha float NOT NULL,
  ball_x float NOT NULL,
  ball_y float NOT NULL,
  time_stamp timestamp DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (id)
)
ENGINE = INNODB,
COMMENT = 'game_data table which stores all relevant data which led to players decision';


/*
CREATE OR REPLACE TRIGGER football.game_data_set_game_id
BEFORE INSERT ON football.game_data
FOR EACH ROW
  BEGIN
  SELECT IFNULL(MAX(game_id), 1) FROM football.game_data INTO @max_game_id;
  SELECT IFNULL((SELECT time from football.game_data g WHERE g.time_stamp = (SELECT MAX(g1.time_stamp) FROM football.game_data g1 WHERE g1.player_id = NEW.player_id)), 0) INTO @max_time;

  IF NEW.time < @max_time THEN
    SET NEW.game_id = @max_game_id + 1;
  ELSE
    SET NEW.game_id = @max_game_id;
  END IF;
  END;
  * /
