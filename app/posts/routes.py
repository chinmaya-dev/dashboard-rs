from flask import (render_template, url_for, flash, request, g,
                   redirect, request, abort, current_app, make_response)
from flask_login import current_user, login_required
from flask_sqlalchemy import get_debug_queries
from app import db
from datetime import datetime
from app.posts import bp
from app.models import Post, User, Comment, PostLike, CommentLike
from app.posts.forms import PostForm, CommentForm
from app.posts.utils import save_picture
from app.main.forms import SearchForm

@bp.before_request
def before_request():
    if current_user.is_authenticated:
        current_user.last_seen = datetime.utcnow()
        g.search_form = SearchForm()
        db.session.commit()


@bp.route("/post/<int:id>", methods=['GET', 'POST'])
@login_required
def new_post(id):
    form = PostForm()
    user = User.query.get_or_404(id)
    if form.validate_on_submit():
        picture_file = save_picture(form.picture.data)
        post = Post(city=form.city.data,
                    image_file=picture_file,
                    category=form.category.data,
                    summary=form.summary.data,
                    title=form.title.data,
                    story=form.story.data,
                    Protagonist= user)
        db.session.add(post)
        db.session.commit()
        flash('Your Solution has been created!', 'success')
        return redirect(url_for('main.solutions'))
    return render_template('posts/create_post.html', title='New Post',
                           form=form, legend='Create Solution')


@bp.route("/postn/<int:post_id>",  methods=['GET', 'POST'])
def postn(post_id):
    post = Post.query.get_or_404(post_id)
    comment=Comment
    form = CommentForm()
    if form.validate_on_submit():
        comment = Comment(body=form.body.data,
                          post=post,
                          Protagonist=current_user._get_current_object() )
        db.session.add(comment)
        db.session.commit()
        flash('Your comment has been published.', 'success')
        return redirect(url_for('posts.postn', post_id=post.id, page=-1))
    page = request.args.get('page', 1, type=int)
    if page == -1:
        page = (post.comments.count() - 1) // \
            current_app.config['FLASKY_COMMENTS_PER_PAGE'] + 1
    pagination = post.comments.order_by(Comment.timestamp.asc()).paginate(
        page, per_page=current_app.config['FLASKY_COMMENTS_PER_PAGE'],
        error_out=False)
    comments = pagination.items

    return render_template('posts/post.html', posts=[post],post=post, form=form,
                           comments=comments, pagination=pagination, comment=comment, title=post.title)


@bp.route("/post/<int:post_id>/update", methods=['GET', 'POST'])
@login_required
def update_post(post_id):
    post = Post.query.get_or_404(post_id)
    form = PostForm()
    if form.validate_on_submit():
        if form.picture.data:
            picture_file = save_picture(form.picture.data)
            post.image_file = picture_file
        post.city = form.city.data
        post.category = form.category.data
        post.title = form.title.data
        post.story = form.story.data
        post.summary = form.summary.data
        db.session.commit()
        flash(' post has been updated!', 'success')
        return redirect(url_for('posts.postn', post_id=post.id))
    elif request.method == 'GET':
        form.city.data = post.city
        form.category.data = post.category
        form.title.data = post.title
        form.story.data = post.story
        form.summary.data = post.summary
    return render_template('posts/create_post.html', title='Update Post',
                           form=form, legend='Update Post')


@bp.route("/post/<int:post_id>/delete", methods=['POST'])
@login_required

def delete_post(post_id):
    post = Post.query.get_or_404(post_id)
    db.session.delete(post)
    db.session.commit()
    flash('  post has been deleted!', 'success')
    return redirect(url_for('main.solutions'))

@bp.route('/postlike/<int:post_id>/<action>')
@login_required
def postlike_action(post_id, action):
    post = Post.query.filter_by(id=post_id).first_or_404()
    if action == 'like':
        current_user.like_post(post)
        db.session.commit()
    if action == 'unlike':
        current_user.unlike_post(post)
        db.session.commit()
    return redirect(url_for('posts.postn', post_id=post.id, page=-1))

@bp.route('/postcommentlike/<int:comment_id>/<action>')
@login_required
def postcommentlike_action(comment_id, action):
    comment = Comment.query.filter_by(id=comment_id).first_or_404()
    if action == 'like':
        current_user.like_comment(comment)
        db.session.commit()
    if action == 'unlike':
        current_user.unlike_comment(comment)
        db.session.commit()
    return redirect(url_for('main.home'))
