from . import users_blueprint
from flask import current_app, render_template, request, flash, url_for, redirect, abort, copy_current_request_context
from .forms import RegistrationForm, LoginForm
from project.models import User
from project import database, mail
from sqlalchemy.exc import IntegrityError
from markupsafe import escape
from flask_login import login_user, current_user, login_required, logout_user
from urllib.parse import urlparse
from flask_mail import Message
from threading import Thread

@users_blueprint.route('/about')
def about():
    return render_template('users/about.html', nameOfperson='Hamza')

@users_blueprint.errorhandler(403)
def page_forbidden(e):
    return render_template('users/403.html'), 403

@users_blueprint.route('/admin')
def admin():
    abort(403)

@users_blueprint.route('/register', methods=['GET', 'POST'])
def register():
    form = RegistrationForm()

    if request.method == 'POST':
        if form.validate_on_submit():
            try:
                new_user = User(form.email.data, form.password.data)
                database.session.add(new_user)
                database.session.commit()
                flash(f'Thanks for registering, {new_user.email}!')
                current_app.logger.info(f'Registered new user: {form.email.data}!')

                @copy_current_request_context
                def send_email(message):
                    with current_app.app_context():
                        mail.send(message)

                msg = Message(subject='Registration - Hamza E-Commerce Website',
                              body='Thanks for signing up with My E-Commerce Website!',
                              recipients=[form.email.data])
                email_thread = Thread(target=send_email, args=[msg])
                email_thread.start()

                return redirect(url_for('users.login'))
            except IntegrityError:
                database.session.rollback()
                flash(f'ERROR! Email ({form.email.data}) already exists.', 'error')
        else:
            flash(f"Error in form data!")

    return render_template('users/register.html', form=form)

@users_blueprint.route('/hello/<path:message>')
def print_path(message):
    return f'<h1>Path provided: {escape(message)}!</h1>'

@users_blueprint.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        flash('Already logged in!')
        current_app.logger.info(f'Duplicate login attempt by user: {current_user.email}')
        return redirect(url_for('products.index'))
    
    form = LoginForm()

    if request.method == 'POST':
        if form.validate_on_submit():
            query = database.select(User).where(User.email == form.email.data)
            user = database.session.execute(query).scalar_one_or_none()

            if user and user.is_password_correct(form.password.data):
                login_user(user, remember=form.remember_me.data)
                flash(f'Thanks for logging in, {current_user.email}!')
                current_app.logger.info(f'Logged in user: {current_user.email}')

                if not request.args.get('next'):
                    return redirect(url_for('users.user_profile'))
                
                next_url = request.args.get('next')
                if urlparse(next_url).scheme != '' or urlparse(next_url).netloc != '':
                    current_app.logger.info(f'Invalid next path in login request: {next_url}')
                    logout_user()
                    return abort(400)

                current_app.logger.info(f'Redirecting after valid login to: {next_url}')
                return redirect(next_url)
            
        flash('ERROR! Incorrect login credentials.')
    return render_template('users/login.html', form=form)

@users_blueprint.route('/logout')
@login_required
def logout():
    current_app.logger.info(f'Logged out user: {current_user.email}')
    logout_user()
    flash('Goodbye!')
    return redirect(url_for('products.index'))


@users_blueprint.route('/profile')
@login_required
def user_profile():
    return render_template('users/profile.html')

@users_blueprint.route('/confirm/<token>')
def confirm_email(token):
    try:
        confirm_serializer = URLS

@users_blueprint.route('/resend_email_confirmation')
@login_required
def resend_email_confirmation():
    @copy_current_request_context
    def send_email(email_message):
        with current_app.app_context():
            mail.send(email_message)

    message = generate_confirmation_email(current_user.email)
    email_thread = Thread(target=send_email, args=[message])
    email_thread.start()

    flash('Email sent to confirm your email address. Please check your email!', 'success')
    current_app.logger.info(f'Email re-sent to confirm email address for user: {current_user.email}')
    return redirect(url_for('users.user_profile'))