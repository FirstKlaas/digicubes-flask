import smtplib
import threading
import logging
from queue import Queue
from datetime import datetime, timedelta

from email.message import EmailMessage
from email.headerregistry import Address
#from email.utils import make_msgid

import jwt

from flask import current_app, url_for


from jinja2 import Environment, PackageLoader, select_autoescape

from digicubes_common import exceptions as ex

from digicubes_client.client.proxy import UserProxy


logger = logging.getLogger(__name__)

class MailCube:
    @staticmethod
    def get_mail_cube():
        bot = getattr(current_app, "digicubes_mail_cube", None)
        if bot is None:
            bot = MailCube(current_app._get_current_object())
            current_app.digicubes_mailcube = bot

        return bot

    @property
    def smtp_host(self):
        assert "smtp_host" in self.config, "SMTP host not configured"
        assert self.config["smtp_host"] is not None, "SMTP host is None"

        return self.config["smtp_host"]

    @property
    def smtp_port(self):
        return self.config.get("smtp_port", 465)

    @property
    def smtp_username(self):
        assert "smtp_username" in self.config, "SMTP username not configured"
        assert (self.config["smtp_username"] is not None), "SMTP username is None"

        return self.config["smtp_username"]

    @property
    def smtp_password(self):
        assert "smtp_password" in self.config, "SMTP password not configured"
        assert (self.config["smtp_password"] is not None), "SMTP password is None"

        return self.config["smtp_password"]

    @property
    def smtp_from_email_addr(self):
        assert "smtp_from_email_addr" in self.config, "SMTP from address not configured"
        assert (self.config["smtp_from_email_addr"] is not None), "SMTP from address is None"

        return self.config["smtp_from_email_addr"]

    @property
    def smtp_from_display_name(self):
        assert "smtp_from_display_name" in self.config, "SMTP from display name not configured"
        assert (self.config["smtp_from_display_name"] is not None), "SMTP from display name is None"

        return self.config["smtp_from_display_name"]

    def __init__(self, app):

        self.config = app.config
        self.secret = app.config.get("secret", None)

        if self.secret is None:
            raise ex.ConfigurationError("Secret not configured")

        self.queue = Queue()
        self.app = app

        self.workers = []
        for _ in range(1):
            w = threading.Thread(target=self.__worker__)
            w.start()
            self.workers.append(w)

        self.jinja = Environment(
            loader=PackageLoader("digicubes_flask.email", "templates"),
            autoescape=select_autoescape(["html", "xml"]),
        )

    def __worker__(self):
        while True:
            obj = self.queue.get()

            number_of_tries = obj.get("number_of_tries", 1)
            recipient = obj["recipient"]
            verification_address = obj["verification_address"]

            try:
                first_name = "" if not recipient.first_name else recipient.first_name
                last_name = "" if not recipient.last_name else recipient.last_name
                name = (
                    recipient.login
                    if not first_name and not last_name
                    else f"{first_name} {last_name}"
                )

                template = self.jinja.get_template("user_verification_plain.jinja")
                plain_text = template.render(
                    user=recipient, verification_address=verification_address
                )

                template = self.jinja.get_template("user_verification_html.jinja")
                html_text = template.render(
                    user=recipient, verification_address=verification_address
                )

                with smtplib.SMTP_SSL(self.smtp_host, self.smtp_port) as mailserver:
                    mailserver.login(self.smtp_username, self.smtp_password)
                    msg = EmailMessage()
                    msg["Subject"] = "Verify your DigiCubes Account"
                    msg.set_content("Automated testmail")
                    msg["To"] = Address(display_name=name, addr_spec=recipient.email)
                    msg["From"] = Address(
                        display_name=self.smtp_from_display_name,
                        addr_spec=self.smtp_from_email_addr)
                    msg.set_content(plain_text)
                    msg.add_alternative(html_text, subtype="html")
                    mailserver.send_message(msg)

            except Exception:  # pylint: disable=bare-except
                # Something failed, so we put
                # the item back into he queue to try
                # again "later"
                number_of_tries += 1
                if number_of_tries > 10:
                    logger.exception("Unable to send verification email for user with id %d. Tried %d times.", recipient.id, (number_of_tries-1))
                else:
                    self.queue.put(obj)
            finally:
                self.queue.task_done()

    def send_verification_email(self, recipient: UserProxy):
        if recipient is None:
            raise ValueError("No recipient provided. Cannot send email.")

        if not recipient.email:
            raise ValueError("Recipient has no email address. Cannot send email.")


        token = self.create_verification_token(recipient)
        url = url_for("admin.verify", token=token, _external=True)
        self.queue.put({
            "recipient" : recipient,
            "verification_address" : url
        })

    def create_verification_token(self, user: UserProxy) -> str:

        lifetime = timedelta(hours=6)

        payload = {}
        payload["user_id"] = user.id
        payload["exp"] = datetime.utcnow() + lifetime
        payload["iat"] = datetime.utcnow()
        token = jwt.encode(payload, self.secret, algorithm="HS256")
        return token.decode("UTF-8")


    def decode_verification_token(self, token: str):
        """
        """
        payload = jwt.decode(token, self.secret, algorithms=["HS256"])
        return payload
