from typing import Tuple, Dict, Any, Text, Union

import attr

from digicubes_client.client.proxy import UserProxy, SchoolProxy, RoleProxy
from digicubes_flask import digicubes, current_user, CurrentUser
from digicubes_flask.web.account_manager import DigicubesAccountManager

server: DigicubesAccountManager = digicubes
user: CurrentUser = current_user

ValueType = Union[str, float, int, bool]
DataType = Dict[Text, ValueType]


@attr.s(auto_attribs=True)
class RfcRequest:
    # pylint: disable=C0111
    function_name: Text
    data: DataType = {}


@attr.s(auto_attribs=True)
class RfcResponse:
    # pylint: disable=C0111
    status: int = 200
    text: Text = "ok"
    data: DataType = {}


class RfcError(Exception):
    pass


class AdminRFC:

    STATUS_OK = 200

    @staticmethod
    def rfc_user_set_active_state(data: DataType) -> RfcResponse:
        user_id = data.get("user_id", None)
        mode = data.get("mode", "toggle")

        user = server.user.get(server.token, user_id, fields=["is_active"])
        new_state = user.is_active

        if mode == "toggle":
            new_state = not new_state
        elif mode == "on":
            new_state = True
        elif mode == "off":
            new_state = False
        else:
            raise ValueError("Unknown mode")

        if new_state != user.is_active:
            u = UserProxy(id=user_id, is_active=new_state)
            u = server.user.update(server.token, u)

        return RfcResponse(data={"user_id": user_id, "state": new_state})

    @staticmethod
    def rfc_user_toggle_role(data: DataType) -> RfcResponse:
        user_id = data.get("user_id", None)
        role_id = data.get("role_id", None)
        operation = data.get("operation", "toggle")

        assert user_id is not None, "No user id provided"
        assert role_id is not None, "No role id provided"

        if operation == "add":
            server.user.add_role(
                server.token, UserProxy(id=user_id), RoleProxy(id=role_id, name="xxx")
            )
            return RfcResponse(data={"user_id": user_id, "role_id": role_id, "has_role": True})

        if operation == "remove":
            server.user.remove_role(
                server.token, UserProxy(id=user_id), RoleProxy(id=role_id, name="xxx")
            )
            return RfcResponse(data={"user_id": user_id, "role_id": role_id, "has_role": False})

        raise ValueError(f"Unknown or unsupported operation '{operation}'")

    @staticmethod
    def rfc_school_get_course_info(data: DataType) -> RfcResponse:
        school_id = data.get("school_id", None)
        assert school_id is not None, "No school id provided"
        courses = server.school.get_courses(server.token, SchoolProxy(id=school_id))
        # TODO: An dieser stelle brauche ich nicht alle Felder der
        # Kurse. Aber die Methode get_courses unterstützt das

        private_courses = list([c.id for c in courses if c.is_private])
        return RfcResponse(
            data={"count_courses": len(courses), "count_private_courses": len(private_courses)}
        )

    @staticmethod
    def rfc_user_set_verified_state(data: DataType) -> RfcResponse:
        user_id = data.get("user_id", None)
        assert user_id is not None, "No user id provided"

        mode = data.get("mode", "toggle")

        user = server.user.get(server.token, user_id, fields=["is_verified"])
        new_state = user.is_verified

        if mode == "toggle":
            new_state = not new_state
        elif mode == "on":
            new_state = True
        elif mode == "off":
            new_state = False
        else:
            raise ValueError("Unknown mode")

        if new_state != user.is_verified:
            u = UserProxy(id=user_id, is_verified=new_state)
            u = server.user.update(server.token, u)

        return RfcResponse(data={"user_id": user_id, "state": new_state})

    @staticmethod
    def no_such_function(request: RfcRequest) -> RfcResponse:

        return RfcResponse(status=404, text="No such function")

    @staticmethod
    def no_function(request: RfcRequest) -> RfcResponse:

        return RfcResponse(status=400, text="Bad request. No function name provided.")

    @staticmethod
    def call(request: RfcRequest) -> RfcResponse:
        if request.function_name is None:
            return AdminRFC.no_such_function(request)

        method = getattr(AdminRFC, f"rfc_{request.function_name.lower()}", None)
        if method is None:
            return AdminRFC.no_such_function(request)

        if not callable(method):
            return AdminRFC.no_such_function(request)

        return method(request.data)
