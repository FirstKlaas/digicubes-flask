"""
All service calls for schooles.
"""
import logging
from typing import Optional, List

from .abstract_service import AbstractService
from ..proxy import SchoolProxy, CourseProxy, UnitProxy, UserProxy

SchoolList = Optional[List[SchoolProxy]]
CourseList = Optional[List[CourseProxy]]
UnitList = Optional[List[UnitProxy]]

logger = logging.getLogger(__name__)

XFieldList = Optional[List[str]]


class SchoolService(AbstractService):
    """
    School services
    """

    def all(self, token) -> SchoolList:
        """
        Returns all schools.
        The result is a list of ``SchoolProxy`` objects.
        """
        headers = self.create_default_header(token)
        url = self.url_for("/schools/")
        response = self.requests.get(url, headers=headers)

        self.check_response_status(response, expected_status=200)

        return [SchoolProxy.structure(school) for school in response.json()]

    def get(self, token, school_id: int, fields: XFieldList = None) -> Optional[SchoolProxy]:
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

        return SchoolProxy.structure(response.json())

    def get_by_name(self, token: str, name: str) -> SchoolProxy:
        """
        Get a single school by the name.

        Endpoint: /school/byname/{name}
        Method: GET
        """
        response = self.requests.get(
            self.url_for(f"/school/byname/{name}"), headers=self.create_default_header(token)
        )
        self.check_response_status(response, expected_status=200)
        return SchoolProxy.structure(response.json())

    def update(self, token, school: SchoolProxy) -> SchoolProxy:
        """
        Update an existing school.
        If successfull, a new school proxy is returned with the latest version of the
        school data.
        """

        headers = self.create_default_header(token)
        url = self.url_for(f"/school/{school.id}")
        response = self.requests.put(url, json=school.unstructure(), headers=headers)
        self.check_response_status(response, expected_status=200)

        return SchoolProxy.structure(response.json())

    def delete(self, token, school_id: int) -> Optional[SchoolProxy]:
        """
        Deletes a school from the database
        """
        headers = self.create_default_header(token)
        url = self.url_for(f"/school/{school_id}")
        response = self.requests.delete(url, headers=headers)
        self.check_response_status(response, expected_status=200)
        return SchoolProxy.structure(response.json())

    def create(self, token, school: SchoolProxy) -> SchoolProxy:
        """
        Create a new school
        """
        headers = self.create_default_header(token)
        data = school.unstructure()
        url = self.url_for("/schools/")
        response = self.requests.post(url, json=data, headers=headers)
        self.check_response_status(response, expected_status=201)
        return SchoolProxy.structure(response.json())

    def create_bulk(self, token, schools: List[SchoolProxy]) -> None:
        """
        Create multiple schools
        """
        headers = self.create_default_header(token)
        data = [school.unstructure() for school in schools]
        url = self.url_for("/schools/")
        response = self.requests.post(url, json=data, headers=headers)
        self.check_response_status(response, expected_status=201)

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

    def create_course(self, token: str, school: SchoolProxy, course: CourseProxy) -> CourseProxy:
        headers = self.create_default_header(token)
        course.school_id = school.id
        data = course.to_json_dict()
        url = self.url_for(f"/school/{school.id}/courses/")
        response = self.requests.post(url, json=data, headers=headers)
        self.check_response_status(response, expected_status=201)
        return CourseProxy.structure(response.json())

    def get_courses(self, token: str, school: SchoolProxy) -> CourseList:
        """
        Get a list of courses, associated with the provided school.
        """
        response = self.requests.get(
            self.url_for(f"/school/{school.id}/courses/"), headers=self.create_default_header(token)
        )
        self.check_response_status(response, expected_status=200)
        return [CourseProxy.structure(course) for course in response.json()]

    def get_course(self, token: str, course_id: int) -> CourseProxy:
        """
        Get an course by id.

        We do not need an school id, as course ids are unique.
        For security reasons, we should check if this course is
        within the scope of the current user. But for the time
        beeing, we are optimistic.
        """
        headers = self.create_default_header(token)
        url = self.url_for(f"/course/{course_id}")
        response = self.requests.get(url, headers=headers)
        self.check_response_status(response, expected_status=200)

        return CourseProxy.structure(response.json())

    def delete_course(self, token: str, course_id: int) -> CourseProxy:
        """
        Delete a course specified by it's id

        We do not need an school id, as course ids are unique.
        For security reasons, we should check if this course is
        within the scope of the current user. But for the time
        beeing, we are optimistic.

        Currently no rights are checked.


        """
        headers = self.create_default_header(token)
        url = self.url_for(f"/course/{course_id}")
        response = self.requests.delete(url, headers=headers)
        self.check_response_status(response, expected_status=200)
        return CourseProxy.structure(response.json())

    def update_course(self, token: str, updated_course: CourseProxy) -> CourseProxy:
        """
        Update an existing course specified by it's id of the proxy.

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
        response = self.requests.put(url, json=updated_course.unstructure(), headers=headers)
        self.check_response_status(response, expected_status=200)
        return CourseProxy.structure(response.json())

    def get_units(self, token: str, course_id: int) -> UnitList:
        headers = self.create_default_header(token)
        url = self.url_for(f"/course/{course_id}/units/")
        response = self.requests.get(url, headers=headers)
        self.check_response_status(response, expected_status=200)

    def create_unit(self, token: str, course_id: int, unit: UnitProxy) -> CourseProxy:
        headers = self.create_default_header(token)
        data = unit.unstructure()
        url = self.url_for(f"/course/{course_id}/units/")
        response = self.requests.post(url, json=data, headers=headers)
        self.check_response_status(response, expected_status=201)
        return UnitProxy.structure(response.json())

    def get_school_teacher(self, token: str, school_id: int) -> List[UserProxy]:
        headers = self.create_default_header(token)
        url = self.url_for(f"/school/{school_id}/teacher/")
        response = self.requests.get(url, headers=headers)
        self.check_response_status(response, expected_status=200)
        return [UserProxy.structure(user) for user in response.json()]
