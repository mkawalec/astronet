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
        user = query_db('SELECT id,passwd,real_name,email,salt,string_id,role '
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
                    
                    log_me_in(user['id'],user['email'],user['string_id'],
                            user['real_name'],user['role'])
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


@app.route('/user/edit', methods=['GET', 'POST'])
@login_required
def edit_profile():
    """ One can manage user's profile profile. Change real name,
    password or email."""
    #TODO: browser fills some form fields (for example mail and old pass) with login data and this is inconvenient when you change real name - you have to delete other forms, other way you've got error. Maybe new names for this fields will be nice. Changing field name doesnt work!
    if request.method == 'POST':
        email1 = request.form['email1'].strip()
        email2 = request.form['email2'].strip()
        real_name = request.form['real_name'].strip()
        
        if len(real_name) != 0:
            if query_db('UPDATE users SET real_name=%s WHERE id=%s', (real_name,session["uid"])):
                flash(u'Uaktualniono Twoje imię i naziwsko', 'success')
            else:
                flash(u'Wystąpił błąd bazy danych', 'error')
        else:
            pass
        
        
        if (len(email1) == 0) and (len(email2) == 0):
            pass
        elif (len(email1) == 0) or\
                (len(email2) == 0) or\
                not re.match('^[a-zA-Z0-9._%-]+@[a-zA-Z0-9._%-]+.'
                    '[a-zA-Z]{2,6}$', email1) or\
                not re.match('^[a-zA-Z0-9._%-]+@[a-zA-Z0-9._%-]+.'
                    '[a-zA-Z]{2,6}$', email2) or\
                query_db('SELECT id from users WHERE email=%s LIMIT 1', 
                    (email1,)) :
            flash(u'Wprowadzono niepoprawny adres email '
                u'lub podany adres jest już zajęty', 'error')
            return render_template('edit_profile.html',)
        elif (len(email1) != 0) and (len(email1) != 0) and \
                                    email1 == email2:
            if query_db('UPDATE users SET email=%s WHERE '
                    'id=%s', (email1,session["uid"])):
                flash(u'Uaktualniono Twój nowy adres email', 'success')
            else:
                flash(u'Wystąpił błąd bazy danych', 'error')
        else:
            flash(u'Wprowadzono niepoprawny adres email', 'error')
            
        passwd_old = request.form['passwd_old'].strip()
        passwd1 = request.form['passwd1'].strip()
        passwd2 = request.form['passwd2'].strip()
        if len(passwd1) == 0 and len(passwd2) == 0 and\
                        len(passwd_old) == 0:
            pass
        else:
            error = False
            if passwd1 != passwd2:
                flash(u'Hasła nie są takie same', 'error')
                error = True

            if len(passwd1) == 0 or len(passwd2) == 0:
                flash(u'Hasło jest puste', 'error')
                error = True
            
            user_data = query_db('SELECT passwd, salt FROM users '
                        'WHERE id=%s LIMIT 1', (session["uid"],), one=True)
            if (sha256(passwd_old+user_data['salt']+\
                       app.config['SALT']).hexdigest()) !=\
                       user_data["passwd"]:
                flash(u'Nieprawidłowe hasło', 'error')
                error = True
            
            if not error and query_db('UPDATE users SET passwd=%s WHERE id=%s',
                        (sha256(passwd1+user_data['salt']+\
                        app.config['SALT']).hexdigest(),
                        session['uid'])):
                flash(u'Hasło zostało zmienione', 'success')
            else:
                flash(u'Wystąpił błąd bazy danych', 'error')
    return render_template('edit_profile.html',)




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
        
        user_data = query_db('SELECT id FROM users WHERE email=%s LIMIT 1',
                    (email,), one=True)
        if user_data is None:
            flash(u'Podany adres nie występuje w bazie', 'error')
            return render_template('reset_pass.html')                
        
        new_hash = gen_filename(10)
        if query_db('INSERT INTO hashes (hash_value,owner) VALUES (%s,%s)',
                (new_hash,user_data["id"])):
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

        user_data = query_db('SELECT u.id as uid,u.real_name,u.string_id, '
                  'u.salt,u.email,u.role '
                  'FROM users u, hashes h WHERE h.hash_value=%s AND '
                  '(current_timestamp - h.timestamp) < (\'1 day\')::interval AND '
                  'u.id=h.owner ORDER BY h.timestamp DESC LIMIT 1',
                   (hash,), one=True)
        if not user_data:
            flash(u'Błędy kod aktywacyjny', 'error')
            return redirect(url_for('home'))

        if query_db('UPDATE users SET passwd=%s '
                    'WHERE id=%s', (sha256(request.form['passwd1'].strip()+\
                            user_data['salt']+app.config['SALT']).hexdigest(),
                            user_data['uid'])):
            query_db('DELETE FROM hashes WHERE hash_value=%s',
                                        (hash,))
            flash(u'Hasło zostało zmienione.', 'success')
            log_me_in(user_data['uid'],user_data['email'],user_data['string_id'],user_data['real_name'],user_data['role'])
            flash(u'Zostałeś zalogowany', 'success')
            return redirect(url_for('home'))
        else:
            flash(u'Błąd bazy danych', 'error')

    # We need to check if the reset hash is correct here
    # for instance in case of someone wrongly entering the hash
    correct_hash = query_db('SELECT u.id,h.timestamp FROM '
               'users u, hashes h WHERE h.hash_value=%s AND u.id=h.owner AND '
               '(current_timestamp - h.timestamp) < (\'1 day\')::interval '
               'ORDER BY h.timestamp DESC LIMIT 1',
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
        real_name = request.form['real_name'].strip()

        if len(real_name) < 5:
            flash(u'Podane imię jest za krótkie')
            return render_template('register.html',
                                   email=email,
                                   first=randint(1, 20),
                                   second=randint(1,20))
        
        if passwd1 != passwd2:
            flash(u'Hasła nie są takie same', 'error')
            return render_template('register.html',
                                   email=email,
                                   real_name=real_name,
                                   first=randint(1,20),
                                   second=randint(1,20))

        if len(passwd1) == 0:
            flash(u'Hasło jest puste', 'error')
            return render_template('register.html',
                                   email=email,
                                   real_name=real_name,
                                   first=randint(1,20),
                                   second=randint(1,20))

        if len(email) == 0 or \
                not re.match('^[a-zA-Z0-9._%-]+@[a-zA-Z0-9._%-]+.[a-zA-Z]{2,6}$', email):
            flash(u'Adres email ma zły format', 'error')
            return render_template('register.html',
                                   first=randint(1,20),
                                   real_name=real_name,
                                   second=randint(1,20))

        if (request.form['result'].strip().isdigit() == False) or \
                    (int(request.form['first'].strip()) + \
                     int(request.form['second'].strip()) != \
                     int(request.form['result'].strip())):
            flash(u'Wprowadzony wynik jest niepoprawny', 'error')
            return render_template('register.html',
                                   email=email,
                                   real_name=real_name,
                                   first=randint(1,20),
                                   second=randint(1,20))
            
        if query_db('SELECT id FROM users WHERE email=%s LIMIT 1',
                (email,), one=True) is not None:
            flash(u'Podany email jest już w użyciu', 'error')
            return render_template('register.html', 
                                   email=email,
                                   real_name=real_name,
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
            ret = query_db('SELECT id, string_id, real_name, role FROM users '
                           'WHERE email=%s LIMIT 1', (email,), one=True)
            log_me_in(ret['id'],email,ret['string_id'],ret['real_name'],ret['role'])
            flash(u'Zostałeś zalogowany', 'success')

        else:
            flash(u'Nastąpił błąd przy rejestracji', 'error')
        return redirect(url_for('home'))
    return render_template('register.html', 
                           first=randint(1,20), 
                           second=randint(1,20))


@app.route('/admin', methods=['GET'])
@login_required
def show_admin_panel():
    """ Shows admin panel. Allows to manage users (change roles, remove) """
    if session['role'] != 'admin':
        flash(u'Nie masz wystarczających uprawnień.', 'error')
        return redirect(url_for('home'))

    keys = ['id', 'email', 'real_name', 'disabled', 'role', 'timestamp']
    sort_by = 'id'
    if 'sort_by' in request.args:
        if keys.index(request.args['sort_by']) != ValueError:
            sort_by = request.args['sort_by']
    if 'desc' in request.args:
        sort_by += ' DESC'
    users = query_db('SELECT id, email, real_name, disabled, role, timestamp '
                     'FROM users ORDER BY %s' % (sort_by))
    return render_template('admin.html', users=users)

@app.route('/admin/manage_user', methods=['GET', 'POST'])
@login_required
def manage_user():
    # TODO: remove user
    if session['role'] != 'admin':
        flash(u'Nie masz wystarczających uprawnień.', 'error')
        return redirect(url_for('home'))

    roles = ['user', 'admin', 'redaktor']
    if request.method == 'POST':
        user_id = int(request.form['user_id'])
        user = query_db('SELECT email, real_name, disabled, role '
                        'FROM users WHERE id=%s', (user_id,), one=True)
        
        email = request.form['email'].strip()
        real_name = request.form['real_name'].strip()
        role = request.form['role'].strip()
        disabled = ('disabled' in request.form)
        delete = ('delete' in request.form)

        if len(real_name) != 0 and real_name != user['real_name']:
            if query_db('UPDATE users SET real_name=%s WHERE id=%s',
                        (real_name,user_id)):
                flash(u'Uaktualniono imię i naziwsko', 'success')
            else:
                flash(u'Wystąpił błąd bazy danych', 'error')
        

        if email == user['email']:
            pass
        elif len(email) == 0 or\
                not re.match('^[a-zA-Z0-9._%-]+@[a-zA-Z0-9._%-]+.'
                    '[a-zA-Z]{2,6}$', email) or\
                query_db('SELECT id FROM users WHERE email=%s LIMIT 1', 
                    (email,)):
            flash(u'Wprowadzono niepoprawny adres email '
                u'lub podany adres jest już zajęty', 'error')
        else:
             if query_db('UPDATE users SET email=%s WHERE '
                    'id=%s', (email,user_id)):
                flash(u'Uaktualniono adres email', 'success')
             else:
                flash(u'Wystąpił błąd bazy danych', 'error')
        

        if role == user['role']:
            pass
        elif role in roles:
            if query_db('UPDATE users SET role=%s WHERE id=%s',
                        (role, user_id)):
                flash(u'Uaktualniono rolę', 'success')
            else:
                flash(u'Wystąpił błąd bazy danych', 'error')
        else:
            flash(u'Wprowadzono niepoprawną rolę', 'error')


        if disabled != user['disabled']:
            if query_db('UPDATE users SET disabled=%s WHERE id=%s',
                        (disabled,user_id)):
                flash(u'Uaktualniono stan zablokowania', 'success')
            else:
                flash(u'Wystąpił błąd bazy danych', 'error')
                
        if delete:
            if query_db('DELETE FROM users WHERE id=%s',
                        (user_id,)):
                flash(u'Użytkownik został usunięty', 'success')
            else:
                flash(u'Wystąpił błąd bazy danych', 'error')


        return redirect(url_for('show_admin_panel'))
    else:
        user_id = int(request.args['user_id'])
        user = query_db('SELECT id, email, real_name, disabled, role, timestamp '
                        'FROM users WHERE id=%s', (user_id,), one=True)
        return render_template('manage_user.html', user=user, roles=roles)

