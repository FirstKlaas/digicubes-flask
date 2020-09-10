"""
The Admin Blueprint
"""
import logging
from flask import Blueprint, render_template, redirect, url_for

from digicubes_flask import login_required, digicubes, current_user
from digicubes_flask.client import proxy
from digicubes_flask.web.account_manager import DigicubesAccountManager

from .forms import UnitForm

teacher_service = Blueprint("teacher", __name__)

logger = logging.getLogger(__name__)

server: DigicubesAccountManager = digicubes


@teacher_service.route("/")
@login_required
def index():
    """The home route"""
    return render_template("teacher/index.jinja")


@teacher_service.route("/home")
@login_required
def home():
    return redirect(url_for("account.home"))


#
# CREATE UNIT
#
@teacher_service.route("/school/<int:school_id>/course/<int:course_id>/cunit/", methods=("GET", "POST"))
@login_required
def create_course_unit(school_id:int, course_id:int):
    """
        Create a new unit for this course.
    """

    form: UnitForm = UnitForm()

    # if method is post and all fields are valid,
    # create the new unit.
    if form.validate_on_submit():

        new_unit = proxy.UnitProxy(created_by_id=current_user.id)

        form.populate_obj(new_unit)
        db_unit: proxy.UnitProxy = server.school.create_unit(server.token, course_id, new_unit)

        # TODO: Redirect to the right url
        return redirect(
            url_for(
                "admin.display_school_course",
                school_id=school_id,
                course_id=course_id
            )
        )

    return render_template(
        "school/create_unit.jinja",
        form=form,
        action=url_for("teacher.create_course_unit", school_id=school_id, course_id=course_id),
    )
