from flask import render_template, request, current_app, request, g, url_for, flash, redirect, send_from_directory
from .. import db
from app.models import Post, Comment, User, Platform, Blog
from flask_bootstrap import Bootstrap
from .email import send_message
from flask_login import login_user, current_user, logout_user, login_required
from app.main.forms import InputTextForm, SearchForm, MessageForm
from datetime import datetime
from app.main import bp

import random
import logging

@bp.before_request
def before_request():
    if current_user.is_authenticated:
        current_user.last_seen = datetime.utcnow()
        g.search_form = SearchForm()
        db.session.commit()


@bp.route('/robots.txt')
@bp.route('/sitemap.xml')
def static_from_root():
    return send_from_directory(current_app.static_folder, request.path[1:])

@bp.route("/", methods=['GET', 'POST'])

@bp.route("/home", methods=['GET', 'POST'])
def home():
    return render_template('main/home.html', title="Home", current_time=datetime.utcnow())


@bp.route("/tandc", methods=['GET', 'POST'])
def tandc():
    return render_template('main/t&c.html', title="Terms & Conditions")

@bp.route("/priv", methods=['GET', 'POST'])
def priv():
    return render_template('main/priv.html', title="Privacy Policy")

@bp.route("/contact", methods=['GET', 'POST'])
def contact():
    form = MessageForm()
    if form.validate_on_submit():
        send_message(form)
        flash('Thanks! For showing your interest we will try to get back to you as soon as possible. ', 'success')
        return redirect(url_for('main.home'))
    return render_template('main/contact.html', form=form, title='Contact us')


@bp.route("/solutions", methods=['GET', 'POST'])
def solutions():
    page = request.args.get('page', 1, type=int)
    posts = Post.query.order_by(
        Post.timestamp.desc()).paginate(page=page, per_page=100)
    return render_template('main/solutions.html', posts=posts, title="Solutions")

@bp.route("/about", methods=['GET', 'POST'])
def about():
    return render_template('main/about.html', title="About us")

@bp.route("/platform", methods=['GET', 'POST'])
def platform():
    page = request.args.get('page', 1, type=int)
    platform = Platform.query.order_by(
        Platform.timestamp.desc()).paginate(page=page, per_page=100)
    pages = request.args.get('page', 1, type=int)
    blogs = Blog.query.order_by(
        Blog.timestamp.desc()).paginate(page=pages, per_page=7)
    return render_template('main/platform.html', platform=platform, blogs=blogs, title="Platform")




@bp.route('/explore')
@login_required
def explore():
    page = request.args.get('page', 1, type=int)
    posts = Post.query.order_by(Post.timestamp.desc()).paginate(
        page, current_app.config['POSTS_PER_PAGE'], False)
    next_url = url_for('main.explore', page=posts.next_num) \
        if posts.has_next else None
    prev_url = url_for('main.explore', page=posts.prev_num) \
        if posts.has_prev else None
    return render_template('main/home.html', title=_('Explore'),
                           posts=posts.items, next_url=next_url,
                           prev_url=prev_url)



@bp.route('/search')
@login_required
def search():
    if not g.search_form.validate():
        return redirect(url_for('main.explore'))
    page = request.args.get('page', 1, type=int)
    posts, total = Post.search(g.search_form.q.data, page,
                               current_app.config['POSTS_PER_PAGE'])
    next_url = url_for('main.search', q=g.search_form.q.data, page=page + 1) \
        if total > page * current_app.config['POSTS_PER_PAGE'] else None
    prev_url = url_for('main.search', q=g.search_form.q.data, page=page - 1) \
        if page > 1 else None
    return render_template('main/search.html', title=('Search'), posts=posts,
                           next_url=next_url, prev_url=prev_url)







@bp.route('/')
def track_example():
    track_event(
        category='Example',
        action='test action')
    return 'Event tracked.'


@bp.errorhandler(500)
def server_error(e):
    logging.exception('An error occurred during a request.')
    return """
    An internal error occurred: <pre>{}</pre>
    See logs for full stacktrace.
    """.format(e), 500













