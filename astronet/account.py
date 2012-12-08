# coding=utf-8
from astronet import app
from astronet.api import log_me_in
from astronet.helpers import (login_required, query_db,
        gen_filename)
from flask import (Flask, request, redirect, url_for, abort,
        render_template, flash, g, session)
from hashlib import sha256
from random import randint
import mailing
import re
    

@app.route('/login', methods=['GET', 'POST'])
def login():
    """ Displays a login template when accessed with **GET** and loggs
        the user in when accessed with **POST**.

        The **POST** request must have the following::
            
            request.form = {
                'email': user_email,
                'passwd': user_password
            }

        .. WARNING::
            This function will not work nicely with JSON-supporting scripts
    """
    email = ''

    if request.method == 'POST':
        email = request.form['email']
        user = query_db('SELECT id,passwd,real_name,email,salt,string_id '
                        'FROM users WHERE email=%s LIMIT 1',
                        (email,), one=True)

        if user is None:
            flash(u'Użytkownik o podanym emailu nie istnieje.', 'error')
            email = ''
        elif user['passwd'] == (
                sha256(request.form['passwd'] + user['salt'] +
                    app.config['SALT']).hexdigest()):
                    
                    # Check if this user is already logged in
                    if 'logged_in' in session and session['logged_in']:
                        flash(u'Ten użytkownik już jest zalogowany!','error')
                        return redirect(url_for('home'))
                    
                    log_me_in(user['id'],user['email'],
                                        user['string_id'])
                    flash(u'Zostałeś zalogowany', 'success')
                    
                    next = request.form['next']
                    if not next or next == 'None':
                        return redirect(url_for('home')) 
                    else:
                        return redirect(next)
        else:
            flash(u'Złe hasło.', 'error')

    next = None if not 'next' in request.args else request.args['next']
    return render_template('login.html', next=next, email=email)

@app.route('/logout')
@login_required
def logout():
    """ When accessed with **GET**, loggs the currently logged in
        user out """
    if 'logged_in' in session:
        if session['logged_in']:
            del session['logged_in']
            if 'email' in session:
                del session['email']
            if 'uid' in session:
                del session['uid']
            if 'role' in session:
                del session['role']
            flash(u'Wylogowano pomyślnie', 'success')

            return redirect(url_for('home'))

    flash(u'Podczas logowania nastąpił błąd.', 'error')
    
    return redirect(url_for('home'))

# TODO: Implement, check if everything is hacker-proof
@app.route('/password_reset', methods=['POST', 'GET'])
def reset_pass():
    """ A password reset form """
    if request.method == 'POST':
        # We want to protect against spaces '_'
        email = request.form['email'].strip()

        if not re.match('^[a-zA-Z0-9._%-]+@[a-zA-Z0-9._%-]+.[a-zA-Z]{2,6}$', email):
            flash(u'Wprowadzono niepoprawny adres email', 'error')
            return render_template('reset_pass.html')
            
        if query_db('SELECT id FROM users WHERE email=%s LIMIT 1',
                    (email,), one=True) is None:
            flash(u'Podany adres nie występuje w bazie', 'error')
            return render_template('reset_pass.html')                
        
        new_hash = gen_filename(10)
        if query_db('UPDATE users set reset_hash=%s WHERE email=%s',
                (new_hash,email)):
            mailing.email(email, 'pass_reset',hash=new_hash)
            flash(u'Na podany adres email wysłano link do zmiany hasła.', 'success')
            return redirect(url_for('home'))
    return render_template('reset_pass.html')
    
@app.route('/password_reset/<hash>', methods=['POST', 'GET'])
def reset_pass_finalize(hash):
    """ It checks if hash is all right and sets new password 
        while cleaning hash from database. """

    if request.method == 'POST':
        if request.form['passwd1'].strip() != request.form['passwd2'].strip():
            flash(u'Hasła nie są takie same', 'error')
            return render_template('new_pass.html',hash=hash)

        user_data = query_db('SELECT id,string_id,salt,email FROM '
                             'users WHERE reset_hash=%s LIMIT 1',
                             (hash,), one=True)
        if not user_data:
            flash(u'Błędy kod aktywacyjny', 'error')
            return render_template('new_pass.html')

        if query_db('UPDATE users SET reset_hash=%s, passwd=%s '
                    'WHERE email = %s', (None, 
                    sha256(request.form['passwd1'].strip()+\
                            user_data['salt']+app.config['SALT']).hexdigest(),
                    user_data['email'])):
            flash(u'Hasło zostało zmienione.', 'success')
            log_me_in(user_data['id'],user_data['email'],user_data['string_id'])
            flash(u'Zostałeś zalogowany', 'success')
            return redirect(url_for('home'))
        else:
            flash(u'Błąd bazy danych', 'error')

    # We need to check if the reset hash is correct here
    # for instance in case of someone wrongly entering the hash
    correct_hash = query_db('SELECT id FROM users WHERE reset_hash=%s LIMIT 1',
                       (hash,), one=True)
    if not correct_hash:
        flash(u'Błędny kod resetujący hasło!', 'error')
        return redirect(url_for('home'))
    return render_template('new_pass.html',hash=hash)



@app.route('/register', methods=['GET', 'POST'])
def register():
    """ Register a user if certain conditions are met. Renders a registration
        template if accessed with **GET** and tries to register if
        queried by **POST**

        Requires the following parameters::
            
            request.form = {
                'passwd1': password_first_time,
                'passwd2': password_second_time,
                'first': first_number,
                'second': second_number,
                'result': sum_of_numbers,
                'email': users_email
            }

        The numbers are a basic captcha, in order to register
        the prospective user needs to provide the sum of two numbers
        correctly
    """
    if request.method == 'POST':
        # TODO: This needs an overhaul, we need a sane correctness checking
        # some were made, but mayby it needs more improvements 
        email = request.form['email'].strip()
        passwd1 = request.form['passwd1'].strip()
        passwd2 = request.form['passwd2'].strip()
        
        if passwd1 != passwd2:
            flash(u'Hasła nie są takie same', 'error')
            return render_template('register.html',
                                   email=email,
                                   first=randint(1,20),
                                   second=randint(1,20))

        if len(passwd1) == 0:
            flash(u'Hasło jest puste', 'error')
            return render_template('register.html',
                                   email=email,
                                   first=randint(1,20),
                                   second=randint(1,20))

        if len(email) == 0 or \
                not re.match('^[a-zA-Z0-9._%-]+@[a-zA-Z0-9._%-]+.[a-zA-Z]{2,6}$', email):
            flash(u'Adres email ma zły format', 'error')
            return render_template('register.html',
                                   first=randint(1,20),
                                   second=randint(1,20))

        if (request.form['result'].strip().isdigit() == False) or \
                    (int(request.form['first'].strip()) + \
                     int(request.form['second'].strip()) != \
                     int(request.form['result'].strip())):
            flash(u'Wprowadzony wynik jest niepoprawny', 'error')
            return render_template('register.html',
                                   email=email,
                                   first=randint(1,20),
                                   second=randint(1,20))
            
        if query_db('SELECT id FROM users WHERE email=%s LIMIT 1',
                (email,), one=True) is not None:
            flash(u'Podany email jest już w użyciu', 'error')
            return render_template('register.html', 
                                   email=email,
                                   first=randint(1,20),
                                   second=randint(1,20))
        
        salt = gen_filename()
        

        if query_db('INSERT INTO users (passwd,salt,email,string_id) '
                 'VALUES (%s,%s,%s,%s)',
                 (sha256(passwd1+\
                         salt+app.config['SALT']).hexdigest(),
                  salt,email, gen_filename())):
            flash(u'Konto zostało utworzone pomyślnie.', 'success')

            # Automatically logging the user
            ret = query_db('SELECT id, string_id FROM users '
                           'WHERE email=%s LIMIT 1', (email,), one=True)
            log_me_in(ret['id'],email,ret['string_id'])
            flash(u'Zostałeś zalogowany', 'success')

        else:
            flash(u'Nastąpił błąd przy rejestracji', 'error')
        return redirect(url_for('home'))
    return render_template('register.html', first=randint(1,20), second=randint(1,20))

