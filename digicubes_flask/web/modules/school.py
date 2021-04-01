"""
The School Blueprint
"""
import logging
from flask import Blueprint, render_template, redirect, url_for
from flask_wtf import FlaskForm
from wtforms import (
    StringField,
    SubmitField,
    validators,
    TextAreaField,
)

from wtforms.validators import ValidationError

from digicubes_flask.client import proxy, service as srv
from digicubes_flask import (
    login_required,
    current_user,
    digicubes,
    CurrentUser,
)

import digicubes_flask.exceptions as ex
from digicubes_flask.web.account_manager import DigicubesAccountManager

import digicubes_flask.web.wtforms_widgets as w

blueprint = Blueprint("school", __name__, url_prefix="/school")

logger = logging.getLogger(__name__)

server: DigicubesAccountManager = digicubes
user: CurrentUser = current_user

# =========================================================================
# THE FORMS
# =========================================================================


class SchoolNameAvailable:
    """
    Field validator to check, if the name (field.data) is available,
    and the school may be created or updated.

    If a school_id is provided, checks, if the school with the name
    is the the same school. Aka, the name hasn't changed. This might
    be the case, when updating a school.
    """

    def __init__(self, school_id: int = None):
        self.school_id = school_id

    def __call__(self, form: FlaskForm, field):
        """
        Checks, if the school already exists, as the name has to be unique
        """
        try:
            if not field.data:
                raise ValidationError("Name may not be empty")

            db_school: proxy.SchoolProxy = digicubes.school.get_by_name(digicubes.token, field.data)

            if self.school_id is not None and db_school.id == self.school_id:
                # Of course the school may keep its name
                return

            # Now we know that there is another school with the same
            # name
            raise ValidationError("School already exists")
        except ex.DoesNotExist:
            pass  # If we can not find the account, that's perfect.


class SchoolForm(FlaskForm):
    """
    Create or update school form
    """

    name = StringField(
        "Name",
        widget=w.materialize_input,
        validators=[validators.InputRequired("A name is required.")],
    )
    description = TextAreaField(
        "Description",
        widget=w.materialize_textarea,
        validators=[validators.InputRequired("A description is required.")],
    )
    submit = SubmitField("Ok", widget=w.materialize_submit)


# =========================================================================
# THE ROUTES
# =========================================================================


@blueprint.route("/all/")
def get_all():
    """
    Display all schools
    """
    school_list = digicubes.school.all(digicubes.token)
    return render_template("school/schools.jinja", schools=school_list)


@blueprint.route("/<int:school_id>/teacher/", methods=("GET",))
def get_school_teacher(school_id: int):
    """
    Get a list of teachers associated with this school.
    """
    teacher = server.school.get_school_teacher(digicubes.token, school_id)
    return teacher


@blueprint.route("/create/", methods=("GET", "POST"))
@login_required
def create():
    """Create a new school"""
    # token = digicubes.token
    form = SchoolForm()
    if form.is_submitted():
        if form.validate({"name": [SchoolNameAvailable()]}):
            new_school = proxy.SchoolProxy(
                name=form.name.data,
                description=form.description.data,
            )
            digicubes.school.create(digicubes.token, new_school)

            # Now lets see, if the current user has the "headmaster" role.
            # if so, make him a headmaster for the newly created school.
            return redirect(url_for("school.get_all"))

    form.submit.label.ttext = "Create"
    return render_template("school/create_school.jinja", form=form, action=url_for("school.create"))


@blueprint.route("/get/<int:school_id>/")
@login_required
def get(school_id: int):
    """Schow details of an existing school"""
    service: srv.SchoolService = digicubes.school
    token = digicubes.token
    # Gettting the school details from the server
    # TODO: Was, wenn die Schule nicht existiert?
    db_school = service.get(token, school_id)
    courses = service.get_courses(token, db_school)
    teacher = service.get_school_teacher(token, school_id)
    return render_template(
        "school/school.jinja", school=db_school, courses=courses, teacher=teacher
    )


@blueprint.route("/update/<int:school_id>/", methods=("GET", "POST"))
@login_required
def update(school_id: int):
    """
    Update the data of an existing school.
    """
    service: srv.SchoolService = digicubes.school
    token = digicubes.token
    form = SchoolForm()
    db_school: proxy.SchoolProxy = service.get(token, school_id)

    # What about the creation date and the modified date?
    if form.is_submitted():
        if form.validate({"name": [SchoolNameAvailable(school_id=school_id)]}):
            upschool = proxy.SchoolProxy()
            form.populate_obj(upschool)
            upschool.id = school_id
            digicubes.school.update(token, upschool)

            return redirect(url_for("school.get", school_id=school_id))
    else:
        # This is the request to display the form with
        # the current data ofthe school
        form = SchoolForm(obj=db_school)

    form.submit.label.text = "Update"

    return render_template(
        "school/update_school.jinja",
        form=form,
        school=db_school,
        action=url_for("school.update", school_id=db_school.id),
    )


@blueprint.route("/delete/<int:school_id>/")
@login_required
def delete(school_id: int):
    """Delete an existing school"""
    token = digicubes.token
    # Gettting the school details from the server
    # TODO: Was, wenn die Schule nicht existiert?
    digicubes.school.delete(token, school_id)
    return redirect(url_for("school.get_all"))
