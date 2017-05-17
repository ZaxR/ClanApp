from flask import Flask, flash, redirect, render_template, request, session, abort
from flask_login import logout_user, login_required, login_manager
from app import app


@app.route('/')
@app.route('/index')
def home():
    if not session.get('logged_in'):
        return render_template('login.html')
    else:
        return addcaps() #"Hello Boss!  <a href='/logout'>Logout</a>"

@app.route('/login', methods=['GET','POST'])
def login():
    if request.method == 'GET':
        return render_template('login.html')
    if request.form['password'] == 'password' and request.form['username'] == 'admin':
        session['logged_in'] = True
    else:
        flash('wrong password!')
    return home()

@app.route('/logout')
def logout():
    session['logged_in'] = False
    return redirect('index')

@app.route('/addcaps')
def addcaps():
    if not session['logged_in']:
        return home()
    else:
        return render_template('addcaps.html',
                               names=['Runeshady','Wigton','Z A X'])

@app.route("/sample" , methods=['GET', 'POST'])
def sample():
    select = request.form.get('comp_select')
    return(str(select)) # just to see what select is


# @app.route('/addcaps', methods=['GET', 'POST'])
# # for views.py
# # https://stackoverflow.com/questions/32019733/getting-value-from-select-tag-using-flask