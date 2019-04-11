from flask import render_template, current_app
from flask import url_for
from flask_mail import Message
from app import mail


def send_message(form):
    msg = Message('Quantamix Solutions-Contact Request',
                  sender='quantamixsolutions@gmail.com',
                  recipients=["abhishek121meena121@gmail.com", "harish77kumar4270@gmail.com", "contact@quantamixsolutions.com"])
    msg.html = f'''<h3>Name: {form.name.data}</h3><h3> Email: {form.email.data}</h3>
<p>{form.msg.data}</p>


'''
    mail.send(msg)
