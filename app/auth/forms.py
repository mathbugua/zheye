# coding=utf-8
from flask_wtf import Form
from wtforms import StringField, PasswordField, BooleanField, SubmitField, FileField, SelectField
from wtforms.validators import Required, Length, Email, Regexp, EqualTo, ValidationError

from app.models.models import User, TopicCategory, Role


class LoginForm(Form):
    email = StringField('Email', validators=[Required(), Length(1, 64),
                                             Email()])
    password = PasswordField('Password', validators=[Required()])
    remember_me = BooleanField('Keep me logged in')
    submit1 = SubmitField('Log In')


class RegistrationForm(Form):
    email = StringField('Email', validators=[Required(), Length(1, 64),
                                           Email()])
    username = StringField('Username', validators=[
        Required(), Length(1, 64), Regexp('^[A-Za-z][A-Za-z0-9_.]*$', 0,
                                          'Usernames must have only letters, '
                                          'numbers, dots or underscores')])
    password = PasswordField('Password', validators=[
        Required(), EqualTo('password2', message='Passwords must match.')])
    password2 = PasswordField('Confirm password', validators=[Required()])
    submit2 = SubmitField('Register')

    def validate_email(self, field):
        if User.query.filter_by(email=field.data).first():
            raise ValidationError('Email already registered.')

    def validate_username(self, field):
        if User.query.filter_by(username=field.data).first():
            raise ValidationError('Username already in use.')


class ChangepasswordForm(Form):
    """修改密码"""
    oldpassword = PasswordField(u'原始密码', validators=[Required()])
    password = PasswordField(u'新密码', validators=[
        Required(), EqualTo('password2', message='Passwords must match.')])
    password2 = PasswordField(u'再次输入', validators=[Required()])
    submit = SubmitField(u'保存')


class ChangeEmailForm(Form):
    """修改邮箱"""
    email = StringField(u'新邮箱', validators=[Required(), Length(1, 64),
                                                 Email()])
    password = PasswordField(u'密码', validators=[Required()])
    submit = SubmitField(u'保存')

    def validate_email(self, field):
        if User.query.filter_by(email=field.data).first():
            raise ValidationError('Email already registered.')


class InsertCategory(Form):
    category_name = StringField(u'类别名称', validators=[Required(), Length(0, 30)])
    category_desc = StringField(u'描述', validators=[Length(0, 300)])
    submit = SubmitField(u'保存')


class InsertTopic(Form):
    topic_name = StringField(u'话题名称', validators=[Required(), Length(1, 30)])
    topic_desc = StringField(u'话题描述', validators=[Length(0, 300)])
    topic_cate = SelectField(u'话题类别', coerce=int, validators=[Required()])
    submit = SubmitField(u'保存')

    def __init__(self, *args, **kwargs):
        super(InsertTopic, self).__init__(*args, **kwargs)
        self.topic_cate.choices = [(cate.id, cate.category_name) for cate in TopicCategory.query.all()]


class EditProfileAdminForm(Form):
    email = StringField(u'邮箱', validators=[Required(), Length(1, 64),
                                             Email()])
    username = StringField(u'用户名', validators=[
        Required(), Length(1, 64), Regexp('^[A-Za-z][A-Za-z0-9_.]*$', 0,
                                          'Usernames must have only letters, '
                                          'numbers, dots or underscores')])
    name = StringField(u'姓名', validators=[Length(0, 64)])
    confirmed = BooleanField(u'验证')
    role = SelectField(u'角色', coerce=int)
    submit = SubmitField(u'提交')

    def __init__(self, user, *args, **kwargs):
        super(EditProfileAdminForm, self).__init__(*args, **kwargs)
        self.role.choices = [(role.id, role.name)
                             for role in Role.query.order_by(Role.name).all()]
        self.user = user

    def validate_email(self, field):
        if field.data != self.user.email and \
                User.query.filter_by(email=field.data).first():
            raise ValidationError('Email already registered.')

    def validate_username(self, field):
        if field.data != self.user.username and \
                User.query.filter_by(username=field.data).first():
            raise ValidationError('Username already in use.')

    def validate_name(self, field):
        if field.data != self.user.name and \
                User.query.filter_by(name=field.data).first():
            raise ValidationError('name already in use.')