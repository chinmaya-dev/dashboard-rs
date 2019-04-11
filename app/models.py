from datetime import datetime
import os
import json
from time import time
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer
from . import db, login_manager
from markdown import markdown
from flask import current_app, request, url_for
import bleach
from flask_login import UserMixin, AnonymousUserMixin
from .search import add_to_index, remove_from_index, query_index


class SearchableMixin(object):
    @classmethod
    def search(cls, expression, page, per_page):
        ids, total = query_index(cls.__tablename__, expression, page, per_page)
        if total == 0:
            return cls.query.filter_by(id=0), 0
        when = []
        for i in range(len(ids)):
            when.append((ids[i], i))
        return cls.query.filter(cls.id.in_(ids)).order_by(
            db.case(when, value=cls.id)), total

    @classmethod
    def before_commit(cls, session):
        session._changes = {
            'add': list(session.new),
            'update': list(session.dirty),
            'delete': list(session.deleted)
        }

    @classmethod
    def after_commit(cls, session):
        for obj in session._changes['add']:
            if isinstance(obj, SearchableMixin):
                add_to_index(obj.__tablename__, obj)
        for obj in session._changes['update']:
            if isinstance(obj, SearchableMixin):
                add_to_index(obj.__tablename__, obj)
        for obj in session._changes['delete']:
            if isinstance(obj, SearchableMixin):
                remove_from_index(obj.__tablename__, obj)
        session._changes = None

    @classmethod
    def reindex(cls):
        for obj in cls.query:
            add_to_index(cls.__tablename__, obj)


db.event.listen(db.session, 'before_commit', SearchableMixin.before_commit)
db.event.listen(db.session, 'after_commit', SearchableMixin.after_commit)




class Permission:
    FOLLOW = 1
    COMMENT = 2
    WRITE = 4
    MODERATE = 8
    ADMIN = 16


class Role(db.Model):
    __tablename__ = 'roles'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), unique=True)
    default = db.Column(db.Boolean, default=False, index=True)
    permissions = db.Column(db.Integer)
    users = db.relationship('User', backref='role', lazy='dynamic')

    def __init__(self, **kwargs):
        super(Role, self).__init__(**kwargs)
        if self.permissions is None:
            self.permissions = 0

    @staticmethod
    def insert_roles():
        roles = {
            'User': [Permission.FOLLOW, Permission.COMMENT, Permission.WRITE],
            'Moderator': [Permission.FOLLOW, Permission.COMMENT,
                          Permission.WRITE, Permission.MODERATE],
            'Administrator': [Permission.FOLLOW, Permission.COMMENT,
                              Permission.WRITE, Permission.ADMIN]
        }
        default_role = 'User'
        for r in roles:
            role = Role.query.filter_by(name=r).first()
            if role is None:
                role = Role(name=r)
            role.reset_permissions()
            for perm in roles[r]:
                role.add_permission(perm)
            role.default = (role.name == default_role)
            db.session.add(role)
        db.session.commit()

    def add_permission(self, perm):
        if not self.has_permission(perm):
            self.permissions += perm

    def remove_permission(self, perm):
        if self.has_permission(perm):
            self.permissions -= perm

    def reset_permissions(self):
        self.permissions = 0

    def has_permission(self, perm):
        return self.permissions & perm == perm

    def __repr__(self):
        return '<Role %r>' % self.name


class Follow(db.Model):
    __tablename__ = 'follows'
    follower_id = db.Column(db.Integer, db.ForeignKey('user.id'),
                            primary_key=True)
    followed_id = db.Column(db.Integer, db.ForeignKey('user.id'),
                            primary_key=True)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)

class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    role_id = db.Column(db.Integer, db.ForeignKey('roles.id'))
    username = db.Column(db.String(20), index=True, unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    image_file = db.Column(db.String(20), nullable=False, default='default.jpg')
    password = db.Column(db.String(60), nullable=False)
    about_me = db.Column(db.String(140))
    is_role =  db.Column(db.String(140))
    social_id = db.Column(db.String(140))
    gender = db.Column(db.String(5))
    contact_number = db.Column(db.Integer)
    tandc = db.Column(db.Boolean)
    first_name = db.Column(db.String(60))
    last_name = db.Column(db.String(60))
    category = db.Column(db.String(60))
    web_url = db.Column(db.String(60))
    date_of_birth = db.Column(db.DateTime, default=datetime.utcnow)
    last_seen = db.Column(db.DateTime, default=datetime.utcnow)
    posts = db.relationship('Post', backref='Protagonist', lazy='dynamic')
    platform = db.relationship('Platform', backref='Protagonist', lazy='dynamic')
    blog = db.relationship('Blog', backref = 'blog_author', lazy= 'dynamic')
    member_since = db.Column(db.DateTime(), default=datetime.utcnow)
    followed = db.relationship('Follow',
                               foreign_keys=[Follow.follower_id],
                               backref=db.backref('follower', lazy='joined'),
                               lazy='dynamic',
                               cascade='all, delete-orphan')
    followers = db.relationship('Follow',
                                foreign_keys=[Follow.followed_id],
                                backref=db.backref('followed', lazy='joined'),
                                lazy='dynamic',
                                cascade='all, delete-orphan')
    comments = db.relationship('Comment', backref='Protagonist', lazy='dynamic')
    blog_comments = db.relationship('BlogComment', backref='blog_author', lazy='dynamic')
    platform_comments = db.relationship('PlatformComment', backref='Protagonist', lazy='dynamic')
    post_liked = db.relationship(
        'PostLike',
        foreign_keys='PostLike.user_id',
        backref='user', lazy='dynamic')
    comment_liked = db.relationship(
        'CommentLike',
        foreign_keys='CommentLike.user_id',
        backref='user', lazy='dynamic')
    blog_liked = db.relationship(
        'BlogLike',
        foreign_keys='BlogLike.user_id',
        backref='user', lazy='dynamic')
    blog_comment_liked = db.relationship(
        'BlogCommentLike',
        foreign_keys='BlogCommentLike.user_id',
        backref='user', lazy='dynamic')
    platform_liked = db.relationship(
        'PlatformLike',
        foreign_keys='PlatformLike.user_id',
        backref='user', lazy='dynamic')
    platform_comment_liked = db.relationship(
        'PlatformCommentLike',
        foreign_keys='PlatformCommentLike.user_id',
        backref='user', lazy='dynamic')
    messages_sent = db.relationship('Message',
                                    foreign_keys='Message.sender_id',
                                    backref='author', lazy='dynamic')
    messages_received = db.relationship('Message',
                                        foreign_keys='Message.recipient_id',
                                        backref='recipient', lazy='dynamic')
    last_message_read_time = db.Column(db.DateTime)
    notifications = db.relationship('Notification', backref='user',
                                    lazy='dynamic')

    def like_post(self, post):
        if not self.has_liked_post(post):
            like = PostLike(user_id=self.id, post_id=post.id)
            db.session.add(like)

    def unlike_post(self, post):
        if self.has_liked_post(post):
            PostLike.query.filter_by(
                user_id=self.id,
                post_id=post.id).delete()

    def has_liked_post(self, post):
        return PostLike.query.filter(
            PostLike.user_id == self.id,
            PostLike.post_id == post.id).count() > 0

    def like_comment(self, comment):
        if not self.has_liked_comment(comment):
            like = CommentLike(user_id=self.id, comment_id=comment.id)
            db.session.add(like)

    def unlike_comment(self, comment):
        if self.has_liked_comment(comment):
            CommentLike.query.filter_by(
                user_id=self.id,
                comment_id=comment.id).delete()

    def has_liked_comment(self, comment):
        return CommentLike.query.filter(
            CommentLike.user_id == self.id,
            CommentLike.comment_id == comment.id).count() > 0

    def like_blog(self, blog):
        if not self.has_liked_blog(blog):
            like = BlogLike(user_id=self.id, blog_id=blog.id)
            db.session.add(like)

    def unlike_blog(self, blog):
        if self.has_liked_blog(blog):
            BlogLike.query.filter_by(
                user_id=self.id,
                blog_id=blog.id).delete()

    def has_liked_blog(self, blog):
        return BlogLike.query.filter(
            BlogLike.user_id == self.id,
            BlogLike.blog_id == blog.id).count() > 0

    def like_blogcomment(self, blogcomment):
        if not self.has_liked_blogcomment(blogcomment):
            like = BlogCommentLike(user_id=self.id, blog_comment_id=blogcomment.id)
            db.session.add(like)

    def unlike_blogcomment(self, blogcomment):
        if self.has_liked_blogcomment(blogcomment):
            BlogCommentLike.query.filter_by(
                user_id=self.id,
                blog_comment_id=blogcomment.id).delete()

    def has_liked_blogcomment(self, blogcomment):
        return BlogCommentLike.query.filter(
            BlogCommentLike.user_id == self.id,
            BlogCommentLike.blog_comment_id == blogcomment.id).count() > 0




    def __init__(self, **kwargs):
        super(User, self).__init__(**kwargs)
        if self.role is None:
            if self.email == current_app.config['FLASKY_ADMIN']:
                self.role = Role.query.filter_by(name='Administrator').first()
            if self.role is None:
                self.role = Role.query.filter_by(default=True).first()
        self.follow(self)


    def can(self, perm):
        return self.role is not None and self.role.has_permission(perm)


    def is_administrator(self):
        return self.can(Permission.ADMIN)


    def follow(self, user):
        if not self.is_following(user):
            f = Follow(follower=self, followed=user)
            db.session.add(f)

    def unfollow(self, user):
        f = self.followed.filter_by(followed_id=user.id).first()
        if f:
            db.session.delete(f)


    def is_following(self, user):
        if user.id is None:
            return False
        return self.followed.filter_by(
            followed_id=user.id).first() is not None

    def is_followed_by(self, user):
        if user.id is None:
            return False
        return self.followers.filter_by(
            follower_id=user.id).first() is not None

    def get_reset_token(self, expires_sec=1800):
        s = Serializer(current_app.config['SECRET_KEY'], expires_sec)
        return s.dumps({'user_id': self.id}).decode('utf-8')



    @staticmethod
    def verify_reset_token(token):
        s = Serializer(current_app.config['SECRET_KEY'])
        try:
            user_id = s.loads(token)['user_id']
        except:
            return None
        return User.query.get(user_id)

    def new_messages(self):
        last_read_time = self.last_message_read_time or datetime(1900, 1, 1)
        return Message.query.filter_by(recipient=self).filter(
            Message.timestamp > last_read_time).count()

    def add_notification(self, name, data):
        self.notifications.filter_by(name=name).delete()
        n = Notification(name=name, payload_json=json.dumps(data), user=self)
        db.session.add(n)
        return n





    def __repr__(self):
        return f"User('{self.username}', '{self.user_id}', '{self.email}', '{self.image_file}', '{self.id}', '{self.last_message_read_time}', '{self.is_role}',  '{self.category}',  '{self.sub_category}')"

class AnonymousUser(AnonymousUserMixin):
    def can(self, permissions):
        return False

    def is_administrator(self):
        return False

    def has_liked_post(self, post):
        return False

    def has_liked_comment(self, comment):
        return False

    def has_liked_blog(self, blog):
        return False

    def has_liked_blogcomment(self, blogcomment):
        return False

login_manager.anonymous_user = AnonymousUser

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))



class Post( db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    city = db.Column(db.String(50), nullable=False)
    category = db.Column(db.String(50), nullable=False)
    title = db.Column(db.String(500), nullable=False)
    story = db.Column(db.Text, nullable=False)
    summary = db.Column(db.Text)
    image_file = db.Column(db.String(20), default='default.jpg')
    timestamp = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    comments = db.relationship('Comment', backref='post', lazy='dynamic')
    likes = db.relationship('PostLike', backref='post', lazy='dynamic')



    def __repr__(self):
        return f"Post('{self.Protagonist}', '{self.date_posted}')"



class Comment(db.Model):
    __tablename__ = 'comments'
    id = db.Column(db.Integer, primary_key=True)
    body = db.Column(db.Text)
    body_html = db.Column(db.Text)
    timestamp = db.Column(db.DateTime, index=True, default=datetime.utcnow)
    disabled = db.Column(db.Boolean)
    author_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    post_id = db.Column(db.Integer, db.ForeignKey('post.id'))
    likes = db.relationship('CommentLike', backref='comment', lazy='dynamic')



    @staticmethod
    def on_changed_body(target, value, oldvalue, initiator):
        allowed_tags = ['a', 'abbr', 'acronym', 'b', 'code', 'em', 'i',
                        'strong']
        target.body_html = bleach.linkify(bleach.clean(
            markdown(value, output_format='html'),
            tags=allowed_tags, strip=True))

db.event.listen(Comment.body, 'set', Comment.on_changed_body)



class Blog(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    city = db.Column(db.String(50), nullable=False)
    category = db.Column(db.String(50), nullable=False)
    title = db.Column(db.String(500), nullable=False)
    story = db.Column(db.Text, nullable=False)
    summary = db.Column(db.Text)
    timestamp = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    comments = db.relationship('BlogComment', backref='blog', lazy='dynamic')
    likes = db.relationship('BlogLike', backref='blog', lazy='dynamic')
    image_file = db.Column(db.String(20), default='default.jpg')


    def __repr__(self):
        return f"Blog('{self.blog_author}', '{self.date_posted}')"



class BlogComment(db.Model):
    __tablename__ = 'blogcomments'
    id = db.Column(db.Integer, primary_key=True)
    body = db.Column(db.Text)
    body_html = db.Column(db.Text)
    timestamp = db.Column(db.DateTime, index=True, default=datetime.utcnow)
    disabled = db.Column(db.Boolean)
    author_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    blog_id = db.Column(db.Integer, db.ForeignKey('blog.id'))
    likes = db.relationship('BlogCommentLike', backref='blogcomment', lazy='dynamic')

    @staticmethod
    def on_changed_body(target, value, oldvalue, initiator):
        allowed_tags = ['a', 'abbr', 'acronym', 'b', 'code', 'em', 'i',
                        'strong']
        target.body_html = bleach.linkify(bleach.clean(
            markdown(value, output_format='html'),
            tags=allowed_tags, strip=True))

db.event.listen(BlogComment.body, 'set', BlogComment.on_changed_body)


class PostLike(db.Model):
    __tablename__ = 'postlikes'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    post_id = db.Column(db.Integer, db.ForeignKey('post.id'))
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)

class CommentLike(db.Model):
    __tablename__ = 'commentlikes'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    comment_id = db.Column(db.Integer, db.ForeignKey('comments.id'))
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)

class BlogLike(db.Model):
    __tablename__ = 'bloglikes'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    blog_id = db.Column(db.Integer, db.ForeignKey('blog.id'))
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)

class BlogCommentLike(db.Model):
    __tablename__ = 'blogcommentlikes'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    blog_comment_id = db.Column(db.Integer, db.ForeignKey('blogcomments.id'))
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)

class Message(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    sender_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    recipient_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    body = db.Column(db.String(140))
    timestamp = db.Column(db.DateTime, index=True, default=datetime.utcnow)

    def __repr__(self):
        return '<Message {}>'.format(self.body)

class Notification(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(128), index=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    timestamp = db.Column(db.Float, index=True, default=time)
    payload_json = db.Column(db.Text)

    def get_data(self):
        return json.loads(str(self.payload_json))

class Platform(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    city = db.Column(db.String(50), nullable=False)
    category = db.Column(db.String(50), nullable=False)
    title = db.Column(db.String(500), nullable=False)
    description = db.Column(db.Text, nullable=False)
    summary = db.Column(db.Text)
    image_file = db.Column(db.String(20), default='default.jpg')
    timestamp = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    comments = db.relationship('PlatformComment', backref='platform', lazy='dynamic')
    likes = db.relationship('PlatformLike', backref='platform', lazy='dynamic')


    def __repr__(self):
        return f"Blog('{self.blog_author}', '{self.date_posted}')"



class PlatformComment(db.Model):
    __tablename__ = 'platformcomments'
    id = db.Column(db.Integer, primary_key=True)
    body = db.Column(db.Text)
    body_html = db.Column(db.Text)
    timestamp = db.Column(db.DateTime, index=True, default=datetime.utcnow)
    disabled = db.Column(db.Boolean)
    author_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    platform_id = db.Column(db.Integer, db.ForeignKey('platform.id'))
    likes = db.relationship('PlatformCommentLike', backref='platformcomment', lazy='dynamic')

    @staticmethod
    def on_changed_body(target, value, oldvalue, initiator):
        allowed_tags = ['a', 'abbr', 'acronym', 'b', 'code', 'em', 'i',
                        'strong']
        target.body_html = bleach.linkify(bleach.clean(
            markdown(value, output_format='html'),
            tags=allowed_tags, strip=True))

db.event.listen(BlogComment.body, 'set', BlogComment.on_changed_body)

class PlatformLike(db.Model):
    __tablename__ = 'platformlikes'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    platform_id = db.Column(db.Integer, db.ForeignKey('platform.id'))
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)

class PlatformCommentLike(db.Model):
    __tablename__ = 'platformcommentlikes'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    platform_comment_id = db.Column(db.Integer, db.ForeignKey('platformcomments.id'))
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)