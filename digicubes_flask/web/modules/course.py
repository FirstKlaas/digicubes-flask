"""
The Course Blueprint
"""
from datetime import date
import logging

from flask import Blueprint, render_template, redirect, url_for
from flask_wtf import FlaskForm
from wtforms import (
    StringField,
    SubmitField,
    validators,
    TextAreaField,
    BooleanField,
    HiddenField,
    DateField,
)

from digicubes_flask.client import proxy, service as srv
from digicubes_flask import (
    login_required,
    current_user,
    digicubes,
    CurrentUser,
    exceptions as ex,
)

from digicubes_flask.web.account_manager import DigicubesAccountManager

import digicubes_flask.web.wtforms_widgets as w

blueprint = Blueprint("course", __name__, url_prefix="/course")

logger = logging.getLogger(__name__)

server: DigicubesAccountManager = digicubes
user: CurrentUser = current_user

# =========================================================================
# THE FORMS
# =========================================================================

class CourseForm(FlaskForm):
    """
    Create new Course Form
    """

    school_id = HiddenField()
    name = StringField(
        "Name",
        widget=w.materialize_input,
        validators=[validators.InputRequired("A name is required")],
    )

    description = TextAreaField(
        "Description",
        widget=w.materialize_textarea,
        validators=[validators.InputRequired("A desciption is required")],
    )

    from_date = DateField(
        "Starting from",
        default=date.today(),
        format="%d.%m.%Y",
        widget=w.materialize_picker,
        validators=[validators.InputRequired("The course needs a starting date.")],
    )

    until_date = DateField(
        "Ending at",
        default=date.today(),
        format="%d.%m.%Y",
        widget=w.materialize_picker,
        validators=[validators.InputRequired("A course needs a ending date.")],
    )

    is_private = BooleanField("Private", widget=w.materialize_switch)

    submit = SubmitField("Ok", widget=w.materialize_submit)

# =========================================================================
# THE ROUTES
# =========================================================================

@blueprint.route("/school/<int:school_id>/dcourse/<int:course_id>/")
def delete(school_id: int, course_id: int):
    """
    Delete an existing course.
    """
    token = digicubes.token
    service: srv.SchoolService = digicubes.school

    # Deleteing the course
    # TODO: catch 404
    try:
        service.delete_course(token, course_id)
    except ex.NotAuthenticated:
        return redirect(url_for("admin.login"))

    return redirect(url_for("school.get", school_id=school_id))


@blueprint.route("/school/<int:school_id>/ucourse/<int:course_id>/", methods=["GET", "POST"])
@login_required
def update(school_id: int, course_id: int):
    """
    Update an existing course
    """
    service: srv.SchoolService = digicubes.school
    token = digicubes.token
    form = CourseForm()

    # First get the course to be updated
    service.get_courses(token, proxy.SchoolProxy(id=school_id))

    # if method is post and all fields are valid,
    # create the new course.
    if form.validate_on_submit():

        course = proxy.CourseProxy()
        form.populate_obj(course)
        course.school_id = int(course.school_id)
        course.id = int(course_id)
        service.update_course(token, course)
        return redirect(url_for("school.get", school_id=school_id))

    school_proxy: proxy.SchoolProxy = service.get(token, school_id)
    course: proxy.CourseProxy = service.get_course(token, course_id)
    action_url = url_for(
        "course.update", school_id=school_proxy.id, course_id=course.id
    )
    form = CourseForm(obj=course)
    form.submit.label.text = "Update"
    return render_template(
        "admin/update_course.jinja",
        school=school_proxy,
        course=course,
        form=form,
        action=action_url,
    )


#
# DISPLAY COURSE
#
@blueprint.route("/school/<int:school_id>/gcourse/<int:course_id>", methods=("GET", "POST"))
@login_required
def get(school_id: int, course_id: int):
    """
    Display a single course.
    """
    service: srv.SchoolService = digicubes.school
    token = digicubes.token
    db_course: proxy.CourseProxy = service.get_course_or_none(token, course_id)
    db_school: proxy.SchoolProxy = service.get(token, school_id)

    # If there is no course, we just display the
    # school details
    if db_course is None:
        return db_school(school_id)

    # Get all the course units
    db_units = service.get_units(token, course_id)
    return render_template("admin/course.jinja", school=db_school, course=db_course, units=db_units)


#
# CREATE COURSE
#
@blueprint.route("/school/<int:school_id>/ccourse/", methods=("GET", "POST"))
@login_required
def create(school_id: int):
    """
        Create a new course for the school

        The method GET will render the creation form, while
        the method POST will validate the form and create the
        course, if possible.

        If any errors occure during the validation of the form,
        the form will be rerendered.
    """

    # Create the form instance
    form: CourseForm = CourseForm()

    # if method is post and all fields are valid,
    # create the new course.
    if form.validate_on_submit():

        new_course = proxy.CourseProxy(created_by_id=current_user.id)
        form.populate_obj(new_course)

        # Create the course.
        # TODO: Errors may occoure and have to be handled in a proper way.
        server.school.create_course(server.token, proxy.SchoolProxy(id=school_id), new_course)

        # After succesfully creating the course go back to
        # the administration page of the school.
        return redirect(url_for("school.get", school_id=school_id))

    # Get the school proxy from the server and render out the form.
    token: str = server.token
    school_proxy: proxy.SchoolProxy = server.school.get(token, school_id)
    form.submit.label.text = "Create"
    action_url = url_for("course.create", school_id=school_proxy.id)
    return render_template(
        "admin/create_course.jinja", school=school_proxy, form=form, action=action_url,
    )
