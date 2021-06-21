from flask import render_template, url_for, flash, redirect, request, abort
from flaskauth import app, db, bcrypt, mail
from flaskauth.forms import RegistrationForm, LoginForm, UpdateAccountForm, RequestResetForm, ResetPasswordForm
from flaskauth.db_models import User
from flask_login import login_user, current_user, logout_user, login_required
from flask_mail import Message

@app.route("/")
@app.route("/home")
def home():
    return render_template('home.html', title='Welcome')

@app.route("/login", methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('account'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user and bcrypt.check_password_hash(user.password, form.password.data):
            login_user(user, remember=form.remember.data)
            next_page = request.args.get('next')
            return redirect(next_page) if next_page else redirect(url_for('account'))
        else:
            flash('Login Unsuccessful. Please check email and password.', 'danger')
    return render_template('login.html', title='Login', form=form)


@app.route("/register", methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('account'))
    form = RegistrationForm()
    if form.validate_on_submit():
        hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        user = User(username=form.username.data, email=form.email.data, password=hashed_password)
        db.session.add(user)
        db.session.commit()
        flash(f'Account has been created for {form.username.data}! You are now able to log in.', 'success')
        return redirect(url_for('login'))
    return render_template('register.html', title='User Registration', form=form)

@app.route("/logout")
def logout():
    logout_user()
    return redirect(url_for('login'))


def send_reset_email(user):
    token = user.get_reset_token()
    msg = Message('Password Reset Request',
                  recipients=[user.email])
    msg.body = f'''Hello user,

A password change request has been made for the user account associated with this mail at a Flask Web-Application.

To reset your password, click the following link or copy paste it in a browser: {url_for('passreset_token', token=token, _external=True)} .

If you did not make this request then simply ignore this email and no changes will be made.
'''
    mail.send(msg)


@app.route("/reset_password", methods=['GET', 'POST'])
def passreset_request():
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    form = RequestResetForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        send_reset_email(user)
        flash('An email has been sent with instructions to reset your password.', 'info')
        return redirect(url_for('home'))
    return render_template('passreset_request.html', title='Reset Password', form=form)


@app.route("/reset_password/<token>", methods=['GET', 'POST'])
def passreset_token(token):
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    user = User.verify_reset_token(token)
    if user is None:
        flash('The password reset request link is invalid or has expired.', 'warning')
        return redirect(url_for('passreset_request'))
    form = ResetPasswordForm()
    if form.validate_on_submit():
        hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        user.password = hashed_password
        db.session.commit()
        flash('Your password has been reset! You are now able to log in.', 'success')
        return redirect(url_for('login'))
    return render_template('passreset_token.html', title='Reset Password', form=form)

@app.route("/account", methods=['GET', 'POST'])
@login_required
def account():
    form = UpdateAccountForm()
    if form.validate_on_submit():
        current_user.username = form.username.data
        current_user.email = form.email.data
        db.session.commit()
        flash('Your account has been updated!', 'success')
        return redirect(url_for('account'))
    elif request.method == 'GET':
        form.username.data = current_user.username
        form.email.data = current_user.email
    return render_template('account.html', title='Account', form=form)

@app.errorhandler(404)
def error_404(error):
    return render_template('error.html', title='Error', enum=404, message='Page not found.'), 404

@app.errorhandler(403)
def error_404(error):
    return render_template('error.html', title='Error', enum=403, message='Access restricted.'), 403

@app.errorhandler(413)
def error_404(error):
    return render_template('error.html', title='Error', enum=413, message='Large payload transfer.'), 413

@app.errorhandler(500)
def error_404(error):
    return render_template('error.html', title='Error', enum=500, message='Internal server error.'), 500
