import smtplib
import threading
import logging
from queue import Queue

from email.message import EmailMessage
from email.headerregistry import Address

# from email.utils import make_msgid

from flask import current_app, url_for

from jinja2 import Environment, PackageLoader, select_autoescape

from digicubes_common import exceptions as ex
from digicubes_client.client import proxy

logger = logging.getLogger(__name__)


class MailCube:
    @staticmethod
    def get_mail_cube():
        mc = getattr(current_app, "digicubes_mail_cube", None)
        if mc is None:
            raise ex.DigiCubeError("No mailbot in application scope. Not initialized?")
        return mc

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
        assert self.config["smtp_username"] is not None, "SMTP username is None"

        return self.config["smtp_username"]

    @property
    def smtp_password(self):
        assert "smtp_password" in self.config, "SMTP password not configured"
        assert self.config["smtp_password"] is not None, "SMTP password is None"

        return self.config["smtp_password"]

    @property
    def smtp_from_email_addr(self):
        assert "smtp_from_email_addr" in self.config, "SMTP from address not configured"
        assert self.config["smtp_from_email_addr"] is not None, "SMTP from address is None"

        return self.config["smtp_from_email_addr"]

    @property
    def smtp_from_display_name(self):
        assert "smtp_from_display_name" in self.config, "SMTP from display name not configured"
        assert self.config["smtp_from_display_name"] is not None, "SMTP from display name is None"

        return self.config["smtp_from_display_name"]

    @property
    def number_of_workers(self):
        return self.config.get("number_of_workers", 1)

    @property
    def number_of_tries(self):
        return self.config.get("number_of_tries", 1)

    def __init__(self, app=None):

        self.queue = Queue()
        self.workers = []

        self.jinja = Environment(
            loader=PackageLoader("digicubes_flask.email", "templates"),
            autoescape=select_autoescape(["html", "xml"]),
        )
        if app is not None:
            self.init_app(app)

    def init_app(self, app):
        app.digicubes_mail_cube = self
        self.secret = app.config.get("secret", None)
        if self.secret is None:
            raise ex.ConfigurationError("Secret not configured")

        self.config = app.config.get("mail_cube", None)
        if self.config is None:
            raise ex.DigiCubeError("Missing mail_cube configuration")

        for _ in range(self.number_of_workers):
            w = threading.Thread(target=self.__worker__, daemon=True)
            w.start()
            self.workers.append(w)

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

                logger.info("Sending masg: %s", html_text)

                with smtplib.SMTP_SSL(self.smtp_host, self.smtp_port) as mailserver:
                    mailserver.login(self.smtp_username, self.smtp_password)
                    msg = EmailMessage()
                    msg["Subject"] = "Verify your DigiCubes Account"
                    msg.set_content("Automated testmail")
                    msg["To"] = Address(display_name=name, addr_spec=recipient.email)
                    msg["From"] = Address(
                        display_name=self.smtp_from_display_name,
                        addr_spec=self.smtp_from_email_addr,
                    )
                    msg.set_content(plain_text)
                    msg.add_alternative(html_text, subtype="html")
                    mailserver.send_message(msg)

            except Exception:  # pylint: disable=bare-except
                # Something failed, so we put
                # the item back into he queue to try
                # again "later"
                number_of_tries += 1
                if number_of_tries > self.number_of_tries:
                    logger.exception(
                        "Unable to send verification email for user with id %d. Tried %d times.",
                        recipient.id,
                        (number_of_tries - 1),
                    )
                else:
                    self.queue.put(obj)
            finally:
                self.queue.task_done()

    def send_verification_email(self, recipient: proxy.UserProxy):
        from digicubes_flask import digicubes  # pylint: disable=import-outside-toplevel

        if recipient is None:
            raise ValueError("No recipient provided. Cannot send email.")

        if not recipient.email:
            raise ValueError("Recipient has no email address. Cannot send email.")

        token = digicubes.user.get_verification_token(recipient.id)
        url = url_for("admin.verify", token=token, _external=True)
        self.queue.put({"recipient": recipient, "verification_address": url})
