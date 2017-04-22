# coding=utf-8
from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, SubmitField, RadioField
from wtforms.validators import Length, Required


class EditProfileForm(FlaskForm):
    username = StringField(u'用户名', validators=[Required(), Length(0, 64)])
    sex = RadioField(u'性别', choices=[('man', u'男'), ('woman', u'女')], default='man')
    location = StringField(u'居住地', validators=[Length(0, 64)])
    short_intr = StringField(u'一句话介绍', validators=[Length(0, 30)])
    industry = StringField(u'所在行业', validators=[Length(0, 64)])
    school = StringField(u'学校', validators=[Length(0, 64)])
    discipline = StringField(u'专业方向', validators=[Length(0, 64)])
    introduction = TextAreaField(u'简介', validators=[Length(0, 100)])
    submit = SubmitField(u'确定')