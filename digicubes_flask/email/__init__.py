from werkzeug.local import LocalProxy
from .automailer import MailCube

mail_cube = LocalProxy(MailCube.get_mail_cube)
