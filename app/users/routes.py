from flask import render_template, url_for, flash, redirect, request, g
from flask_login import login_user, current_user, logout_user, login_required
from app import db, bcrypt
from datetime import datetime
from app.users import bp
from app.models import (User, Post, Follow, Role, Permission, 
                         PostLike, CommentLike, BlogLike, BlogCommentLike)
from app.users.forms import ( UpdateAccountForm,  EventsForm,  
                                 LinksForm,  MediaForm, )
from app.users.utils import save_picture
from app.main.forms import SearchForm


@bp.before_request
def before_request():
    if current_user.is_authenticated:
        current_user.last_seen = datetime.utcnow()
        g.search_form = SearchForm()
        db.session.commit()



@bp.route("/account/<int:id>", methods=['GET', 'POST'])
@login_required
def account(id):
    form = UpdateAccountForm()
    user = User.query.get_or_404(id)
    if form.validate_on_submit():
        if form.picture.data:
            picture_file = save_picture(form.picture.data)
            user.image_file = picture_file
        user.last_name = form.last_name.data
        user.first_name = form.first_name.data
        user.username = form.username.data
        user.email = form.email.data
        user.about_me= form.about_me.data
        user.gender = form.gender.data
        user.web_url = form.web_url.data
        user.contact_number = form.contact_number.data
        user.date_of_birth = form.date_of_birth.data
        db.session.commit()
        flash('Your account has been updated!', 'success')
        return redirect(url_for('users.user', id=user.id))
    elif request.method == 'GET':
        form.first_name.data = user.first_name
        form.last_name.data = user.last_name
        form.username.data = user.username
        form.email.data = user.email
        form.about_me.data = user.about_me
        form.gender.data = user.gender
        form.web_url.data = user.web_url
        form.contact_number.data = user.contact_number
        form.date_of_birth.data = user.date_of_birth
    image_file = url_for('static', filename='profile_pics/' + user
        .image_file)
    return render_template('users/account.html', title='Account',
                           image_file=image_file, form=form, user=user)





@bp.route("/user/<int:id>", methods=['GET', 'POST'])
def user(id):
    page = request.args.get('page', 1, type=int)
    user = User.query.filter_by(id=id).first_or_404()
    datetimecurr = datetime.utcnow()
    user_id = user.id
    links = Links.query.filter_by(user_id=id).first()
    image_file = url_for('static', filename='profile_pics/' + user.image_file)
    posts = Post.query.filter_by(Protagonist=user)\
        .order_by(Post.date_posted.desc())\
        .paginate(page=page, per_page=5)
    return render_template('users/user.html', datetimecurr=datetimecurr, image_file=image_file, posts=posts, user=user,  links=links)






@bp.route('/follow/<int:id>')
@login_required
def follow(id):
    user = User.query.filter_by(id=id).first()
    if user is None:
        flash(('User not found','warning'))
        return redirect(url_for('main.home'))
    if current_user.is_following(user):
        flash('You are already following this user', 'warning')
        return redirect(url_for('main.home', id=id))
    if user == current_user:
        flash(('You cannot follow yourself!', 'warning'))
        return redirect(url_for('main.home', id=id))
    current_user.follow(user)
    db.session.commit()
    flash('You are now following this user' , 'success' )
    return redirect(url_for('users.user', id=id))




@bp.route('/unfollow/<int:id>')
@login_required
def unfollow(id):
    user = User.query.filter_by(id=id).first()
    if user is None:
        flash(('User  not found.', 'warning'))
        return redirect(url_for('main.home'))
    if user == current_user:
        flash(('You cannot unfollow yourself!', 'warning'))
        return redirect(url_for('users.home', id=id))
    current_user.unfollow(user)
    db.session.commit()
    flash('You are not following this user anymore', 'danger'  )
    return redirect(url_for('users.user', id=id))

@bp.route('/followers/<int:id>')
def followers(id):
    user = User.query.filter_by(id=username).first()
    if user is None:
        flash('Invalid user', 'warning')
        return redirect(url_for('users.user'))
    page = request.args.get('page', 1, type=int)
    pagination = user.followers.paginate(
        page, per_page=current_app.config['FLASKY_FOLLOWERS_PER_PAGE'],
        error_out=False)
    follows = [{'user': item.follower, 'timestamp': item.timestamp}
               for item in pagination.items]
    return render_template('users/followers.html', user=user, title="Followers of",
                           endpoint='followers', pagination=pagination,
                           follows=follows)


@bp.route('/followed_by/<int:id>')
def followed_by(id):
    user = User.query.filter_by(id=id).first()
    if user is None:
        flash('Invalid user.')
        return redirect(url_for('users.user'))
    page = request.args.get('page', 1, type=int)
    pagination = user.followed.paginate(
        page, per_page=current_app.config['FLASKY_FOLLOWERS_PER_PAGE'],
        error_out=False)
    follows = [{'user': item.followed, 'timestamp': item.timestamp}
               for item in pagination.items]
    return render_template('followers.html', user=user, title="Followed by",
                           endpoint='followed_by', pagination=pagination,
                           follows=follows)
