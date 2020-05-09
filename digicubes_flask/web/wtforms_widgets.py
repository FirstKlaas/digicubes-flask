"""
Some form widgets.
"""
import logging

from datetime import date

from wtforms import Field
from wtforms.widgets import html_params

from markupsafe import Markup, escape

logger = logging.getLogger(__name__)


def materialize_password(field: Field, **kwargs):
    """
    A widget for the materialize input field.
    """
    field_id = kwargs.pop("id", field.id)
    field_type = kwargs.get("type", "password")

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
    html.append(f"<label {html_params(**label_params)}>{ escape(label) }</label>")
    if len(field.errors) > 0:
        error_text = ", ".join(field.errors)
        attributes = {"class": "red-text"}
        html.append(f"<span { html_params(**attributes) }>{ error_text }</span>")
    html.append("</div>")

    return "".join(html)


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
        attributes["value"] = escape(field.data)

    if "data-length" in kwargs:
        attributes["data-length"] = kwargs["data-length"]

    grid = kwargs.get("grid", "")
    outer_params = {"class": f"input-field col {grid}"}

    label_params = {"for": field_id}

    # label = kwargs.get("label", field_id)
    label = field.label
    html = [f"<div {html_params(**outer_params)}>"]
    html.append(f"<input {html_params(**attributes)}></input>")
    html.append(f"<label {html_params(**label_params)}>{ escape(label) }</label>")
    if len(field.errors) > 0:
        error_text = ", ".join(field.errors)
        attributes = {"class": "red-text"}
        html.append(f"<span { html_params(**attributes) }>{ error_text }</span>")
    html.append("</div>")

    return "".join(html)


def materialize_textarea(field: Field, **kwargs):
    """
    A widget for the materialize textarea.
    """
    field_id = kwargs.pop("id", field.id)

    attributes = {
        "id": field_id,
        "name": field_id,
        "class": "materialize-textarea",
        "required": "",
    }

    content = ""

    if field.data is not None and kwargs.get("value", True):
        content = field.data

    if "data-length" in kwargs:
        attributes["data-length"] = kwargs["data-length"]

    grid = kwargs.get("grid", "")
    outer_params = {"class": f"input-field col {grid}"}

    label_params = {"for": field_id}

    label = field.label
    html = [f"<div {html_params(**outer_params)}>"]
    html.append(f"<textarea {html_params(**attributes)}>{ escape(content) }</textarea>")
    html.append(f"<label {html_params(**label_params)}>{ escape(label) }</label>")
    if len(field.errors) > 0:
        error_text = ", ".join(field.errors)
        attributes = {"class": "red-text"}
        html.append(f"<span { html_params(**attributes) }>{ error_text }</span>")
    html.append("</div>")

    return Markup("".join(html))


def materialize_switch(field, **kwargs):

    field_id = kwargs.pop("id", field.id)

    attributes = {
        "id": field_id,
        "name": field_id,
        "type": "checkbox",
    }

    grid = kwargs.get("grid", "s12")  # Default, if no grid was specified
    outer_params = {"class": f"switch col {grid}"}

    return f"""
        <div {html_params(**outer_params)}>
            <label>
                {kwargs.get('checked_label','Yes')}
                <input {html_params(**attributes)}>
                <span class='lever'></span>
                {kwargs.get('unchecked_label','No')}
            </label>
        </div>
    """


def materialize_picker(field, **kwargs):
    """
    A Widget to render an date picker
    """

    grid = kwargs.get("grid", "s12")  # Default, if no grid was specified
    outer_params = {"class": f"switch col {grid}"}

    field_id = kwargs.pop("id", field.id)

    date_value: date = field.data

    attributes = {
        "id": field_id,
        "name": field_id,
        "type": "text",
        "value": date_value.strftime("%d.%m.%Y"),
        "class": "datepicker",
    }

    return f"""
        <div {html_params(**outer_params)}>
        <label for='{field_id}'>{ field.label }</label>
        <input {html_params(**attributes)}></input>
        </div>
    """


def materialize_checkbox(field, **kwargs):

    field_id = kwargs.pop("id", field.id)

    div_params = {"class": f"switch col {kwargs.pop('grid', 's12')}"}
    input_params = {
        "id": field_id,
        "name": field_id,
        "type": "checkbox",
        "class": "filled-in",
    }
    if field.data:
        input_params["checked"] = "checked"

    return f"""
    <div {html_params(**div_params)}>    
        <label>
            <input {html_params(**input_params)} ></input>
            <span>{field.label}</span>
        </label>
    </div>
    """


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
    html.append(f"<i class='material-icons right'>{ icon}</i>")
    html.append("</button>")
    return "".join(html)
