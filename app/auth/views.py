# coding=utf-8
from flask_login import login_user, login_required, logout_user, current_user
from flask import render_template, redirect, url_for, request, flash

from app import db
from app.auth import auth
from app.auth.forms import LoginForm, RegistrationForm, ChangepasswordForm, ChangeEmailForm
from app.helpers.email import send_email
from app.models.models import User


@auth.before_app_request
def before_request():
    if current_user.is_authenticated:
        if not current_user.confirmed \
                and request.endpoint[:5] != 'auth.'\
                and request.endpoint != 'static':
            return redirect(url_for('auth.unconfirmed'))


@auth.route('/login', methods=['GET', 'POST'])
def login_register():
    login_form = LoginForm()
    register_form = RegistrationForm()
    # 进行登录表单的验证
    if login_form.submit1.data and login_form.validate_on_submit():
        user = User.query.filter_by(email=login_form.email.data).first()
        if user is not None and user.verify_password(login_form.password.data):
            login_user(user, login_form.remember_me.data)
            return redirect(url_for('main.index'))
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
    return redirect(url_for('main.index'))


@auth.route('/confirm/<token>')
@login_required
def confirm(token):
    if current_user.confirmed:
        return redirect(url_for('main.index'))
    if current_user.confirm(token):
        flash(u'账户验证成功')
    else:
        flash(u'验证链接已过期或无效.')
    return redirect(url_for('main.index'))


@auth.route('/unconfirmed')
def unconfirmed():
    if current_user.is_anonymous or current_user.confirmed:
        return redirect(url_for('main.index'))
    return render_template('auth/unconfirmed.html', user=current_user)


@auth.route('/confirm')
@login_required
def resend_confirmation():
    """进行验证邮箱的重新发送"""
    token = current_user.generate_confirmation_token()
    send_email(current_user.email, 'Confirm Your Account',
               'auth/email/confirm', user=current_user, token=token)
    flash(u'验证邮件已发送到你的邮箱')
    return redirect(url_for('main.index'))


@auth.route('/settings', methods=['GET', 'POST'])
@login_required
def settings():
    return redirect(url_for("auth.profile"))


@auth.route('/settings/profile', methods=['GET', 'POST'])
@login_required
def profile():
    """账户邮箱设置"""
    form = ChangeEmailForm()
    if form.validate_on_submit():
        if current_user.verify_password(form.password.data):
            new_email = form.email.data
            token = current_user.generate_email_change_token(new_email)
            send_email(new_email, 'Confirm your email address',
                       'auth/email/change_email',
                       user=current_user, token=token)
            flash(u'验证已发送到你的邮箱')
            return redirect(url_for('auth.profile'))
        else:
            flash(u'密码错误')
    return render_template("email_settings.html", user=current_user, form=form)


@auth.route('/change-email/<token>')
@login_required
def change_email(token):
    if current_user.change_email(token):
        flash(u'邮箱账户已修改')
    else:
        flash(u'未修改成功')
    return redirect(url_for('auth.profile'))


@auth.route('/settings/password', methods=['GET', 'POST'])
@login_required
def password():
    """用户密码设置"""
    form = ChangepasswordForm()
    if form.validate_on_submit():
        if current_user.verify_password(form.oldpassword.data):
            if current_user.change_password(form.password.data):
                flash(u"密码设置成功")
                logout_user()
                return redirect(url_for('auth.login_register'))
            else:
                flash(u'未能设置成功')
        else:
            flash(u"密码错误")

    return render_template("password_settings.html", user=current_user, form=form)
