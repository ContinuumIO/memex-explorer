from flask.ext.mail import Message
from app import app, mail

# http://blog.miguelgrinberg.com/post/the-flask-mega-tutorial-part-xi-email-support

#def async(f):
#    def wrapper(*args, **kwargs):
#        thr = Thread(target=f, args=args, kwargs=kwargs)
#        thr.start()
#    return wrapper

#@async
#def send_async_email(app, msg):
#    with app.app_context():
#        mail.send(msg)

def send_email(subject, sender, recipients, text_body, html_body):
    msg = Message(subject, sender=sender, recipients=recipients)
    msg.body = text_body
    msg.html = html_body
    with app.app_context():
        mail.send(msg)

