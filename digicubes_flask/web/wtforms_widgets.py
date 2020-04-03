"""
Some form widgets.
"""
import logging

from wtforms import Field
from wtforms.widgets import html_params

logger = logging.getLogger(__name__)


def materialize_input(field: Field, **kwargs):
    """
    A widget for the materialize input field.
    """
    field_id = kwargs.pop("id", field.id)
    field_type = kwargs.get("type", "text")

    attributes = {
        "id": field_id,
        "name": field_id,
        "type": field_type,
        "class": "validate",
        "required": "",
    }

    if field.data is not None and kwargs.get("value", True):
        attributes["value"] = field.data

    if "data-length" in kwargs:
        attributes["data-length"] = kwargs["data-length"]

    grid = kwargs.get("grid", "")
    outer_params = {"class": f"input-field col {grid}"}

    label_params = {"for": field_id}

    # label = kwargs.get("label", field_id)
    label = field.label
    html = [f"<div {html_params(**outer_params)}>"]
    html.append(f"<input {html_params(**attributes)}></input>")
    html.append(f"<label {html_params(**label_params)}>{ label }</label>")
    if len(field.errors) > 0:
        error_text = ", ".join(field.errors)
        attributes = {"class": "red-text"}
        html.append(f"<span { html_params(**attributes) }>{ error_text }</span>")
    html.append("</div>")

    return "".join(html)


def materialize_submit(field, **kwargs):
    """
    A widget for the materialize submit button.
    """
    field_id = kwargs.pop("id", field.id)
    field_type = kwargs.get("type", "submit")
    label = field.label.text
    icon = kwargs.get("icon", "send")

    button_attrs = {
        "id": field_id,
        "type": field_type,
        "class": "btn light-blue lighten-1 waves-effect waves-light",
    }

    html = [f"<button {html_params(**button_attrs)}>{label}"]
    html.append(f"<i class='material-icons right'>{icon}</i>")
    html.append("</button>")
    return "".join(html)
