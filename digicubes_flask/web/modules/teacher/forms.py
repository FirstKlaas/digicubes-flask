"""
Some forms to be used with the wtforms package.
"""
import logging
from datetime import date

from flask_wtf import FlaskForm
from wtforms import (BooleanField, DateField, HiddenField, IntegerField,
                     StringField, SubmitField, TextAreaField, validators)

import digicubes_flask.web.wtforms_widgets as w

logger = logging.getLogger(__name__)

__ALL__ = [
    "CourseForm",
    "UnitForm",
]


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
