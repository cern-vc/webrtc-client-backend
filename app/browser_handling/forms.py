from flask.ext.wtf import Form
from wtforms import HiddenField, StringField, IntegerField, BooleanField, SelectMultipleField
from wtforms.validators import DataRequired
from flask.ext.wtf import Form
from wtforms import widgets
from wtforms.widgets import html_params, HTMLString

from app.browser_handling.models import OperatingSystemFactory


class CheckboxListWidget(object):
    """
    Renders a list of fields as a `ul` or `ol` list.

    This is used for fields which encapsulate many inner fields as subfields.
    The widget will try to iterate the field to get access to the subfields and
    call them to render them.

    If `prefix_label` is set, the subfield's label is printed before the field,
    otherwise afterwards. The latter is useful for iterating radios or
    checkboxes.
    """

    def __init__(self, prefix_label=True):
        self.prefix_label = prefix_label

    def __call__(self, field, **kwargs):
        kwargs.setdefault('id', field.id)
        html = []
        for subfield in field:
            if self.prefix_label:
                html.append(' %s %s ' % (subfield.label, subfield()))
            else:
                html.append(' %s %s ' % (subfield(), subfield.label))
        return HTMLString(' '.join(html))


class MultiCheckboxField(SelectMultipleField):
    widget = CheckboxListWidget(prefix_label=False)
    option_widget = widgets.CheckboxInput()


class DeleteManagedBrowserForm(Form):
    managed_browser_id = HiddenField('Managed Browser ID', [DataRequired()])


class AddOperatingSystemForm(Form):
    operating_system_name = StringField('Name', [DataRequired()])


class AddBrowserForm(Form):
    browser_name = StringField('Name', [DataRequired()])


class DeleteOperatingSystemForm(Form):
    operating_system_id = HiddenField('Operating System ID', [DataRequired()])


class DeleteBrowserForm(Form):
    browser_id = HiddenField('Browser ID', [DataRequired()])


class AddManagedBrowserForm(Form):
    add_managed_browser_id = IntegerField('Browser Name', [DataRequired()])
    add_managed_browser_version = StringField('Version', [DataRequired()])
    add_managed_browser_disabled = BooleanField('Disabled')

    add_operating_systems = MultiCheckboxField('Operating Systems', choices=[], coerce=int)

    def __init__(self, *args, **kwargs):
        super(AddManagedBrowserForm, self).__init__(*args, **kwargs)
        self.add_operating_systems.choices = [(operating_system.id, operating_system.name) for operating_system in
                                              OperatingSystemFactory.fetch_all()]


class EditManagedBrowserForm(Form):
    edit_managed_browser_browser_id = HiddenField('Managed Browser ID', [DataRequired()])
    edit_managed_browser_id = IntegerField('Browser ID', [DataRequired()])
    edit_managed_browser_version = StringField('Version', [DataRequired()])
    edit_managed_browser_disabled = BooleanField('Disabled')

    edit_operating_systems = MultiCheckboxField('Operating Systems', choices=[], coerce=int)

    def __init__(self, *args, **kwargs):
        super(EditManagedBrowserForm, self).__init__(*args, **kwargs)
        self.edit_operating_systems.choices = [(operating_system.id, operating_system.name) for operating_system in
                                               OperatingSystemFactory.fetch_all()]
