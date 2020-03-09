# -*- coding: utf-8 -*-

from flask import Flask, render_template, request, redirect, url_for, session, send_file
import datetime as dt

import os
import os.path
import database
import clustering
import pymysql
import pandas as pd 
import plotly.io as pio
import re
import hashlib
import zipfile


algs = {0: 'K-means', 
        1:'Hierarchichal'}

app = Flask(__name__)
app.config['SEND_FILE_MAX_AGE_DEFAULT'] = 0
app.config['UPLOAD_FOLDER'] = 'projects_data'

app.secret_key= 'asd'

connection = pymysql.connect(host='localhost',
                             user='anon',
                             password='@Patata23',
                             db='clustomics',
                             charset='utf8mb4',
                             cursorclass=pymysql.cursors.DictCursor)


@app.route('/')
def clustomics():
    if 'loggedin' in session:
        return render_template('index.html', logged=True)
    return render_template('index.html', logged=False)

@app.route('/login', methods=['GET', 'POST'])
def login():
    # Output message if something goes wrong...
    msg = ''
    # Check if "username" and "password" POST requests exist (user submitted form)
    if request.method == 'POST' and 'email' in request.form and 'password' in request.form:
        # Create variables for easy access
        email = request.form['email']
        password = request.form['password']
        password = hashlib.md5(password.encode('ascii')).hexdigest()
        # Check if account exists using MySQL
        with connection.cursor() as cursor:
            # Read a single record
            sql = "SELECT * FROM user_info WHERE email = %s AND password = %s"
            cursor.execute(sql, (email,password))
            #connection.commit()        
            account = cursor.fetchone()
            # If account exists in user_info table in out database
            if account:
                # Create session data, we can access this data in other routes
                session['loggedin'] = True
                session['email'] = account['email']
                session['username'] = account['username']
                # Redirect to home page
                return redirect(url_for('projects', user=account['username']))
            else:
                # Account doesnt exist or username/password incorrect
                msg = 'Incorrect email/password!'    
   
    return render_template('login.html', msg=msg)


@app.route('/delete', methods=['POST'])
def delete(group):
    user = session['username']
    msg=''
    if (database._is_admin(user, group)):
        msg = 'Cannot abandon a group if you are the admin'
    else:
        database.abandon_group(user, group)
        msg = 'Group abandoned successfully'
    user_projects = database.get_projects_from_user(user)
    print(user_projects, user)
    groups = database.get_groups_of_user(session['username'])
    return render_template('personal_page.html', projects=user_projects, 
                                                     groups=groups,
                                                     username=user,
                                                        msg=msg)
    pass

@app.route('/dashboard', methods=['GET','POST'])
def projects():
    if (not 'loggedin' in session):
        return redirect(url_for('login'))
    user = session['username']
    if 'msg' in request.args:
        msg=request.args['msg']
    else:
        msg=''
    user_projects = database.get_projects_from_user(user)
    print(msg, 'Hola')
    groups = database.get_groups_of_user(session['username'])
    response = render_template('personal_page.html', projects=user_projects, 
                                                     groups=groups,
                                                     msg=msg,
                                                     username=user)
    return response

@app.route('/create_group', methods=['POST'])
def new_group(msg=''):
    if 'loggedin' in session:
        # Output message if something goes wrong...
        msg = ''
        print(request.form)
        if request.method == 'POST' and 'group' in request.form:
            # Create variables for easy access
            groupname = request.form['group']
            username = session['username']
            # Check if group exists using MySQL   
            with connection.cursor() as cursor:
                # Read a single record
                sql = 'SELECT * FROM groups WHERE group_name = %s'
                cursor.execute(sql, (groupname))
                connection.commit()        
                group_exists = cursor.fetchone()
                # If account exists show error and validation checks
                if group_exists:
                    msg = 'Group name already exists!'
                    return redirect(url_for('projects', msg=msg))
                else:
                    # Account doesnt exists and the form data is valid, now insert new account into accounts table
                    cursor.execute('INSERT INTO groups VALUES (%s,%s)', (groupname, 8))
                    cursor.execute('INSERT INTO member_group VALUES (%s, %s ,%s)', (username,groupname,True))
                    connection.commit()
                    msg = 'You have created a group succesfully!'
                    return redirect(url_for('projects', msg=msg))
        else:
            # Form is empty... (no POST data)
            msg = 'Please fill out the form!'
            print('Nanai')
            return redirect(url_for('projects'))
    return redirect(url_for('projects'), msg=msg)

@app.route('/dashboard/pr/<group>/<project>', methods=['POST','GET'])
def project_info(project, group):
    if (not 'loggedin' in session):
        return redirect(url_for('login')) 
    user = session['username']
    sql = "SELECT * from projects WHERE project_name=%s AND group_name = %s"
    with connection.cursor() as cursor:
        cursor.execute(sql, (project,group ))
        project_ = cursor.fetchone()
    with connection.cursor() as cursor:
        sql = "SELECT admin from member_group WHERE group_name=%s AND username = %s"
        cursor.execute(sql, (group,user ))
        admin= cursor.fetchone()
    print(admin)
    results = database.get_result_from_project(project)
    return render_template('project.html', 
                                     project=project_, 
                                     results=results,
                                     username=user,admin=admin)
    

@app.route('/dashboard/pr/<group>/<project>/changedescription', methods=['GET','POST'])
def change_description(project,group): 
    description=request.form['description']
    with connection.cursor() as cursor:
        sql = "UPDATE projects SET description = %s WHERE group_name = %s AND project_name = %s"
        cursor.execute(sql, (description,group,project))
        connection.commit()        
    return redirect(url_for('project_info',project=project,group=group))

@app.route('/dashboard/pr/<group>/<project>/delete_proj',methods=['GET', 'POST'])
def delete_project(group,project):
    with connection.cursor() as cursor:
        sql="DELETE FROM projects WHERE group_name = %s AND project_name = %s"
        cursor.execute(sql, (group,project ))
        sql="DELETE FROM project_result WHERE group_name = %s AND project_name = %s"
        cursor.execute(sql, (group,project))
        connection.commit()
    return redirect(url_for('projects'))

@app.route('/dashboard/pr/<project>/new_run', methods=['POST'])
def new_run(project):
    if (not 'loggedin' in session):
        return redirect(url_for('login'))
    #elif (session['username'] != user or (request.method == 'GET' and 'loggedin' in session)):
    #    return redirect(url_for('projects', user=session['username']))
    user = session['username']
    path = os.path.join('projects_data', project+'_data')
    group_name = database.get_id_from_project(project, user)[0]['group_name']
    if (not os.path.exists(path)):
        os.mkdir(path)
    csv_path = os.path.join(path, 'data.csv')
    data_details = database.get_data_details(project, group_name)
    sep = data_details['sep']
    col_names = data_details['colname']
    row_names = data_details['rowname']
    if int(col_names) == 0: col_names = None
    else: col_names = 0
    if int(row_names) == 0: row_names = None
    else: row_names = 0
    array = pd.read_csv(csv_path, sep = sep, header = col_names, index_col = row_names)
    array = pd.get_dummies(array)
    date = str(dt.datetime.now())[:-7]
    algorithm = int(request.form['algorithm'])
    groups = int(request.form['groups'])
    distance = request.form['distance']
    linkage = request.form['type']
    result = clustering.cluster(algorithm, array, groups, distance, linkage )
    id_ = database.get_id_from_project(project, user)
    id_ = id_[0]['id_project']
    out = open(os.path.join(path, str(id_)+'_run.csv'), 'w')
    for point, label in zip(array, result[0]):
        #(out.write(str(value)+'\t') for value in point)
        out.write(str(label))
        out.write('\n')
    out.close()
    array = pd.DataFrame(array)
    path = str(user+'_')
    database.save_result(id_, project, float(result[1]), date, algorithm, groups,
                         distance, linkage, group_name, user, path +'.csv')
    run_number = database.get_project_last_run_number(project)
    path = os.path.join('projects_data', project+'_data')
    csv_out = os.path.join(path, str(run_number)+'_.csv')
    with open(csv_out, 'w') as fhand:
        for label in result[0]:
            fhand.write(str(label)+'\n')
    return redirect('/dashboard/result?project='+project+'&run='+str(run_number))

algs = {0:'Hierarchical clustering', 1:'K-Means'}

@app.route('/dashboard/result', methods=['GET','POST'])
def recover_run():
    if(not request.args):
        return redirect(url_for('project_info'))
    project = request.args['project']
    run_id = request.args['run']
    run = database.get_run_results(run_id)[0]
    csv_path = os.path.join('projects_data', project+'_data','data.csv')
    csv_labels = os.path.join('projects_data', project+'_data',str(run_id)+'_.csv')
    f = open(csv_path)
    array = [] 
    for line in f:
        data = line.split()
        data = tuple(x for x in data)
        print(data)
        array.append(data)
    f = open(csv_labels)
    labels = []
    for line in f:
        labels.append(line.strip('\n'))
    dt = pd.DataFrame(array)
    print(len(array), len(labels))
    print(labels, dt)
    plot = clustering.plotPCA(dt, labels)
    plot_html = pio.to_html(plot, full_html = False)
    ids = database.get_project_ids(project, run_id)
    return render_template('run.html', 
                                     ids=ids,
                                     ID=run_id,
                                     date=run['date_time'],
                                     project_name=run['project_name'], 
                                     algorithm=algs[run['algo_rithm']],
                                     user_name=run['user'],
                                     group_name=run['group_name'],
                                     validation_parameter=run['validation_result'],
                                     number_of_groups=run['groups'],
                                     distance=run['distance'],
                                     linkage=run['linkage'],
                                     points=zip(array, labels),
                                     img=plot_html)

@app.route('/dashboard/pr/<proj>/compare', methods=['GET', 'POST'])
def compare_2_runs(proj):
    run1_id = request.args['run1']
    run = database.get_run_results(run1_id)[0]
    csv_path = os.path.join('projects_data', proj+'_data','data.csv')
    csv_labels = os.path.join('projects_data', proj+'_data',str(run1_id)+'_.csv')
    f = open(csv_path)
    array = []
    for line in f:
        data = line.split()
        data = tuple(x for x in data)
        print(data)
        array.append(data)
    f = open(csv_labels)
    labels = []
    for line in f:
        labels.append(line.strip('\n'))
    dt = pd.DataFrame(array)
    print(len(array), len(labels))
    plot = clustering.plotPCA(dt, labels)
    plot_html = pio.to_html(plot, full_html = False)
    if 'id2' in request.args:
        run2_id = request.args['id2']
    else:
        run2_id = request.form['id_to_compare']
    run2 = database.get_run_results(run2_id)[0]
    csv_path = os.path.join('projects_data', proj+'_data','data.csv')
    csv_labels = os.path.join('projects_data', proj+'_data',str(run1_id)+'_.csv')
    f = open(csv_path)
    array2 = []
    for line in f:
        data = line.split()
        data = tuple(x for x in data)
        print(data)
        array2.append(data)
    f = open(csv_labels)
    labels2 = []
    for line in f:
        labels2.append(line.strip('\n'))
    #### Conteo
    igual = 0
    distinto = 0
    for label_1, label_2 in zip(labels, labels2):
        if label_1 == label_2:
            igual += 1
        else:
            distinto += 1
    clusters = set(labels)
    id_1_class = {}
    id_2_class = {}
    for element in clusters:
        id_1_class[element] = labels.count(element)
        id_2_class[element] = labels.count(element)
    clasification = (id_1_class,id_2_class )
    dt = pd.DataFrame(array2)
    plot = clustering.plotPCA(dt, labels)
    plot_html_2 = pio.to_html(plot, full_html = False)
    return render_template('result_compare.html', ID=run1_id, ID_2=run2_id,
                                     date=run['date_time'],
                                     project_name=run['project_name'], 
                                     algorithm=algs[run['algo_rithm']],
                                     user_name=run['user'],
                                     igual = (igual, distinto),
                                     group_name=run['group_name'],
                                     validation_parameter=run['validation_result'],
                                     number_of_groups=run['groups'],
                                     distance=run['distance'],
                                     linkage=run['linkage'],
                                     points=zip(array, labels, labels2),
                                     img=plot_html,
                                     set_=sorted(clusters, key=lambda x: int(x[7:])),
                                     clas=clasification,
                                     date_2=run['date_time'],
                                     algorithm_2=algs[run2['algo_rithm']],
                                     user_name_2=run2['user'],
                                     group_name_2=run2['group_name'],
                                     validation_parameter_2=run2['validation_result'],
                                     number_of_groups_2=run2['groups'],
                                     distance_2=run2['distance'],
                                     linkage_2=run2['linkage'],
                                     img_2=plot_html_2)

@app.route('/header')
def header():
    return render_template('header.html', user=session['username'])


############# DEMO

@app.route('/demo/new_run', methods=['POST'])
def new_demo_run():
    user = 'Demo user'
    project = 'Demo project'
    path = os.path.join('projects_data', project+'_data' )
    if (not os.path.exists(path)):
        os.mkdir(path)
    f = open(os.path.join('projects_data', request.form['dataset'] ))
    a = open('projects_data/Demo project_data/data.csv', 'w')
    for line in f:
        a.write(line)
    a.close()
    f = open(os.path.join('projects_data', request.form['dataset'] ))
    array = []
    for line in f:
        data = line.split()
        data = tuple(float(x) for x in data)
        array.append(data)
    date = str(dt.datetime.now())[:-7]
    algorithm = int(request.form['algorithm'])
    groups = int(request.form['groups'])
    distance = request.form['distance']
    linkage = request.form['type']
    result = clustering.cluster(algorithm, array, groups, distance, linkage )
    id_ = database.get_id_from_project(project, user)
    print(id_)
    id_ = id_[0]['id_project']
    out = open(os.path.join(path, str(id_)+'_run.csv'), 'w')
    for point, label in zip(array, result[0]):
        (out.write(str(value)+'\t') for value in point)
        out.write(str(label))
        out.write('\n')
    out.close()
    array = pd.DataFrame(array)
    group_name = database.get_id_from_project(project, user)[0]['group_name']
    path = str(user+'_')
    database.save_result(id_, project, float(result[1]), date, algorithm, groups,
                         distance, linkage, group_name, user, path +'.csv')
    run_number = database.get_project_last_run_number(project)
    path = os.path.join('projects_data', project+'_data')
    csv_out = os.path.join(path, str(run_number)+'_.csv')
    with open(csv_out, 'w') as fhand:
        for label in result[0]:
            fhand.write(str(label)+'\n')
    return redirect('/dashboard/result?project='+project+'&run='+str(run_number))

@app.route('/demo')
def demo():
    user = 'Demo user'
    proj = 'Demo project'
    project_ = database.get_info_from_project(proj)
    results = database.get_result_from_project(proj)
    return render_template('project_demo.html', 
                                     project=project_[0], 
                                     results=results,
                                     username=user)
    pass

@app.route('/dashboard/new_project', methods=['GET', 'POST'])
def new_project(msg=''):
    if 'loggedin' in session:
        # Output message if something goes wrong...
        if request.method == 'POST' and 'name_of_the_project' in request.form and 'file' in request.files and 'groups' in request.form:
            # Create variables for easy access
            projectname = request.form['name_of_the_project']
            username = session['username']
            groupname= request.form['group']
            description= request.form['description']
            #aparezca en el html un desplegable con los grupos a los que pertenece, y ojala poder seleccionar varios     
            with connection.cursor() as cursor:
                # Read a single record
                path = "%s_data" % (projectname)
                # If mirando si ese project name esta cogido ya para su user o su grupo                
                sql = "SELECT * from projects WHERE project_name = %s and group_name = %s;"
                cursor.execute(sql, (projectname , groupname))
                connection.commit()        
                project_exists = cursor.fetchone()
                # If project exists show error and validation checks
                if project_exists:
                    msg = 'There is a project with the name in that group!'
                else:
                    # Account doesnt exists and the form data is valid, now insert new account into accounts table
                    path = os.path.join('projects_data', projectname+'_data')
                    if (not os.path.exists(path)):
                        os.mkdir(path)
                    csv_path = os.path.join(path, 'data.csv')
                    f = request.files['file']
                    sep = request.form['input_type']
                    if int(request.form['col_names']): col_names = 0
                    else: col_names = None
                    if int(request.form['row_names']): row_names = 0
                    else: row_names = None
                    f.save(csv_path)
                    array = pd.read_csv(csv_path, sep = sep, header = col_names, index_col = row_names)
                    array = pd.get_dummies(array)
                    cursor.execute('INSERT INTO projects ( description, group_name, user, project_name, file_path, sep, rowname, colname) VALUES ( %s, %s, %s, %s, %s, %s, %s, %s);', (description, groupname, username, projectname , path, sep, request.form['row_names'], request.form['col_names']))
                    connection.commit()
                    date = str(dt.datetime.now())[:-7]
                    algorithm = int(request.form['algorithm'])
                    distance = request.form['distance']
                    groups = int(request.form['groups'])
                    linkage = request.form['type']
                    path = str(session['username']+'_')
                    result = clustering.cluster(algorithm, array, groups, distance, linkage )
                    id_ = database.get_id_from_project(projectname, username)[0]['id_project']
                    group_name = database.get_id_from_project(projectname, username)[0]['group_name']
                    database.save_result(id_, projectname, float(result[1]), date, algorithm, groups,
                                         distance, linkage, group_name, username, path +'.csv')
                    run_number = database.get_project_last_run_number(projectname)
                    path = os.path.join('projects_data', projectname+'_data')
                    csv_out = os.path.join(path, str(run_number)+'_.csv')
                    with open(csv_out, 'w') as fhand:
                        for label in result[0]:
                            fhand.write(str(label)+'\n')
                    run_number = database.get_project_last_run_number(projectname)
                    return redirect('/dashboard/result?project='+projectname+'&run='+str(run_number))
        else:
            # Form is empty... (no POST data)
            msg = 'Please fill out the form!'
            groups = database.get_groups_of_user(session['username'])
            groups = ['Privado'] + [group['group_name'] for group in groups]
            print('Its a POST!')
            return render_template('new_project.html', 
                                                       msg=msg,
                                                       groups=groups)
    return redirect(url_for('login'))

@app.route('/dashboard/pr/<proj>/download')
def download_project(proj):
    import io
    data = io.BytesIO()
    path = os.path.join('projects_data', proj+'_data')
    zip_file = zipfile.ZipFile('Downloads/'+proj+'.zip', 'w')
    for file in os.listdir(path):
        zip_file.write(os.path.join(path, file))
    zip_file.close()
    data.seek(0)
    data = open('Downloads/'+proj+'.zip', 'rb')
    return send_file(data, 
                     attachment_filename=proj+'.zip', 
                     as_attachment=True,
                     mimetype='application/zip')

######## SIGN UP

@app.route('/signup', methods=['GET', 'POST'])
def signup(msg=''):
    # Output message if something goes wrong...
    # Check if "username", "password" and "email" POST requests exist (user submitted form)
    if request.method == 'POST' and 'username' in request.form and 'password' in request.form and 'email' in request.form:
        # Create variables for easy access
        username = request.form['username']
        password = request.form['password']
        if(request.form['confirm'] != request.form['password']):
            msg = 'Passwords don\'t match'
            return render_template('signup.html', msg=msg)
        email = request.form['email']
        # Check if account exists using MySQL        
        with connection.cursor() as cursor:
            # Read a single record
            sql = 'SELECT * FROM user_info WHERE username = %s'
            cursor.execute(sql, (username))
            connection.commit()        
            account = cursor.fetchone()
            # If account exists show error and validation checks
            if account:
                msg = 'Account already exists!'
            elif not re.match(r'[^@]+@[^@]+\.[^@]+', email):
                msg = 'Invalid email address!'
            elif not re.match(r'[A-Za-z0-9]+', username):
                msg = 'Username must contain only characters and numbers!'
            elif not username or not password or not email:
                msg = 'Please fill out the form!'
            else:
                # Account doesnt exists and the form data is valid, now insert new account into accounts table
                password = hashlib.md5(password.encode('ascii')).hexdigest()
                cursor.execute('INSERT INTO user_info VALUES (%s, %s, %s)', (username,email,password))
                connection.commit()
                msg = 'You have successfully registered!'
                return redirect(url_for('login'))
    elif request.method == 'POST':
        # Form is empty... (no POST data)
        msg = 'Please fill out the form!'
    # Show registration form with message (if any)
    
    return render_template('signup.html', msg=msg)

###### SETTINGS

@app.route('/dashboard/gr/<group>',methods=['GET', 'POST'])
def groupsettings(group,msg=''):
    
    username=session['username']
    admin=0
    if 'msg' in request.args:   
        msg=request.args['msg']	
    with connection.cursor() as cursor:   
        sql = "SELECT admin FROM member_group WHERE username= %s and group_name =%s"
        cursor.execute(sql, (username,group))
        admin=cursor.fetchone()
    with connection.cursor() as cursor:
        sql = "SELECT * FROM member_group WHERE group_name = %s"
        cursor.execute(sql, (group,))
        users_of_group=cursor.fetchall()
    num_admins=0
    
    for user in users_of_group:
        if user['admin']==1:
            num_admins+=1    	
    num_users=len(users_of_group)
    if admin['admin']==1:
        return render_template('settings_group_admin.html',users_of_group=users_of_group,group=group,msg=msg,num_users=num_users,num_admins=num_admins)  
    return render_template('settings_group.html',users_of_group=users_of_group,group=group,msg=msg,num_admins=num_admins)


@app.route('/dashboard/gr/<group>/include',methods=['GET', 'POST'])
def include_user(group):
    msg = ''
    
    if request.method == 'POST' and request.form['newmember']!='':
        newuser=request.form['newmember']
        with connection.cursor() as cursor:
            sql = "SELECT * FROM user_info WHERE username = %s"
            cursor.execute(sql, (newuser,))       
            account = cursor.fetchone()
            if account:
                with connection.cursor() as cursor:
                    sql = "SELECT * FROM member_group WHERE username = %s AND group_name = %s"
                    cursor.execute(sql, (newuser,group))                         
                    account = cursor.fetchone()
                    if account:
                        msg='The user is already in this group'
                    else:
                        cursor.execute('INSERT INTO member_group VALUES (%s, %s ,%s)', (newuser,group,False))
                        connection.commit()
                        msg='User included in the group succesfully!'
            else:
                msg='There is no user registered with that username'
    return redirect(url_for('groupsettings',msg=msg,group=group))

@app.route('/dashboard/gr/<group>/delete',methods=['GET', 'POST'])
def delete_user(group):
    user=request.args['user']	
    with connection.cursor() as cursor:
        sql="DELETE FROM member_group WHERE username = %s AND group_name = %s"
        cursor.execute(sql, (user,group))
        connection.commit()
    return redirect(url_for('groupsettings',group=group))

@app.route('/dashboard/gr/<group>/permision',methods=['GET', 'POST'])
def give_permision(group):
    user=request.args['user']	
    with connection.cursor() as cursor:
        sql="UPDATE member_group SET admin = %s WHERE username = %s AND group_name = %s"
        cursor.execute(sql, (1,user,group))
        connection.commit()
    return redirect(url_for('groupsettings',group=group))

@app.route('/dashboard/gr/<group>/leave',methods=['GET', 'POST'])
def leave_group(group):
    msg=''
    num_admins=request.args['num_admins']
    user=session['username']
    if int(num_admins)>1:
        with connection.cursor() as cursor:
            sql="DELETE FROM member_group WHERE username = %s AND group_name = %s"
            cursor.execute(sql, (user,group))
            connection.commit()
            return redirect(url_for('projects'))
    else:
        msg='There must be at least one admin per group, give permision to a member before leaving the group'
        return redirect(url_for('groupsettings',group=group,msg=msg))

@app.route('/dashboard/gr/<group>/delete_group',methods=['GET', 'POST'])
def delete_group(group):
    with connection.cursor() as cursor:
        sql="DELETE FROM member_group WHERE group_name = %s"
        cursor.execute(sql, (group, ))
        connection.commit()
        sql="DELETE FROM projects WHERE group_name = %s"
        cursor.execute(sql, (group,))
        connection.commit()
        sql="DELETE FROM project_result WHERE group_name = %s"
        cursor.execute(sql, (group,))
        connection.commit()
    return redirect(url_for('projects')) 

@app.route('/dashboard/settings',methods=['GET', 'POST'])
def settings():
    if (not 'loggedin' in session):
        return redirect(url_for('login'))
    msg = ''
 
    if request.method == 'POST' and request.form['action'] == 'changeusername' and request.form['currentusername']!='' and request.form['password']!='' and request.form['newusername']!='':

        currentusername = request.form['currentusername']
        username=session['username']	
        newusername = request.form['newusername']
        password = request.form['password']
        password = hashlib.md5(password.encode('ascii')).hexdigest()
        if currentusername==username:
            with connection.cursor() as cursor:
                sql = "SELECT * FROM user_info WHERE username = %s"
                cursor.execute(sql, (newusername))
                connection.commit()        
                exists = cursor.fetchone()
                if exists:
                    msg='Username already exists!'
    		
                else:
                    with connection.cursor() as cursor:
                        sql = "SELECT * FROM user_info WHERE username = %s AND password = %s"
                        cursor.execute(sql, (username,password))
                        connection.commit()        
                        account = cursor.fetchone()
                        # If account exists update the username in all tables
                        if account:
                            print(session)
                            with connection.cursor() as cursor:
                                sql = "UPDATE user_info SET username = %s WHERE username = %s"
                                cursor.execute(sql, (newusername,username))
                                connection.commit()        
                                account = cursor.fetchone()                  
                            with connection.cursor() as cursor:
                                sql = "UPDATE member_group SET username = %s WHERE username = %s"
                                cursor.execute(sql, (newusername,username))
                                connection.commit()        
                                account = cursor.fetchone()
                            with connection.cursor() as cursor:
                                # Read a single record
                                sql = "UPDATE projects SET user = %s WHERE user = %s"
                                cursor.execute(sql, (newusername,username))
                                connection.commit()        
                                account = cursor.fetchone()
                            with connection.cursor() as cursor:
                                # Read a single record
                                sql = "UPDATE project_result SET user = %s WHERE user = %s"
                                cursor.execute(sql, (newusername,username))
                                connection.commit()        
                                account = cursor.fetchone()
                                msg ='Username succesfully changed!'
                                session['username'] = newusername
                        
                            
                        else:
                        # Account doesnt exist or username/password incorrect
                             msg = 'Incorrect username/password!'  
        else:
            msg = 'Incorrect username/password!'
    elif request.method == 'POST' and request.form['action'] == 'changepassword' and request.form['currentusername']!='' and request.form['password']!='' and request.form['newpassword']!='' and request.form['confirmpassword']!='':
        currentusername = request.form['currentusername']
        username=session['username']	
        newusername = request.form['newusername']
        password = request.form['password']
        newpassword = request.form['newpassword']
        confirmpassword = request.form['confirmpassword']
        password = hashlib.md5(password.encode('ascii')).hexdigest()
        if currentusername==username:
            if newpassword==confirmpassword:                        
                with connection.cursor() as cursor:
                    sql = "SELECT * FROM user_info WHERE username = %s AND password = %s"
                    cursor.execute(sql, (username,password))
                    connection.commit()        
                    account = cursor.fetchone()
                    # If account exists update the password in all tables
                    if account:
                        newpassword= hashlib.md5(newpassword.encode('ascii')).hexdigest()
                        with connection.cursor() as cursor:
                            sql = "UPDATE user_info SET password = %s WHERE username = %s"
                            cursor.execute(sql, (newpassword,username))
                            connection.commit()        
                            account = cursor.fetchone()
                            msg='Password changed succesfully!'
                    else:
                        msg='Incorrect username/password!'
            else:
                msg='Please confirm the new password correctly'                 
    else:
        msg='Please fill one of the two forms'

    return render_template('settings.html',msg=msg)

####### ABOUT

@app.route('/about_us')
def about():
    if('loggedin' in session):
        return render_template('about.html', logged=True)
    else:
        return render_template('about.html', logged=False)


####### LOGOUT

@app.route('/logout')
def logout():
    # Remove session data, this will log the user out
   session.pop('loggedin', None)
   session.pop('email', None)
   session.pop('username', None)
   # Redirect to login page
   return redirect(url_for('login'))

####### ERRORS

@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404

@app.errorhandler(500)
def internal_server_error(e):
    return render_template('500.html'), 500

@app.errorhandler(403)
def page_forbidden(e):
    return render_template('403.html'), 500

@app.route('/favicon.ico')
def get_image():
    return send_file('/static/img/favicon.ico', mimetype='image/ico')

if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=True)
