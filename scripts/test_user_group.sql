USE clustomics;

INSERT INTO user_info (username, email, password) VALUES ('test_user', 'test@clustomics.com', '35bc8cec895861697a0243c1304c7789'); 
INSERT INTO groups (group_name, max_users_number) VALUES('test_group', 8);
INSERT INTO groups (group_name, max_users_number) VALUES('test_group2', 8);

INSERT INTO member_group (username, group_name, admin) VALUES ('test_user', 'test_group', true);
INSERT INTO member_group (username, group_name, admin) VALUES ('adria', 'test_group2', true);

INSERT INTO projects (group_name, user, project_name, file_path) VALUES ('test_group', 'test_user', 'test_project','1afs.csv');
INSERT INTO projects (group_name, user, project_name, file_path) VALUES ('test_group2', 'adria', 'test_for2','1afas.csv');

INSERT INTO project_result (project_name, validation_result, date, user, algorithm, distance, groups );

INSERT INTO projects (group_name, user, project_name, file_path) VALUES ( NULL, 'adria','Monster_Hunter','mnt.csv');
