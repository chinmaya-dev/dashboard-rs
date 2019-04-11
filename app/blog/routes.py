from flask import (render_template, url_for, flash, current_app, request, g,
                   redirect, request, abort,current_app, make_response)
from flask_login import current_user, login_required
from flask_sqlalchemy import get_debug_queries
from app import db
from app.blog import bp
from app.models import Blog, User, BlogComment, BlogLike, BlogCommentLike
from app.blog.forms import BlogForm, BlogCommentForm
from app.blog.utils import save_picture
from datetime import datetime
from app.main.forms import SearchForm

@bp.before_request
def before_request():
    if current_user.is_authenticated:
        current_user.last_seen = datetime.utcnow()
        g.search_form = SearchForm()
        db.session.commit()


@bp.route("/blogview")
def blog_view():
    page = request.args.get('page', 1, type=int)
    blogs = Blog.query.order_by(Blog.timestamp.desc()).paginate(page=page, per_page=100)
    return render_template('blog/blogview.html', blogs=blogs, current_time=datetime.utcnow(), title="Blogs")


@bp.route("/blog/<int:id>", methods=['GET', 'POST'])
@login_required
def new_blog(id):
    form = BlogForm()
    user = User.query.get_or_404(id)
    if form.validate_on_submit():
        picture_file = save_picture(form.picture.data)
        blog = Blog(city=form.city.data,
                    image_file=picture_file,
                    category=form.category.data,
                    summary=form.summary.data,
                    title=form.title.data,
                    story=form.story.data,
                    blog_author= user)
        db.session.add(blog)
        db.session.commit()
        flash('Your blog post has been created', 'success')
        return redirect(url_for('blog.blog_view'))
    return render_template('blog/create_blog.html', title='New Blog',
                           form=form, legend='New Blog')


@bp.route("/blogn/<int:blog_id>",  methods=['GET', 'POST'])
def blogn(blog_id):
    blog = Blog.query.get_or_404(blog_id)
    blogcomment=BlogComment
    form = BlogCommentForm()
    if form.validate_on_submit():
        blogcomment = BlogComment(body=form.body.data,
                          blog=blog,
                          blog_author=current_user._get_current_object() )
        db.session.add(blogcomment)
        db.session.commit()
        flash('Your blog comment has been published.', 'success')
        return redirect(url_for('blog.blogn', blog_id=blog.id, page=-1))
    page = request.args.get('page', 1, type=int)
    if page == -1:
        page = (blog.blogcomments.count() - 1) // \
            current_app.config['FLASKY_COMMENTS_PER_PAGE'] + 1
    pages = request.args.get('page', 1, type=int)
    blogsx = Blog.query.order_by(
        Blog.timestamp.desc()).paginate(page=pages, per_page=7)
    

    return render_template('blog/blog.html', blogs=[blog],blog=blog, form=form, blogsx=blogsx,
                           blogcomment=blogcomment, title=blog.title)


@bp.route("/blog/<int:blog_id>/update", methods=['GET', 'POST'])
@login_required
def update_blog(blog_id):
    blog = Blog.query.get_or_404(blog_id)
    form = BlogForm()
    if form.validate_on_submit():
        if form.picture.data:
            picture_file = save_picture(form.picture.data)
            blog.image_file = picture_file
        blog.city = form.city.data
        blog.category = form.category.data
        blog.title = form.title.data
        blog.summary = form.summary.data
        blog.story = form.story.data
        db.session.commit()
        flash(' Blog post has been updated!', 'success')
        return redirect(url_for('blog.blogn', blog_id=blog.id))
    elif request.method == 'GET':
        form.city.data = blog.city
        form.category.data = blog.category
        form.title.data = blog.title
        form.summary.data = blog.summary
        form.story.data = blog.story
    return render_template('blog/create_blog.html', title='Update Blog',
                           form=form, legend='Update Blog')


@bp.route("/blog/<int:blog_id>/delete", methods=['POST'])
@login_required

def delete_blog(blog_id):
    blog = Blog.query.get_or_404(blog_id)
    db.session.delete(blog)
    db.session.commit()
    flash('Blog post has been deleted!', 'success')
    return redirect(url_for('blog.blog_view'))

@bp.route('/bloglike/<int:blog_id>/<action>')
@login_required
def bloglike_action(blog_id, action):
    blog = Blog.query.filter_by(id=blog_id).first_or_404()
    if action == 'like':
        current_user.like_blog(blog)
        db.session.commit()
    if action == 'unlike':
        current_user.unlike_blog(blog)
        db.session.commit()
    return redirect(url_for('blog.blogn', blog_id=blog.id, page=-1))

@bp.route('/blogcommentlike/<int:blog_comment_id>/<action>')
@login_required
def blogcommentlike_action(blog_comment_id, action):
    blogcomment = BlogComment.query.filter_by(id=blog_comment_id).first_or_404()
    if action == 'like':
        current_user.like_blogcomment(blogcomment)
        db.session.commit()
    if action == 'unlike':
        current_user.unlike_blogcomment(blogcomment)
        db.session.commit()
    return redirect(url_for('blog.blog_view'))
