# coding=utf-8

"""定义数据库的models"""
import hashlib

from flask import current_app
from flask_login import UserMixin, AnonymousUserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer
from app import db, login_manager


class Permission:
    """权限管理"""
    FOLLOW = 0x01
    COMMENT = 0x02
    WRITE_ARTICLES = 0x04
    MODERATE_COMMENTS = 0x08
    ADMINISTER = 0x08


class Role(db.Model):
    """角色"""
    __tablename__ = "roles"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), unique=True)
    default = db.Column(db.Boolean, default=False, index=True)
    permissions = db.Column(db.Integer)
    users = db.relationship("User", backref="role", lazy="dynamic")

    @staticmethod
    def insert_roles():
        roles = {
            'User': (Permission.FOLLOW |

                     Permission.COMMENT |
                     Permission.WRITE_ARTICLES, True),
            'Moderator': (Permission.FOLLOW |
                          Permission.COMMENT |
                          Permission.WRITE_ARTICLES |
                          Permission.MODERATE_COMMENTS, False),
            'Administrator': (0xff, False)
        }
        for r in roles:
            role = Role.query.filter_by(name=r).first()
            if role is None:
                role = Role(name=r)
            role.permissions = roles[r][0]
            role.default = roles[r][1]
            db.session.add(role)
        db.session.commit()

    def __repr__(self):
        return "<Role %r>" % self.name


class Follow(db.Model):
    __tablename__ = 'follows'
    # 关注者
    follower_id = db.Column(db.Integer, db.ForeignKey('users.id'),
                            primary_key=True)
    # 被关注者
    followed_id = db.Column(db.Integer, db.ForeignKey('users.id'),
                            primary_key=True)


class User(db.Model, UserMixin):
    """用户信息"""
    __tablename__ = "users"
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(64), unique=True, index=True)
    sex = db.Column(db.String(20))
    short_intr = db.Column(db.String(30))
    introduction = db.Column(db.String(100))
    location = db.Column(db.String(64))
    industry = db.Column(db.String(64))
    school = db.Column(db.String(64))
    discipline = db.Column(db.String(64))
    username = db.Column(db.String(30), nullable=False)
    password_hash = db.Column(db.String(128))
    avatar = db.Column(db.LargeBinary(length=2048))
    confirmed = db.Column(db.Boolean, default=True)
    role_id = db.Column(db.Integer, db.ForeignKey("roles.id"))

    # followed代表followed_id字段为自身的所有实例。
    followed = db.relationship('Follow',
                               foreign_keys=[Follow.follower_id],
                               backref=db.backref('follower', lazy='joined'),
                               lazy='dynamic',
                               cascade='all, delete-orphan')
    # User为一，Follow为多，这是向Follow表中添加followed属性，foreign_keys代表是外键followed_id的关系。代表被关注者本身。
    followers = db.relationship('Follow',
                                foreign_keys=[Follow.followed_id],
                                backref=db.backref('followed', lazy='joined'),
                                lazy='dynamic',
                                cascade='all, delete-orphan')

    def __init__(self, **kwargs):
        super(User, self).__init__(**kwargs)
        # if self.role is None:
        #     if self.email == current_app.config['FLASKY_ADMIN']:
        #         self.role = Role.query.filter_by(permissions=0xff).first()
        #     if self.role is None:
        #         self.role = Role.query.filter_by(default=True).first()

    @property
    def password(self):
        raise AttributeError('password is not a readable attribute')

    @password.setter
    def password(self, password):
        """设置密码"""
        self.password_hash = generate_password_hash(password)

    def verify_password(self, password):
        """验证密码"""
        return check_password_hash(self.password_hash, password)

    def generate_confirmation_token(self, expiration=3600):
        s = Serializer(current_app.config['SECRET_KEY'], expiration)
        return s.dumps({'confirm': self.id})

    def confirm(self, token):
        s = Serializer(current_app.config['SECRET_KEY'])
        try:
            data = s.loads(token)
        except:
            return False
        if data.get('confirm') != self.id:
            return False
        self.confirmed = True
        db.session.add(self)
        db.session.commit()
        return True

    def change_password(self, newpassword):
        """修改密码"""
        try:
            self.password = newpassword
            db.session.add(self)
            db.session.commit()
        except:
            return False
        return True

    def generate_email_change_token(self, new_email, expiration=3600):
        """生成邮箱秘钥"""
        s = Serializer(current_app.config['SECRET_KEY'], expiration)
        return s.dumps({'change_email': self.id, 'new_email': new_email})

    def change_email(self, token):
        """修改邮箱"""
        s = Serializer(current_app.config['SECRET_KEY'])
        try:
            data = s.loads(token)
        except:
            return False
        if data.get('change_email') != self.id:
            return False
        new_email = data.get('new_email')
        if new_email is None:
            return False
        if self.query.filter_by(email=new_email).first() is not None:
            return False
        self.email = new_email
        try:
            db.session.add(self)
            db.session.commit()
        except:
            return False
        return True

    def follow(self, user):
        if not self.is_following(user):
            f = Follow(followed=user)
            self.followed.append(f)
            print self.followed.count()

    def unfollow(self, user):
        f = self.followed.filter_by(followed_id=user.id).first()
        if f:
            self.followed.remove(f)

    def is_following(self, user):
        return self.followed.filter_by(
            followed_id=user.id).first() is not None

    def is_followed_by(self, user):
        return self.followers.filter_by(
            follower_id=user.id).first() is not None

    def change_avatar(self, images):
        """改变头像"""
        try:
            self.avatar = images
            db.session.add(self)
            db.session.commit()
        except:
            return False
        return True


class AnonymousUser(AnonymousUserMixin):
    def can(self, permissions):
        return False

    def is_administrator(self):
        return False

login_manager.anonymous_user = AnonymousUser


@login_manager.user_loader
def load_user(user_id):
    """返回唯一标识符"""
    return User.query.get(int(user_id))
