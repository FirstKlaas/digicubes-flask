"""
The Admin Blueprint
"""
import logging

from flask import Blueprint, redirect, render_template, url_for
from flask_wtf import FlaskForm
from wtforms import (BooleanField, IntegerField, StringField, SubmitField,
                     TextAreaField, validators)

import digicubes_flask.web.wtforms_widgets as w
from digicubes_flask import (CurrentUser, current_user, digicubes,
                             login_required, requested_html)
from digicubes_flask.client import service as srv
from digicubes_flask.client.model import CourseModel, SchoolModel, UnitModel
from digicubes_flask.web.account_manager import DigicubesAccountManager

unit_service = Blueprint("unit", __name__, url_prefix="/unit")

logger = logging.getLogger(__name__)

server: DigicubesAccountManager = digicubes
user: CurrentUser = current_user

# =========================================================================
# THE FORMS
# =========================================================================


class UnitForm(FlaskForm):
    """
    Unit Form. A unit is a part of a course.
    """

    position = IntegerField(
        "Position",
        widget=w.materialize_input,
        validators=[validators.InputRequired("A name is required"), validators.NumberRange(min=1)],
    )

    name = StringField(
        "Name",
        widget=w.materialize_input,
        validators=[
            validators.InputRequired("A name is required"),
            validators.Length(max=20, message="Maximum length is 20 characters"),
        ],
    )

    short_description = StringField(
        "Short Description",
        widget=w.materialize_input,
        validators=[
            validators.InputRequired("A short description is required"),
            validators.Length(max=64, message="Maximum length is 64 characters"),
        ],
    )

    long_description = TextAreaField(
        "Description",
        widget=w.materialize_textarea,
        validators=[validators.InputRequired("A desciption is required. Markdown is supported")],
    )

    is_active = BooleanField("Active", widget=w.materialize_switch)
    is_visible = BooleanField("Visible", widget=w.materialize_switch)

    submit = SubmitField("Ok", widget=w.materialize_submit)


# =========================================================================
# THE SERVICE ENDPOINTS
# =========================================================================


# DISPLAY COURSE UNIT
# -------------------


@unit_service.route(
    "/school/<int:school_id>/course/<int:course_id>/unit/<int:unit_id>/", methods=("GET", "POST")
)
@login_required
def get(school_id: int, course_id: int, unit_id: int):
    """
    Get the uint details.
    """
    service: srv.SchoolService = digicubes.school
    token = digicubes.token
    db_course: CourseModel = service.get_course_or_none(token, course_id)
    db_school: SchoolModel = service.get(token, school_id)
    db_unit: UnitModel = service.get_unit(token, unit_id)
    if requested_html():
        return render_template("unit/unit.jinja", school=db_school, course=db_course, unit=db_unit)

    return db_unit.json()


# CREATE UNIT
# -----------
@unit_service.route(
    "/school/<int:school_id>/course/<int:course_id>/cunit/", methods=("GET", "POST")
)
@login_required
def create(school_id: int, course_id: int):
    """
    Create a new unit for this course.
    """

    form: UnitForm = UnitForm()

    # if method is post and all fields are valid,
    # create the new unit.
    if form.validate_on_submit():

        new_unit = UnitModel.parse_obj(form.data)
        server.school.create_unit(server.token, course_id, new_unit)

        return redirect(url_for("course.get", school_id=school_id, course_id=course_id))

    return render_template(
        "unit/create_unit.jinja",
        form=form,
        action=url_for("unit.create", school_id=school_id, course_id=course_id),
    )


# UPDATE UNIT
# -----------
@unit_service.route(
    "/school/<int:school_id>/course/<int:course_id>/uunit/<int:unit_id>", methods=("GET", "POST")
)
@login_required
def update(school_id: int, course_id: int, unit_id: int):
    """
    Update an existing unit for this course.
    """
    service: srv.SchoolService = digicubes.school
    token = digicubes.token
    db_unit: UnitModel = service.get_unit(token, unit_id)
    db_course: CourseModel = service.get_course_or_none(token, course_id)
    db_school: SchoolModel = service.get(token, school_id)

    form: UnitForm = UnitForm()

    # if method is post and all fields are valid,
    # create the new unit.
    if form.is_submitted():
        if form.validate():
            updated_unit = UnitModel.parse_obj(form.data)
            updated_unit.id = unit_id
            service.update_unit(token, updated_unit)
            return redirect(
                url_for(
                    "unit.get",
                    school_id=school_id,
                    course_id=course_id,
                    unit_id=unit_id,
                )
            )

    else:
        form.process(obj=db_unit)

    return render_template(
        "unit/update.jinja",
        school=db_school,
        course=db_course,
        unit=db_unit,
        form=form,
        action=url_for("unit.update", school_id=school_id, course_id=course_id, unit_id=unit_id),
    )


# DELETE UNIT
# -----------
@unit_service.route(
    "/school/<int:school_id>/course/<int:course_id>/dunit/<int:unit_id>", methods=("GET",)
)
@login_required
def delete(school_id: int, course_id: int, unit_id: int):
    """
    Delete a new unit for this course.
    """
    service: srv.SchoolService = digicubes.school
    token = digicubes.token

    service.delete_unit(token, unit_id=unit_id)
    
    return redirect(url_for("course.get", school_id=school_id, course_id=course_id))
