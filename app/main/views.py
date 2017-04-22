# coding=utf-8

from flask import redirect, flash
from flask import render_template
from flask import url_for
from flask_login import login_required, current_user

from app import db
from app.main.forms import EditProfileForm
from app.models.models import User
from . import main


@main.route("/")
@login_required
def index():
    return render_template("zheye.html", user=current_user)


@main.route('/people/<username>')
def people(username):
    """个人资料界面"""
    user = User.query.filter_by(username=username).first_or_404()
    return render_template('user.html', user=user)


@main.route('/edit-profile', methods=['POST', 'GET'])
@login_required
def edit_profile():
    """编辑个人资料"""
    form = EditProfileForm()
    if form.validate_on_submit():
        current_user.username = form.username.data
        current_user.location = form.location.data
        current_user.sex = form.sex.data
        current_user.short_intr = form.short_intr.data
        current_user.school = form.school.data
        current_user.industry = form.industry.data
        current_user.discipline = form.discipline.data
        current_user.introduction = form.introduction.data
        db.session.add(current_user)
        db.session.commit()
        flash('Your profile has been updated')
        return redirect(url_for('main.people', username=current_user.username))

    form.username.data = current_user.username
    form.sex.data = current_user.sex or "man"
    form.short_intr.data = current_user.short_intr
    form.industry.data = current_user.industry
    form.school.data = current_user.school
    form.discipline.data = current_user.discipline
    form.introduction.data = current_user.introduction
    form.location.data = current_user.location

    return render_template('edit_profile.html', form=form, user=current_user)
