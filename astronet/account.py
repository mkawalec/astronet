from astronet import app
from astronet.helpers import (login_required, query_db,
        gen_filename)
from flask import (Flask, request, redirect, url_for, abort,
        render_template, flash, g, session)

from hashlib import sha256
from random import randint

@app.route('/login', methods=['GET', 'POST'])
def login():
    email = ''

    if request.method == 'POST':
        email = request.form['email']
        user = query_db('SELECT id,passwd,real_name,email,salt '
                        'FROM users WHERE email=%s',
                        [email], one=True)

        if user is None:
            flash('There is no user with this email.', 'error')
            email = ''
        elif user['passwd'] == (
                sha256(request.form['passwd'] + user['salt'] +
                    app.config['SALT']).hexdigest()):
                    session['logged_in'] = True
                    session['email'] = user['email']
                    session['uid'] = user['id']

                    flash('You were logged in', 'success')
                    
                    next = request.form['next']
                    if not next or next == 'None':
                        return redirect(url_for('home')+'search') 
                    else:
                        return redirect(next)
        else:
            flash('Wrong password.', 'error')

    next = None if not 'next' in request.args else request.args['next']
    return render_template('login.html', next=next, email=email)

@app.route('/logout')
@login_required
def logout():
    if 'logged_in' in session:
        if session['logged_in']:
            del session['logged_in']
            if 'email' in session:
                del session['email']
            if 'uid' in session:
                del session['uid']
            if 'role' in session:
                del session['role']
            flash('Successfully logged out', 'success')

            return redirect(url_for('home'))

    flash('Something went wrong when logging you out', 'error')
    
    return redirect(url_for('home'))

# TODO: Implement
@app.route('/password_reset', methods=['POST', 'GET'])
def reset_pass():
    return render_template('reset_pass.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        if request.form['passwd1'] != request.form['passwd2']:
            flash('The passwords are not the same', 'error')
            return render_template('register.html',
                                   email=request.form['email'],
                                   first=randint(1,20),
                                   second=randint(1,20))

        if len(request.form['passwd1']) == 0:
            flash('The passwords are empty', 'error')
            return render_template('register.html',
                                   email=request.form['email'],
                                   first=randint(1,20),
                                   second=randint(1,20))

        if len(request.form['email']) == 0:
            flash('The email is empty', 'error')
            return render_template('register.html',
                                   first=randint(1,20),
                                   second=randint(1,20))

        if int(request.form['first'])+int(request.form['second']) != int(request.form['result']):
            flash('The result you entered is incorrect', 'error')
            return render_template('register.html',
                                   email=request.form['email'],
                                   first=randint(1,20),
                                   second=randint(1,20))
            
        if query_db('SELECT id FROM users WHERE email=%s',
                    [request.form['email']], one=True) is not None:
            flash('The email is already in use', 'error')
            return render_template('register.html', 
                                   email=request.form['email'],
                                   first=randint(1,20),
                                   second=randint(1,20))
        
        salt = gen_filename(10)
        if query_db('INSERT INTO users (passwd,salt,email) '
                 'VALUES (%s,%s,%s)',
                 [sha256(request.form['passwd1']+salt+app.config['SALT']).hexdigest(),
                  salt,request.form['email']]):
            flash('Your account was created. Good sailing sailor!', 
                'success')

            # Automatically logging the user
            session['uid'] = query_db('SELECT id FROM users WHERE email=%s',
                                      [request.form['email']], one=True)['id']
            session['logged_in'] = True
            session['email'] = request.form['email']

        else:
            flash('Error adding you', 'error')
        return redirect(url_for('search'))
    return render_template('register.html', first=randint(1,20), second=randint(1,20))

