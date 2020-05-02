"""
The Admin Blueprint
"""
import logging
from flask import Blueprint, render_template, abort, redirect, url_for

from digicubes_client.client import UserProxy
from digicubes_common.exceptions import DigiCubeError
from digicubes_common.structures import BearerTokenData
from digicubes_flask import login_required, account_manager, request
from .forms import LoginForm, RegisterForm

account_service = Blueprint("account", __name__)

logger = logging.getLogger(__name__)


@account_service.route("/")
@login_required
def index():
    """The home route"""
    return render_template("account/index.jinja")


@account_service.route("/home")
@login_required
def home():
    """Routing to the right home url"""
    token = account_manager.token
    my_roles = account_manager.user.get_my_roles(token, ["name, home_route"])

    if len(my_roles) == 1:
        # Dispatch directly to the right homepage
        rolename = my_roles[0].name
        url = url_for(my_roles[0].home_route)
        logger.debug(
            "User %s has only one role (%s). Redirecting immediately to %s", "me", rolename, url
        )
        return redirect(url)
    # TODO: Filter the roles, that don't have a home route.
    return render_template("account/home.jinja", roles=my_roles)


@account_service.route("/logout", methods=["GET"])
@login_required
def logout():
    """
        Logs current user out.
        Redirects to the configured unauthorized page.
    """
    account_manager.logout()
    return account_manager.unauthorized()


@account_service.route("/login", methods=["GET", "POST"])
def login():
    """
    Login route. On `GET`, it displays the login form.
    on `POST`, it tries to login to the account service.

    If authentification fails, it calls the `unauthorized`
    handler of the `DigicubesAccountManager`.

    If authentification was successful, it calls the
    `successful_logged_in` handler of the
    `DigicubesAccountManager`.
    """
    if account_manager is None:
        return abort(500)

    # If user is already authenticated, then
    # logout first.
    if account_manager.authenticated:
        account_manager.logout()

    form = LoginForm()
    if form.validate_on_submit():
        try:
            user_login = form.login.data
            password = form.password.data
            account_manager.login(user_login, password)
            return home()
        except DigiCubeError:
            return account_manager.unauthorized()

    if request.method == "POST":
        logger.debug("Validation of the form failed")

    return render_template("account/login.jinja", form=form)


@account_service.route("/register", methods=["GET", "POST"])
def register():
    """
    Register a new user.
    """

    # You cannot register, if you are already logged in
    if account_manager.authenticated:
        return account_manager.successful_logged_in()

    form = RegisterForm()
    if form.validate_on_submit():

        try:
            # Need root rights for this
            # FIXME: don't put root credentials in code
            bearer_token: BearerTokenData = account_manager.generate_token_for("root", "digicubes")
            token = bearer_token.bearer_token

            new_user = UserProxy()
            form.populate_obj(new_user)
            new_user.is_active = True
            new_user.id = None  # Just du be shure, we don't have an id in the form accidently
            # and do an update instead of an creation
            new_user.is_verified = account_manager.auto_verify

            # Create a new user in behalf of root
            new_user = account_manager.user.create(token, new_user)

            # Also setting the password in behalf of root
            account_manager.user.set_password(token, new_user.id, form.password.data)

            # If the user has been auto verified, we can directly proceed to the login page.
            # Otherwise we have to show an information to check his email inbox
            # TODO: Pay respect to both situations.
            return account_manager.successful_logged_in()

        except DigiCubeError as e:
            logger.exception("Could not create new account.", exc_info=e)
            abort(500)

    return render_template("account/register.jinja", form=form)
