CREATE DATABASE clustomics;

USE clustomics;

CREATE TABLE user_info (
    username VARCHAR(15) PRIMARY KEY NOT NULL UNIQUE,
    email VARCHAR(100) NOT NULL UNIQUE,
    password VARCHAR(32) 
	);
    
CREATE TABLE groups (
    group_name VARCHAR(40) PRIMARY KEY NOT NULL UNIQUE,
    max_users_number INT DEFAULT 8
	);
    
CREATE TABLE member_group (
	username VARCHAR(15),
    group_name VARCHAR(40),
    admin BOOLEAN default false
	);
    
CREATE TABLE projects(
    id_project INT NOT NULL PRIMARY KEY AUTO_INCREMENT,
    description VARCHAR(500),
    group_name VARCHAR(40),
    user VARCHAR(15),
    project_name VARCHAR(50),
    file_path VARCHAR(45),
    rowname BOOLEAN default false,
    colname BOOLEAN default false,
    sep VARCHAR(10)
	);
    
CREATE TABLE project_result(
    id_result INT NOT NULL PRIMARY KEY AUTO_INCREMENT,
    id_project INT,	
    project_name VARCHAR(50),
    validation_result FLOAT,
    date_time CHAR(20),
    algo_rithm INT,
    groups INT, 
    distance VARCHAR(25),
    linkage VARCHAR(25),
    group_name VARCHAR(40),
    user VARCHAR(15),
    path VARCHAR(15)
	);

INSERT INTO projects (description, group_name, user, project_name, file_path)values ('Demo project for unregistered users', 'Demo_group', 'Demo_user','Demo_project', 'Demo_path');
