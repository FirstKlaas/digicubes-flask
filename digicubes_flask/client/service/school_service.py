"""
All service calls for schooles.
"""
import logging
from typing import List, Optional

from digicubes_flask.client.model import (CourseModel, SchoolModel, UnitModel,
                                          UserModel)

from .abstract_service import AbstractService

SchoolList = Optional[List[SchoolModel]]
CourseList = Optional[List[CourseModel]]
UnitList = Optional[List[UnitModel]]

logger = logging.getLogger(__name__)

XFieldList = Optional[List[str]]


class SchoolService(AbstractService):
    """
    School services
    """

    def all(self, token) -> SchoolList:
        """
        Returns all schools.
        The result is a list of ``SchoolModel`` objects.
        """
        headers = self.create_default_header(token)
        url = self.url_for("/schools/")
        response = self.requests.get(url, headers=headers)

        self.check_response_status(response, expected_status=200)

        return [SchoolModel.parse_obj(school) for school in response.json()]

    def get(self, token, school_id: int, fields: XFieldList = None) -> Optional[SchoolModel]:
        """
        Get a single school specified by its id

        Requested Endpoint: `/school/{school_id}`
        """
        headers = self.create_default_header(token)
        if fields is not None:
            headers[self.X_FILTER_FIELDS] = ",".join(fields)

        url = self.url_for(f"/school/{school_id}")
        response = self.requests.get(url, headers=headers)
        self.check_response_status(response, expected_status=200)

        return SchoolModel.parse_obj(response.json())

    def get_by_name(self, token: str, name: str) -> SchoolModel:
        """
        Get a single school by the name.

        Endpoint: /school/byname/{name}
        Method: GET
        """
        response = self.requests.get(
            self.url_for(f"/school/byname/{name}"), headers=self.create_default_header(token)
        )
        self.check_response_status(response, expected_status=200)
        return SchoolModel.parse_obj(response.json())

    def update(self, token, school: SchoolModel) -> SchoolModel:
        """
        Update an existing school.
        If successfull, a new school model is returned with the latest version of the
        school data.
        """

        headers = self.create_default_header(token)
        url = self.url_for(f"/school/{school.id}")
        response = self.requests.put(url, data=school.json(), headers=headers)
        self.check_response_status(response, expected_status=200)

        return SchoolModel.parse_obj(response.json())

    def delete(self, token, school_id: int) -> Optional[SchoolModel]:
        """
        Deletes a school from the database
        """
        headers = self.create_default_header(token)
        url = self.url_for(f"/school/{school_id}")
        response = self.requests.delete(url, headers=headers)
        self.check_response_status(response, expected_status=200)
        return SchoolModel.parse_obj(response.json())

    def create(self, token, school: SchoolModel) -> SchoolModel:
        """
        Create a new school
        """
        headers = self.create_default_header(token)
        data = school.json()
        url = self.url_for("/schools/")
        response = self.requests.post(url, data=data, headers=headers)
        self.check_response_status(response, expected_status=201)
        return SchoolModel.parse_obj(response.json())

    def delete_all(self, token: str) -> None:
        """
        Deletes all schools from the database. This operation is atomic.
        A successful operation is indicated by a 200 status.
        If the operation fails, a ``ServerError`` is thrown.

        .. warning:: This operation cannot be undone. So be shure you know, what you are doing.
        """
        headers = self.create_default_header(token)
        url = self.url_for("/schools/")
        response = self.requests.delete(url, headers=headers)
        self.check_response_status(response, expected_status=200)

    def create_course(self, token: str, school: SchoolModel, course: CourseModel) -> CourseModel:
        headers = self.create_default_header(token)
        course.school_id = school.id
        data = course.json()
        url = self.url_for(f"/school/{school.id}/courses/")
        response = self.requests.post(url, data=data, headers=headers)
        self.check_response_status(response, expected_status=201)
        return CourseModel.parse_obj(response.json())

    def get_courses(self, token: str, school: SchoolModel) -> CourseList:
        """
        Get a list of courses, associated with the provided school.
        """
        response = self.requests.get(
            self.url_for(f"/school/{school.id}/courses/"), headers=self.create_default_header(token)
        )
        self.check_response_status(response, expected_status=200)
        return [CourseModel.parse_obj(course) for course in response.json()]

    def get_course(self, token: str, course_id: int) -> CourseModel:
        """
        Get an course by id.

        We do not need an school id, as course ids are unique.
        For security reasons, we should check if this course is
        within the scope of the current user. But for the time
        beeing, we are optimistic.
        """
        # TODO: Check rights
        headers = self.create_default_header(token)
        url = self.url_for(f"/course/{course_id}")
        response = self.requests.get(url, headers=headers)
        self.check_response_status(response, expected_status=200)

        return CourseModel.parse_obj(response.json())

    def get_course_or_none(self, token: str, course_id: int) -> Optional[CourseModel]:
        """
        Returns the CourseModel for the requested course is or None, if
        any prerequisite does not match (Does not exist, not enough rigths, ...)
        """
        try:
            return self.get_course(token, course_id)
        except Exception:  # pylint: disable=bare-except
            return None

    def delete_course(self, token: str, course_id: int) -> CourseModel:
        """
        Delete a course specified by it's id

        We do not need an school id, as course ids are unique.
        For security reasons, we should check if this course is
        within the scope of the current user. But for the time
        beeing, we are optimistic.

        Currently no rights are checked.
        """
        # TODO: Check rights
        headers = self.create_default_header(token)
        url = self.url_for(f"/course/{course_id}")
        response = self.requests.delete(url, headers=headers)
        self.check_response_status(response, expected_status=200)
        return CourseModel.parse_obj(response.json())

    def update_course(self, token: str, updated_course: CourseModel) -> CourseModel:
        """
        Update an existing course specified by it's id of the course.

        We do not need an school id, as course ids are unique.
        For security reasons, we should check if this course is
        within the scope of the current user. But for the time
        beeing, we are optimistic.

        Currently not rights are checked.

        Raises an DoesNotExist error, if the course does not exist.
        Raises an TokenExpired, if the login token has expired.

        """
        headers = self.create_default_header(token)
        url = self.url_for(f"/course/{updated_course.id}")
        response = self.requests.put(url, data=updated_course.json(), headers=headers)
        self.check_response_status(response, expected_status=200)
        return CourseModel.parse_obj(response.json())

    def get_units(self, token: str, course_id: int) -> UnitList:
        headers = self.create_default_header(token)
        url = self.url_for(f"/course/{course_id}/units/")
        response = self.requests.get(url, headers=headers)
        self.check_response_status(response, expected_status=200)
        return [UnitModel.parse_obj(unit) for unit in response.json()]

    def get_unit(self, token: str, unit_id: int) -> UnitModel:
        headers = self.create_default_header(token)
        url = self.url_for(f"/unit/{unit_id}")
        response = self.requests.get(url, headers=headers)
        self.check_response_status(response, expected_status=200)
        return UnitModel.parse_obj(response.json())

    def create_unit(self, token: str, course_id: int, unit: UnitModel) -> CourseModel:
        headers = self.create_default_header(token)
        data = unit.json()
        url = self.url_for(f"/course/{course_id}/units/")
        response = self.requests.post(url, data=data, headers=headers)
        self.check_response_status(response, expected_status=201)
        return UnitModel.parse_obj(response.json())

    def update_unit(self, token: str, unit: UnitModel) -> UnitModel:
        headers = self.create_default_header(token)
        url = self.url_for(f"/unit/{unit.id}")
        response = self.requests.put(url, headers=headers, data=unit.json())
        self.check_response_status(response, expected_status=200)
        return UnitModel.parse_obj(response.json())

    def delete_unit(self, token: str, unit_id: int) -> UnitModel:
        headers = self.create_default_header(token)
        url = self.url_for(f"/unit/{unit_id}")
        response = self.requests.delete(url, headers=headers)
        self.check_response_status(response, expected_status=200)
        return UnitModel.parse_obj(response.json())

    def get_school_teacher(self, token: str, school_id: int) -> List[UserModel]:
        headers = self.create_default_header(token)
        url = self.url_for(f"/school/{school_id}/teacher/")
        response = self.requests.get(url, headers=headers)
        self.check_response_status(response, expected_status=200)
        return [UserModel.parse_obj(user) for user in response.json()]

    def _get_space_schools(self, token, user: UserModel, space: str) -> List[SchoolModel]:
        headers = self.create_default_header(token)
        url = self.url_for(f"/user/{user.id}/{space}/schools/")
        response = self.requests.get(url, headers=headers)
        self.check_response_status(response, expected_status=200)
        return [SchoolModel.parse_obj(school) for school in response.json()]

    def get_headmaster_schools(self, token, user: UserModel) -> List[SchoolModel]:
        return self._get_space_schools(token, user, "headmaster")

    def get_teacher_schools(self, token, user: UserModel) -> List[SchoolModel]:
        return self._get_space_schools(token, user, "teacher")

    def get_student_schools(self, token, user: UserModel) -> List[SchoolModel]:
        return self._get_space_schools(token, user, "student")

    def add_teacher(self, token: str, school: SchoolModel, teacher: UserModel) -> bool:
        headers = self.create_default_header(token)
        url = self.url_for(f"/school/{school.id}/teacher/{teacher.id}/")
        response = self.requests.put(url, headers=headers)
        return response.status_code == 200

    def remove_teacher(self, token: str, school: SchoolModel, teacher: UserModel) -> bool:
        headers = self.create_default_header(token)
        url = self.url_for(f"/school/{school.id}/teacher/{teacher.id}/")
        response = self.requests.delete(url, headers=headers)
        return response.status_code == 200
