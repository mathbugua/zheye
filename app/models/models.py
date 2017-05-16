# coding=utf-8

"""定义数据库的models"""
import calendar
import hashlib

from datetime import datetime
from flask import current_app
from flask_login import UserMixin, AnonymousUserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer
from app import db, login_manager
from .OperateModel import operate_model


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
            operate_model.db_add(role)  # 提交到数据库

    def __repr__(self):
        return "<Role %r>" % self.name


class Comments(db.Model):
    """评论回答"""
    __tablename__ = "comments"
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    answer_id = db.Column(db.Integer, db.ForeignKey("answer.id"))
    content_body = db.Column(db.String(2000), nullable=False)
    content_time = db.Column(db.DateTime(), default=datetime.utcnow)
    comment_type = db.Column(db.String(64), default='comment')
    reply_to = db.Column(db.Integer, db.ForeignKey("users.id"))

    @staticmethod
    def add_comment(answer_id, comment_body, current_user_id):
        """添加评论"""
        comment = Comments(
            user_id=current_user_id,
            answer_id=answer_id,
            content_body=comment_body
        )
        return operate_model.db_add(comment)


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
    name = db.Column(db.String(30), nullable=False)   # 姓名字段
    password_hash = db.Column(db.String(128))
    avatar = db.Column(db.LargeBinary(length=2048))
    confirmed = db.Column(db.Boolean, default=False)
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

    follow_topics = db.relationship("FollowTopic", backref="users",
                                    lazy='dynamic',
                                    cascade='all, delete-orphan'
                                    )

    follow_questions = db.relationship("FollowQuestion", backref="users",
                                      lazy='dynamic',
                                      cascade='all, delete-orphan'
                                      )

    answers = db.relationship("Answer", backref="users",
                                    lazy='dynamic',
                                    cascade='all, delete-orphan'
                                    )

    # 用户与提问题之间是一对多的关系，即一个用户能够提多个问题，而一个问题只属于一个人
    questions = db.relationship("Question", backref="uesrs",
                                lazy='dynamic',
                                cascade='all, delete-orphan'
                                )

    comments = db.relationship("Comments",
                               foreign_keys=[Comments.user_id],
                               backref="comment_user",
                               lazy='dynamic',
                               cascade='all, delete-orphan'
                               )

    replay = db.relationship("Comments",
                               foreign_keys=[Comments.reply_to],
                               backref="replay_user",
                               lazy='dynamic',
                               cascade='all, delete-orphan'
                               )

    def __init__(self, **kwargs):
        super(User, self).__init__(**kwargs)
        if self.role is None:
            if self.email == current_app.config['FLASKY_ADMIN']:
                self.role = Role.query.filter_by(permissions=0xff).first()
            if self.role is None:
                self.role = Role.query.filter_by(default=True).first()

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
        return operate_model.db_add(self)

    def change_password(self, newpassword):
        """修改密码"""
        self.password = newpassword
        return operate_model.db_add(self)

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
        return operate_model.db_add(self)

    def can(self, permissions):
        return self.role is not None and \
            (self.role.permissions & permissions) == permissions

    def is_administrator(self):
        return self.can(Permission.ADMINISTER)

    # 关注人
    def follow(self, user):
        if not self.is_following(user):
            f = Follow(followed=user)
            self.followed.append(f)

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

    # 关注话题
    def follow_topic(self, topic):
        if not self.is_following_topic(topic):
            t = FollowTopic(topic=topic)
            self.follow_topics.append(t)

    def unfollow_topic(self, topic):
        t = self.follow_topics.filter_by(topic_id=topic.id).first()
        if t:
            self.follow_topics.remove(t)

    def is_following_topic(self, topic):
        return self.follow_topics.filter_by(
            topic_id=topic.id).first() is not None

    # 关注问题
    def follow_question(self, question):
        if not self.is_following_question(question):
            q = FollowQuestion(question=question)
            self.follow_questions.append(q)

    def unfollow_question(self, question):
        t = self.follow_questions.filter_by(question_id=question.id).first()
        if t:
            self.follow_questions.remove(t)

    def is_following_question(self, question):
        return self.follow_questions.filter_by(
            question_id=question.id).first() is not None

    def change_avatar(self, images):
        """改变头像"""
        self.avatar = images
        return operate_model.db_add(self)

    def is_answer_question(self, question_id):
        """是否回答了某个问题"""
        return self.answers.filter_by(
            user_id=self.id, question_id=question_id).first() is not None

    def add_dynamic(self, user_id, t_q_id, type):
        """添加个人动态记录"""
        dynamic = Dynamic(
            user_id=user_id,
            t_q_id=t_q_id,
            type=type
        )
        return operate_model.db_add(dynamic)

    def notify_follower(self, target_id, operate_type):
        """把当前用户的动态通知给他的关注者"""
        for user in self.followers.all():  # 遍历当前用户的所有关注者
            self.notify_message(user.follower.id, self.id,
                                target_id, operate_type)

    def notify_message(self, follower_id, followed_id,
                       target_id, operate_type):
        """记录添加到数据库"""
        update = FriendUpdates(
            follower_id=follower_id,
            followed_id=followed_id,
            target=target_id,
            type=operate_type
        )
        return operate_model.db_add(update)

    def current_user_index(self):
        """
        当前用户的首页数据展示;
            - 关注的用户的动态
            - 关注的话题的下问题的展示
        """
        index_show = list()    # 存储首页显示的数据
        # 存储关注的话题下的问题及优秀回答
        for topic in self.follow_topics.all():
            questions_excellans = topic.topic.questions_excellans()
            # 添加内容的类型
            [questions_excellan.append("current_user_follow") for questions_excellan in questions_excellans]
            if questions_excellans:
                index_show.extend(questions_excellans)

        # 存储关注的用户的动态
        search_notes = FriendUpdates.search_notes(self.id)
        if search_notes:
            index_show.extend(search_notes)

        return sorted(index_show)


class Dynamic(db.Model):
    """用户个人动态,存放用户关注的话题,问题记录"""
    __tablename__ = "dynamic"
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"))
    t_q_id = db.Column(db.Integer)   # 存放话题或问题id
    dynamic_time = db.Column(db.DateTime(), default=datetime.utcnow)
    type = db.Column(db.String(20))  # type = "question" or "topic"

    @staticmethod
    def search_dynamic(user_id):
        """查询个人动态以备显示"""
        dynamic_note_list = list()
        dynamic = Dynamic.query.filter_by(user_id=user_id).order_by(Dynamic.dynamic_time.desc()).all()
        for item in dynamic:
            stored = []
            if item.type == "question":
                question = Question.query.filter_by(id=item.t_q_id).first()
                if question:
                    stored.append("question")
                    stored.append(question)
                    stored.append(item.dynamic_time)
                    dynamic_note_list.append(stored)
            else:
                topic = Topic.query.filter_by(id=item.t_q_id).first()
                if topic:
                    stored.append("topic")
                    stored.append(topic)
                    stored.append(item.dynamic_time)
                    dynamic_note_list.append(stored)
        return dynamic_note_list    # 返回一个嵌套列表[["type", 对象, "time"]]


class FriendUpdates(db.Model):
    """
    记录关注的人的动态,以供在首页进行展示:
    type: "关注用户", "关注话题", "关注问题", "回答了问题","提问"
    """
    id = db.Column(db.Integer, primary_key=True)
    follower_id = db.Column(db.Integer)  # 关注者
    followed_id = db.Column(db.Integer)  # 被关注者,即记录的发生者
    target = db.Column(db.Integer)   # 操作的目标, 值为"用户id" or "话题id" or "问题id" or "回答id"
    type = db.Column(db.String(20))  # type = "follow_user" or "follow_topic" or "follow_ques" or "answer" or "ask"
    update_time = db.Column(db.DateTime(), default=datetime.utcnow)
    show = db.Column(db.Boolean, default=False)   # 是否已经被展示,默认为否

    @staticmethod
    def search_notes(id):
        """查询与某用户相关的记录"""
        follow_user_activity = list()
        updates = FriendUpdates.query.filter_by(follower_id=id).all()
        for update in updates:
            activity = list()
            activity.append(User.query.filter_by(id=update.followed_id).first())
            result = None
            if update.type == "follow_user":
                result = User.query.filter_by(id=update.target).first()
            if update.type == "follow_topic":
                result = Topic.query.filter_by(id=update.target).first()
            if update.type == "follow_ques" or update.type == "ask":
                result = Question.query.filter_by(id=update.target).first()
            if update.type == "answer":
                result = Answer.query.filter_by(id=update.target).first()

            if not result:
                continue
            activity.append(result)
            activity.append(update.update_time)
            activity.append(calendar.timegm(update.update_time.utctimetuple()))
            activity.append(update.type)
            follow_user_activity.append(activity)
        return follow_user_activity


class TopicCategory(db.Model):
    """话题类别"""
    __tablename__ = "topiccate"
    id = db.Column(db.Integer, primary_key=True)
    category_name = db.Column(db.String(30), nullable=False)
    category_desc = db.Column(db.String(50))
    topics = db.relationship("Topic", backref="category")

    @staticmethod
    def insert_category(name, desc):
        topic_cate = TopicCategory(
            category_name=name,
            category_desc=desc
        )
        return operate_model.db_add(topic_cate)

    @staticmethod
    def delete_category(cate_id):
        cate = TopicCategory.query.filter_by(id=cate_id).first()
        if not cate:
            return False
        return operate_model.db_delete(cate)


class Topic(db.Model):
    """话题"""
    __tablename__ = "topic"
    id = db.Column(db.Integer, primary_key=True)
    topic_name = db.Column(db.String(30), nullable=False)
    topic_avatar = db.Column(db.LargeBinary(length=2048))
    topic_desc = db.Column(db.String(50))
    category_id = db.Column(db.Integer, db.ForeignKey("topiccate.id"))
    follow_topics = db.relationship("FollowTopic", backref="topic",
                                    lazy='dynamic',
                                    cascade='all, delete-orphan'
                                    )
    question_topic = db.relationship("QuestionTopic", backref="topic")

    def questions_excellans(self):
        """
        列举话题本身下的所有问题，
         以及最优回答，即评论最多的。
        """
        questions_excellans = list()  # 存放所有问题以及最优回答对象
        for question in self.question_topic:
            query = question.question.answers.filter_by().all()  # 查询问题下的所有回答
            question_answer = []  # 存放检索到的目标问题_回答集合
            if query:
                answer_excell = query[0]
                count = answer_excell.comments.count()
                for answer in query:
                    if answer.comments.count() > count:
                        answer_excell = answer
                        count = answer_excell.comments.count()
                question_answer.append(question.question)
                question_answer.append(answer_excell)
            else:
                question_answer.append(question.question)
                question_answer.append(None)
            question_answer.append(self)
            questions_excellans.append(question_answer)  # 添加进总集和并返回
        return questions_excellans

    @staticmethod
    def insert_topic(name, desc, avatar, cate):
        topic = Topic(
            topic_name=name,
            topic_desc=desc,
            topic_avatar=avatar,
            category_id=cate

        )
        return operate_model.db_add(topic)

    @staticmethod
    def delete_topic(topic_id):
        topic = Topic.query.filter_by(id=topic_id).first()
        if not topic:
            return False
        return operate_model.db_delete(topic)


class FollowTopic(db.Model):
    """
    关注话题：
    多对多的关系
    """
    __tablename__ = "followtopic"
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"),
                        primary_key=True)
    topic_id = db.Column(db.Integer, db.ForeignKey("topic.id"),
                         primary_key=True)
    desc = db.Column(db.String(30))


class Question(db.Model):
    """问题"""
    __tablename__ = "question"
    id = db.Column(db.Integer, primary_key=True)
    question_name = db.Column(db.String(30), nullable=False)
    question_desc = db.Column(db.String(500))
    views = db.Column(db.Integer, default=0)  # 问题被浏览次数,默认为0次.
    author_id = db.Column(db.Integer, db.ForeignKey("users.id"))
    question_time = db.Column(db.DateTime(), default=datetime.utcnow)
    question_topic = db.relationship("QuestionTopic", backref="question")

    answers = db.relationship("Answer", backref="question",
                              lazy='dynamic',
                              cascade='all, delete-orphan'
                              )
    follow_questions = db.relationship("FollowQuestion", backref="question",
                                       lazy='dynamic',
                                       cascade='all, delete-orphan'
                                       )

    def ping(self):
        """问题被浏览的次数"""
        self.views += 1
        return operate_model.db_add(self)

    @staticmethod
    def add_question(question_name, question_desc, topic, current_user_id):
        """添加一个问题"""
        question = Question(
            question_name=question_name,
            question_desc=question_desc,
            author_id=current_user_id
        )
        result = operate_model.db_add(question)
        if not result:
            return result

        question = Question.query.filter_by(question_name=question_name).first()
        if question:
            question_topic = QuestionTopic(
                question_id=question.id,
                topic_id=topic
            )
            result = operate_model.db_add(question_topic)
            if not result:
                operate_model.db_delete(question)
                return False

            return question


class QuestionTopic(db.Model):
    """问题与话题之间是多对多的关系"""
    __tablename__ = "question_topic"
    question_id = db.Column(db.Integer, db.ForeignKey("question.id"),
                            primary_key=True)
    topic_id = db.Column(db.Integer, db.ForeignKey("topic.id"),
                         primary_key=True)


class Answer(db.Model):
    """用户回答问题是多对多的关系"""
    __tablename__ = "answer"
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"))
    question_id = db.Column(db.Integer, db.ForeignKey("question.id"))
    timestamp = db.Column(db.DateTime(), default=datetime.utcnow)
    answer_body = db.Column(db.String(2000), nullable=False)
    comments = db.relationship("Comments", backref="answer",
                               lazy='dynamic',
                               cascade='all, delete-orphan'
                               )

    @staticmethod
    def answer_question(user_id, question_id, answer_body):
        answer = Answer(
            user_id=user_id,
            question_id=question_id,
            answer_body=answer_body
        )
        result = operate_model.db_add(answer)
        return Answer.query.filter_by(user_id=user_id, question_id=question_id).first() if result else result


class FollowQuestion(db.Model):
    __tablename__ = "follow_question"
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"),
                        primary_key=True)
    question_id = db.Column(db.Integer, db.ForeignKey("question.id"),
                         primary_key=True)
    desc = db.Column(db.String(30))


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
