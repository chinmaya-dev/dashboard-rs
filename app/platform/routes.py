from flask import (render_template, url_for, flash, request, g,
                   redirect, request, abort, current_app, make_response)
from flask_login import current_user, login_required
from flask_sqlalchemy import get_debug_queries
from app import db
from datetime import datetime
from app.platform import bp
from app.models import Platform, User, PlatformComment, PlatformLike, PlatformCommentLike
from app.platform.forms import PlatformForm, CommentForm
from app.platform.utils import save_picture
from app.main.forms import SearchForm

@bp.before_request
def before_request():
    if current_user.is_authenticated:
        current_user.last_seen = datetime.utcnow()
        g.search_form = SearchForm()
        db.session.commit()


@bp.route("/platform/<int:id>", methods=['GET', 'POST'])
@login_required
def new_platform(id):
    form = PlatformForm()
    user = User.query.get_or_404(id)
    if form.validate_on_submit():
        picture_file = save_picture(form.picture.data)
        platform = Platform(city=form.city.data,
                    image_file=picture_file,
                    category=form.category.data,
                    summary=form.summary.data,
                    title=form.title.data,
                    description=form.description.data,
                    Protagonist= user)
        db.session.add(platform)
        db.session.commit()
        flash('Your Platform post has been created!', 'success')
        return redirect(url_for('main.platform'))
    return render_template('platform/create_platform.html', title='New Post',
                           form=form, legend='Create Solution')


@bp.route("/platformn/<int:platform_id>",  methods=['GET', 'POST'])
def platformn(platform_id):
    platform = Platform.query.get_or_404(platform_id)
    platformcomment = PlatformComment
    form = CommentForm()
    if form.validate_on_submit():
        comment = PlatformComment(body=form.body.data,
                          platform=platform,
                          Protagonist=current_user._get_current_object() )
        db.session.add(comment)
        db.session.commit()
        flash('Your comment has been published.', 'success')
        return redirect(request.referrer)
    page = request.args.get('page', 1, type=int)
    if page == -1:
        page = (platform.comments.count() - 1) // \
            current_app.config['FLASKY_COMMENTS_PER_PAGE'] + 1
    pagination = platform.comments.order_by(PlatformComment.timestamp.asc()).paginate(
        page, per_page=current_app.config['FLASKY_COMMENTS_PER_PAGE'],
        error_out=False)
    comments = pagination.items

    return render_template('platform/platform.html',  platforms=[platform], platform=platform, form=form,
                              comments=comments, pagination=pagination, platformcomment=platformcomment, title=platform.title)


@bp.route("/platform/<int:platform_id>/update", methods=['GET', 'POST'])
@login_required
def update_platform(platform_id):
    platform = Platform.query.get_or_404(platform_id)
    form = PlatformForm()
    if form.validate_on_submit():
        if form.picture.data:
            picture_file = save_picture(form.picture.data)
            platform.image_file = picture_file
        platform.city = form.city.data
        platform.category = form.category.data
        platform.summary = form.summary.data
        platform.title = form.title.data
        platform.description = form.description.data
        db.session.commit()
        flash(' post has been updated!', 'success')
        return redirect(url_for('platform.platformn', platform_id=platform.id))
    elif request.method == 'GET':
        form.city.data = platform.city
        form.category.data = platform.category
        form.summary.data = platform.summary
        form.title.data = platform.title
        form.description.data = platform.description
    return render_template('platform/create_platform.html', title='Update',
                           form=form, legend='Update Platform Post')


@bp.route("/platform/<int:platform_id>/delete", methods=['POST'])
@login_required
def delete_platform(platform_id):
    platform = Platform.query.get_or_404(platform_id)
    db.session.delete(platform)
    db.session.commit()
    flash( 'post has been deleted!', 'success')
    return redirect(request.referrer)


