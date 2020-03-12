# -*- coding: utf-8 -*-

from flask import Flask, render_template, request, redirect, url_for, session
import datetime as dt

#import plotly.express as px
#import plotly.io as pio
import os
import os.path
import database
from clustering import *
import pymysql
import re
import hashlib

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

@app.route('/dashboard', methods=['GET','POST'])
def projects():
    if (not 'loggedin' in session):
        return redirect(url_for('login'))
    user = session['username']
    user_projects = database.get_projects_from_user(user)
    print(user_projects, user)
    groups = database.get_groups_of_user(session['username'])
    print(type(groups))
    print(groups)
    response = render_template('personal_page.html', projects=user_projects,
                                                     groups=groups,
                                                     username=user)
    return response

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

@app.route('/create_group', methods=['POST'])
def new_group():
    if 'loggedin' in session:
        # Output message if something goes wrong...
        msg = ''
        print(request.form)
        if request.method == 'POST' and 'group' in request.form:
            print('If entered')
            # Create variables for easy access
            groupname = request.form['group']
            username = session['username']
            # Check if group exists using MySQL
            with connection.cursor() as cursor:
                # Read a single record
                sql = 'SELECT * FROM groups WHERE group_name = %s'
                cursor.execute(sql, (groupname))
                connection.commit()
                group = cursor.fetchone()
                # If account exists show error and validation checks
                if group:
                    msg = 'Group name already exists!'
                else:
                    # Account doesnt exists and the form data is valid, now insert new account into accounts table
                    cursor.execute('INSERT INTO groups VALUES (%s,%s)', (groupname, 8))
                    cursor.execute('INSERT INTO member_group VALUES (%s, %s ,%s)', (username,groupname,True))
                    connection.commit()
                    msg = 'You have created a group succesfully!'
                    return redirect(url_for('projects'))
        else:
            # Form is empty... (no POST data)
            msg = 'Please fill out the form!'
            print('Nanai')
            return redirect(url_for('projects'))
    return redirect(url_for('login'))

@app.route('/dashboard/pr/<proj>')
def project_info(proj):
    if (not 'loggedin' in session):
        return redirect(url_for('login'))
    user = session['username']
    project_ = database.get_info_from_project(proj)
    print(project_)
    results = database.get_result_from_project(proj)
    return render_template('project.html',
                                     project=project_[0],
                                     results=results,
                                     username=user)

@app.route('/dashboard/pr/<project>/new_run', methods=['POST'])
def new_run(project):
    if (not 'loggedin' in session):
        return redirect(url_for('login'))
    #elif (session['username'] != user or (request.method == 'GET' and 'loggedin' in session)):
    #    return redirect(url_for('projects', user=session['username']))
    f = request.files['file']
    separator = request.form['input_type']
    if int(request.form['col_names']): col_names = 0
    else: col_names = None
    if int(request.form['row_names']): row_names = 0
    else: row_names = None
    user = session['username']
    path = os.path.join('projects_data', project+'_data')
    if (not os.path.exists(path)): os.mkdir(path)
    csv_path = os.path.join(path, 'data.csv')
    f.save(csv_path)
    array = pd.read_csv(csv_path, sep = separator, header = col_names, index_col = row_names)
    array = pd.get_dummies(array)
    date = str(dt.datetime.now())[:-7]
    algorithm = int(request.form['algorithm'])
    groups = int(request.form['groups'])
    distance = request.form['distance']
    linkage = request.form['type']
    result = cluster(algorithm, array, groups, distance, linkage )

    id_ = database.get_id_from_project(project, user)[0]['id_project']
    group_name = database.get_id_from_project(project, user)[0]['group_name']
    path = str(user+'_')
    database.save_result(id_, project, float(result[1]), date, algorithm, groups,
                         distance, linkage, group_name, user, path +'.csv')
    points = zip(array, result[0])

    plot = plotPCA(array, result[0])
    plot_html = pio.to_html(plot, full_html = False)

    return render_template('run.html',
                                 project_name=project,
                                 algorithm=algs[algorithm],
                                 user_name=user,
                                 date=date,
                                 group_name=group_name,
                                 validation_parameter=float(result[1]),
                                 number_of_groups=groups,
                                 distance=distance,
                                 points=points,
                                 input_=array,
                                 img = plot_html,
                                 groups=result[0],
                                 linkage=linkage)

@app.route('/<user>/<project>/results', methods=['POST','GET'])
def run_results(user, project, id_project, datetime):
    if (not 'loggedin' in session):
        return redirect(url_for('login'))
    run = database.get_run_results(id_project, datetime, user)
    run=run[0]
    return render_template('run.html',
                                     project_name=run['project_name'],
                                     algorithm=run['algo_rithm'],
                                     user_name=run['user'],
                                     group_name=run['group_name'],
                                     validation_parameter=run['validation_result'],
                                     number_of_groups=run['groups'],
                                     distance=run['distance'],
                                     linkage=run['linkage'])

@app.route('/header')
def header():
    return render_template('header.html')

@app.route('/dashboard/new_project', methods=['GET', 'POST'])
def new_project(msg=''):
    if 'loggedin' in session:
        # Output message if something goes wrong...
        print('Logged in')
        print(request.form)
        print(request.files)
        if request.method == 'POST' and 'name_of_the_project' in request.form and 'file' in request.files and 'groups' in request.form:
            print('Correct')
            # Create variables for easy access
            projectname = request.form['name_of_the_project']
            username = session['username']
            groupname= request.form['group']
            #aparezca en el html un desplegable con los grupos a los que pertenece, y ojala poder seleccionar varios
            with connection.cursor() as cursor:
                # Read a single record
                path = "%s_data" % (projectname)
                print(path)
                # If mirando si ese project name esta cogido ya para su user o su grupo
                sql = "SELECT * from projects WHERE project_name = %s and group_name = %s;"
                cursor.execute(sql, (projectname , groupname))
                connection.commit()
                project_exists = cursor.fetchone()
                # If project exists show error and validation checks
                print('Checking if exists')
                if project_exists:
                    print('Exists project')
                    msg = 'There is a project with the name in that group!'
                else:
                    # Account doesnt exists and the form data is valid, now insert new account into accounts table
                    cursor.execute('INSERT INTO projects ( group_name, user,project_name, file_path) VALUES ( %s, %s, %s, %s);', (groupname, username, projectname , path))
                    connection.commit()
                    print('Does not exist')
                    path = os.path.join('projects_data', projectname+'_data')
                    if (not os.path.exists(path)):
                        os.mkdir(path)
                    csv_path = os.path.join(path, 'data.csv')
                    f = request.files['file']
                    f.save(csv_path)
                    array = pd.read_csv(csv_path, sep = "\t")
                    print('Clustering now')
                    date = str(dt.datetime.now())[:-7]
                    algorithm = int(request.form['algorithm'])
                    distance = request.form['distance']
                    groups = int(request.form['groups'])
                    linkage = request.form['type']
                    print('Data ready')
                    path = str(session['username']+'_')
                    npath = 'static/img/'+path+'.html'
                    result = cluster(algorithm, array, groups, distance, linkage )


                    id_ = database.get_id_from_project(projectname, username)[0]['id_project']
                    group_name = database.get_id_from_project(projectname, username)[0]['group_name']
                    path = str(username+'_')
                    print('Saving on database')
                    database.save_result(id_, projectname, float(result[1]), date, algorithm, groups,
                                         distance, linkage, group_name, username, path +'.csv')
                    points = zip(array, result[0])

                    temporal = tempfile.NamedTemporaryFile(dir = "static/img", suffix='.html', delete = False)
                    plot = plotPCA(array, result[0])
                    pio.write_html(plot, file = temporal.name)

                    print('Rendering HTML')
                    return render_template('run.html',
                                                 project_name=projectname,
                                                 algorithm=algs[algorithm],
                                                 user_name=username,
                                                 date=date,
                                                 group_name=group_name,
                                                 validation_parameter=float(result[1]),
                                                 number_of_groups=groups,
                                                 distance=distance,
                                                 points=points,
                                                 input_=array,
                                                 img_path="../../../static/img/"+temporal.name.split("/")[-1],
                                                 groups=result[0],
                                                 linkage=linkage)
        else:
            # Form is empty... (no POST data)
            msg = 'Please fill out the form!'
            groups = database.get_groups_of_user(session['username'])
            groups = ['Private'] + [group['group_name'] for group in groups]
            print('Its a POST!')
            return render_template('new_project.html',
                                                       msg=msg,
                                                       groups=groups)
    return redirect(url_for('login'))



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

@app.route('/about_us')
def about():
    if('loggedin' in session):
        return render_template('about.html', logged=True)
    else:
        return render_template('about.html', logged=False)

@app.route('/dashboard/settings')
def settings():
    if (not 'loggedin' in session):
        return redirect(url_for('login'))
    return render_template('settings.html')

@app.route('/logout')
def logout():
    # Remove session data, this will log the user out
   session.pop('loggedin', None)
   session.pop('email', None)
   session.pop('username', None)
   # Redirect to login page
   return redirect(url_for('login'))

@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404

@app.errorhandler(500)
def internal_server_error(e):
    return render_template('500.html'), 500

@app.errorhandler(403)
def page_forbidden(e):
    return render_template('403.html'), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=False)
