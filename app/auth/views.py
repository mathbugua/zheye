# coding=utf-8
from flask_login import login_user, login_required, logout_user
from flask import render_template, redirect, url_for, request, flash

from app import db
from app.auth import auth
from app.auth.forms import LoginForm, RegistrationForm
from app.helpers.email import send_email
from app.models.models import User


@auth.route('/login', methods=['GET', 'POST'])
def login_register():
    login_form = LoginForm()
    register_form = RegistrationForm()
    # 进行登录表单的验证
    if login_form.submit1.data and login_form.validate_on_submit():
        user = User.query.filter_by(email=login_form.email.data).first()
        if user is not None and user.verify_password(login_form.password.data):
            login_user(user, login_form.remember_me.data)
            return redirect(request.args.get('next') or url_for('main.index'))
        flash(u'错误的用户名或密码.')

    # 进行注册表单的验证
    if register_form.submit2.data and register_form.validate_on_submit():
        user = User(email=register_form.email.data,
                    username=register_form.username.data,
                    password=register_form.password.data)
        db.session.add(user)
        db.session.commit()
        try:
            token = user.generate_confirmation_token()
            send_email(user.email, 'Confirm Your Account',
                       'auth/email/confirm', user=user, token=token)
            flash(u'验证邮件已发送到你的邮箱，请先登录')
        except Exception as e:
            print e
        return redirect(url_for('auth.login_register'))

    return render_template('auth/login.html', form1=login_form, form2=register_form)


@auth.route('/logout')
@login_required
def logout():
    logout_user()
    flash('You have been logged out.')
    return redirect(url_for('main.index'))


# @auth.route('/register', methods=['GET', 'POST'])
# def register():
#     form = RegistrationForm()
#     if form.validate_on_submit():
#         user = User(email=form.email.data,
#                     username=form.username.data,
#                     password=form.password.data)
#         db.session.add(user)
#         db.session.commit()
#         # token = user.generate_confirmation_token()
#         # send_email(user.email, 'Confirm Your Account',
#         #            'auth/email/confirm', user=user, token=token)
#         # flash('A confirmation email has been sent to you by email.')
#         return redirect(url_for('auth.login'))
#     return render_template('auth/register.html', form=form)
