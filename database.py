#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sun Feb  2 11:02:47 2020

@author: fabian
"""

import pymysql


def get_project_last_run_number(project):
    connection = pymysql.connect(host='localhost',
                             user='anon',
                             password='@Patata23',
                             db='clustomics',
                             charset='utf8mb4',
                             cursorclass=pymysql.cursors.DictCursor)
    sql = "SELECT * from project_result WHERE project_name=%s"
    with connection.cursor() as cursor:
        cursor.execute(sql, (project, ))
        result = tuple(cursor)
    connection.close()
    result = tuple(value['id_result'] for value in result)
    print(result)
    max_ = max(result)
    return max_

def get_project_ids(project, ID):
    connection = pymysql.connect(host='localhost',
                             user='anon',
                             password='@Patata23',
                             db='clustomics',
                             charset='utf8mb4',
                             cursorclass=pymysql.cursors.DictCursor)
    sql = "SELECT id_result from project_result WHERE project_name=%s"
    with connection.cursor() as cursor:
        cursor.execute(sql, (project, ))
        result = tuple(cursor)
    connection.close()
    result = tuple(value['id_result'] for value in result if value['id_result'] != str(ID)) #Eliminamos el id que es de la run actual para no compararlo con sigo mismo
    return result

def get_info_from_project(project_name):
    connection = pymysql.connect(host='localhost',
                             user='anon',
                             password='@Patata23',
                             db='clustomics',
                             charset='utf8mb4',
                             cursorclass=pymysql.cursors.DictCursor)
    sql = "SELECT * from projects WHERE project_name=%s"
    with connection.cursor() as cursor:
        cursor.execute(sql, (project_name, ))
        result = tuple(cursor)
    connection.close()
    return result
    pass

def get_id_from_project(project, user):
    connection = pymysql.connect(host='localhost',
                             user='anon',
                             password='@Patata23',
                             db='clustomics',
                             charset='utf8mb4',
                             cursorclass=pymysql.cursors.DictCursor)
    sql = "SELECT id_project, group_name from projects WHERE project_name=%s AND user=%s"
    with connection.cursor() as cursor:
        cursor.execute(sql, (project, user))
        result = tuple(cursor)
    connection.close()
    return result
    pass
    

def get_info_from_user(user):
    pass

def get_result_from_project(id_project):
    connection = pymysql.connect(host='localhost',
                             user='anon',
                             password='@Patata23',
                             db='clustomics',
                             charset='utf8mb4',
                             cursorclass=pymysql.cursors.DictCursor)
    sql = "SELECT * from project_result WHERE project_name=%s"
    with connection.cursor() as cursor:
        cursor.execute(sql, (id_project, ))
        result = tuple(cursor)
    connection.close()
    return result

def create_new_project(user, name, group):
    connection = pymysql.connect(host='localhost',
                             user='anon',
                             password='@Patata23',
                             db='clustomics',
                             charset='utf8mb4',
                             cursorclass=pymysql.cursors.DictCursor)
    path = "%s_data" % (name)
    sql = "INSERT INTO projects (project_name, user, group_name, file_path) VALUES ( %s, %s, %s, %s);"
    # If mirando si ese project name esta cogido ya para su user o su grupo
    with connection.cursor() as cursor:
        cursor.execute(sql, (name, user, group, path))
    connection.commit()
    connection.close()
    print('New project created successfully')
    return 0
        
def create_new_user():
    pass

def get_user_info(user):
    connection = pymysql.connect(host='localhost',
                             user='anon',
                             password='@Patata23',
                             db='clustomics',
                             charset='utf8mb4',
                             cursorclass=pymysql.cursors.DictCursor)
    with connection.cursor() as cursor:
        sql = 'SELECT email FROM user_info where username=%s;'
        cursor.execute(sql, (user, ))
        result = tuple(cursor)
    connection.close()
    return result


def get_groups_of_user(user):
    sql = "SELECT group_name FROM member_group WHERE username=%s;"
    connection = pymysql.connect(host='localhost',
                             user='anon',
                             password='@Patata23',
                             db='clustomics',
                             charset='utf8mb4',
                             cursorclass=pymysql.cursors.DictCursor)
    with connection.cursor() as cursor:
        cursor.execute(sql, (user, ))
        result = list(cursor)
    connection.close()
    return result

def get_group_info():
    pass

def save_result(id_, project, score, date_time, algorithm, groups,
                 distance, linkage, group_name, user, path):
    connection = pymysql.connect(host='localhost',
                             user='anon',
                             password='@Patata23',
                             db='clustomics',
                             charset='utf8mb4',
                             cursorclass=pymysql.cursors.DictCursor)
    if (group_name is None): group_name = 'NULL'
    sql = 'INSERT INTO project_result (id_project, project_name, validation_result, date_time, algo_rithm, groups, distance, linkage, group_name, user, path) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)'
    with connection.cursor() as cursor:
        cursor.execute(sql, (id_, project, score, date_time, algorithm, groups, 
                             distance, 
                             linkage, 
                             group_name, 
                             user, 
                             path ))
    connection.commit()
    connection.close()
    pass

def get_user_result(datetime, user, projecy):
    connection = pymysql.connect(host='localhost',
                             user='anon',
                             password='@Patata23',
                             db='clustomics',
                             charset='utf8mb4',
                             cursorclass=pymysql.cursors.DictCursor)
    sql = "SELECT * FROM project_result where username=%s AND project;"
    with connection.cursor() as cursor:
        cursor.execute(sql, (user, ))
        result = tuple(cursor)
    connection.close()
    return result
    pass

def get_projects_from_user(user):
    connection = pymysql.connect(host='localhost',
                             user='anon',
                             password='@Patata23',
                             db='clustomics',
                             charset='utf8mb4',
                             cursorclass=pymysql.cursors.DictCursor)
    groups = get_groups_of_user(user)
    member_of = list()
    sql = 'SELECT * FROM projects WHERE user=%s'
    for group in groups:
        member_of.append(group['group_name'])
        sql += ' OR group_name=%s'
    sql += ";"
    with connection.cursor() as cursor:
        cursor.execute(sql, (user, *member_of, ))
        result = cursor.fetchall()
    connection.close()
    return tuple(result)

def get_run_results(id_project):
    connection = pymysql.connect(host='localhost',
                             user='anon',
                             password='@Patata23',
                             db='clustomics',
                             charset='utf8mb4',
                             cursorclass=pymysql.cursors.DictCursor)
    sql = 'SELECT * FROM project_result WHERE id_result=%s order  by date_time'
    with connection.cursor() as cursor:
        cursor.execute(sql, (id_project ))
        result = tuple(cursor)
    print(result)
    connection.close()
    return result

def delete_project():
    pass

def _is_admin(user_name, group_name):
    connection = pymysql.connect(host='localhost',
                             user='anon',
                             password='@Patata23',
                             db='clustomics',
                             charset='utf8mb4',
                             cursorclass=pymysql.cursors.DictCursor)
    sql = 'SELECT admin FROM member_group WHERE user=%s AND group_name=%s'
    with connection.cursor() as cursor:
        cursor.execute(sql, (user_name, group_name ))
        result = tuple(cursor)
    connection.close()
    return result

def abandon_group(user_name, group_name):
    connection = pymysql.connect(host='localhost',
                             user='anon',
                             password='@Patata23',
                             db='clustomics',
                             charset='utf8mb4',
                             cursorclass=pymysql.cursors.DictCursor)
    sql = 'DELETE FROM member_group WHERE user=%s AND group=%s;'
    with connection.cursor() as cursor:
        cursor.execute(sql, (user_name, group_name ))
    connection = pymysql.connect(host='localhost',
                             user='anon',
                             password='@Patata23',
                             db='clustomics',
                             charset='utf8mb4',
                             cursorclass=pymysql.cursors.DictCursor)