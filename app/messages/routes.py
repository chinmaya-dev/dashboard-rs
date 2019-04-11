from flask import render_template, url_for, flash, redirect, request, redirect, current_app, jsonify, g
from flask_login import login_user, current_user,  login_required
from datetime import datetime
from .. import db
from . import bp
from .forms import MessageForm
from ..models import Message, User, Notification
from app.main.forms import SearchForm

@bp.before_request
def before_request():
    if current_user.is_authenticated:
        current_user.last_seen = datetime.utcnow()
        g.search_form = SearchForm()
        db.session.commit()



@bp.route('/send_message/<int:id>', methods=['GET', 'POST'])
@login_required
def send_message(id):
    user = User.query.filter_by(id=id).first_or_404()
    form = MessageForm()
    if form.validate_on_submit():
        msg = Message(author=current_user, recipient=user,
                      body=form.message.data)
        db.session.add(msg)
        db.session.commit()
        user.add_notification('unread_message_count', user.new_messages())
        db.session.commit()
        flash('Your message has been sent!', 'success')
        return redirect(url_for('users.user', id=user.id))
    return render_template('messages/send_message.html', title=('Send Message'),
                           form=form, user=user)


@bp.route('/message')
@login_required
def message():
    current_user.last_message_read_time = datetime.utcnow()
    current_user.add_notification('unread_message_count', 0)
    db.session.commit()
    page = request.args.get('page', 1, type=int)
    messages = current_user.messages_received.order_by(
        Message.timestamp.asc()).paginate(
            page, current_app.config['POSTS_PER_PAGE'], False)
    owns = current_user.messages_sent.order_by(
        Message.timestamp.asc()).paginate(
            page, current_app.config['POSTS_PER_PAGE'], False)
    next_url = url_for('messages.message', page=messages.next_num) \
        if messages.has_next else None
    prev_url = url_for('messages.message', page=messages.prev_num) \
        if messages.has_prev else None
    return render_template('messages/message.html', messages=messages.items,
                           next_url=next_url, prev_url=prev_url, owns=owns.items)

@bp.route('/notifications')
@login_required
def notifications():
    since = request.args.get('since', 0.0, type=float)
    notifications = current_user.notifications.filter(
        Notification.timestamp > since).order_by(Notification.timestamp.asc())
    return jsonify([{
        'name': n.name,
        'data': n.get_data(),
        'timestamp': n.timestamp
    } for n in notifications])
