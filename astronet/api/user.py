from ..api import api, auth_required, query_db
from flask import (request, render_template, g, jsonify, abort)



# User name operations
@api.route('/user/name', methods=['GET', 'POST'])
@auth_required
def user_name():
    """ If accessed by **GET** returns the user real_name, if known.
        
        If **POST** is used the real name for the currently authenticated
        user is changed. The **POST** ed parameters must be::

            request.form = {
                'real_name': user_real_name
            }

        The real_name is not used in any operations-critical part of the program
    """
    if request.method == 'POST':
        ret = query_db('UPDATE users SET real_name=%s WHERE id=%s',
                      [(request.form['real_name']).strip(), g.uid])
        if ret == 1:
            return jsonify(status='succ')
        elif ret == -1:
            return jsonify(status='db_constraints_error')
        return jsonify(status='db_error')
    
    if request.method == 'GET':
        ret = query_db('SELECT real_name FROM users WHERE id=%s',
                       [g.uid], one=True)
        if ret == None:
            return jsonify(status='db_null_error')
        return jsonify(status='succ', real_name=ret['real_name'])

# Email operations
@api.route('/user/email', methods=['GET', 'POST'])
@auth_required
def user_email():
    """ Either **GET** s the currently set email or enables the user
        to **POST** a new one
    """
    # Update the email
    if request.method == 'POST':
        ret = query_db('UPDATE users SET email=%s WHERE id=%s',
                       [(request.form['email']).strip(), g.uid])
        if ret == 1:
            return jsonify(status='succ')
        elif ret == -1:
            return jsonify(status='db_constraints_error')
        return jsonify(status='db_error')
    
    # Get the email
    if request.method == 'GET':
        email = query_db('SELECT email FROM users WHERE id=%s',
                         [g.uid], one=True)

        if 'email' not in email:
            return jsonify(status='db_null_error')
        else:
            return jsonify(status='succ', email=email['email'])

# Password change
@api.route('/user/password', methods=['POST'])
@auth_required
def user_password():
    """ Enables the user to change her password """
    passwd = query_db('SELECT salt,passwd FROM users WHERE id=%s',
                    [g.uid], one=True)
    if sha256(request.form['pass_old']+passwd['salt']+app.config['SALT']).hexdigest()!=passwd['passwd']:
        # The old password is incorrect
        return jsonify(status='old_pass_incorrect')

    ret = query_db('UPDATE users SET passwd=%s WHERE id=%s',
                   [sha256(request.form['pass1']+passwd['salt']+app.config['SALT']).hexdigest(),
                    g.uid])
    if ret == -1:
        return jsonify(status='db_constraints_error')
    elif ret == 0:
        return jsonify(status='db_error')
    return jsonify(status='succ')
