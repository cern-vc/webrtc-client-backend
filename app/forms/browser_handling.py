from flask import flash, current_app
from flask.ext.wtf import Form
from wtforms import HiddenField, StringField, IntegerField, BooleanField, SelectMultipleField
from wtforms import widgets
from wtforms.validators import DataRequired
from wtforms.widgets import HTMLString

from app.extensions import db
from app.models.browser_handling import OperatingSystem, Browser, ManagedBrowser


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
    """
        Multi Checkbox field
    """
    widget = CheckboxListWidget(prefix_label=False)
    option_widget = widgets.CheckboxInput()


class DeleteManagedBrowserForm(Form):
    """
        Form to delete a ManagedBrowser
    """
    managed_browser_id = HiddenField('Managed Browser ID', [DataRequired()])


class AddOperatingSystemForm(Form):
    """
    Form to add an OperatingSystem
    """
    operating_system_name = StringField('Name', [DataRequired()])


class AddBrowserForm(Form):
    """
    Form to add a Browser
    """
    browser_name = StringField('Name', [DataRequired()])


class DeleteOperatingSystemForm(Form):
    """
    Form to delete an OperatingSystem
    """
    operating_system_id = HiddenField('Operating System ID', [DataRequired()])


class DeleteBrowserForm(Form):
    """
    Form to delete a browser
    """
    browser_id = HiddenField('Browser ID', [DataRequired()])


class AddManagedBrowserForm(Form):
    """
        Form to add a new ManagedBrowser
    """
    add_managed_browser_id = IntegerField('Browser Name', [DataRequired()])
    add_managed_browser_version = StringField('Version', [DataRequired()])
    add_managed_browser_allow_version = BooleanField('Allow Version')
    add_managed_browser_allow_lower_versions = BooleanField('Allow lower versions')
    add_managed_browser_allow_higher_versions = BooleanField('Allow higher versions')

    add_operating_systems = MultiCheckboxField('Operating Systems', choices=[], coerce=int)

    def __init__(self, *args, **kwargs):
        super(AddManagedBrowserForm, self).__init__(*args, **kwargs)
        self.add_operating_systems.choices = [(operating_system.id, operating_system.name) for operating_system in
                                              OperatingSystem.query.filter_by(disabled=False)]


class EditManagedBrowserForm(Form):
    """
        Form to edit an existing ManagedBrowser
    """
    edit_managed_browser_browser_id = HiddenField('Managed Browser ID', [DataRequired()])
    edit_managed_browser_id = IntegerField('Browser ID', [DataRequired()])
    edit_managed_browser_version = StringField('Version', [DataRequired()])
    edit_managed_browser_allow_version = BooleanField('Allow Version')
    edit_managed_browser_allow_lower_versions = BooleanField('Allow lower versions')
    edit_managed_browser_allow_higher_versions = BooleanField('Allow higher versions')

    edit_operating_systems = MultiCheckboxField('Operating Systems', choices=[], coerce=int)

    def __init__(self, *args, **kwargs):
        super(EditManagedBrowserForm, self).__init__(*args, **kwargs)
        self.edit_operating_systems.choices = [(operating_system.id, operating_system.name) for operating_system in
                                               OperatingSystem.query.filter_by(disabled=False)]


def process_operating_system_add(form):
    """
        Handles the submission of a new OperatingSystem
    :param add_os_form: The form to process
    :return: True if is valid or the form
    """
    operating_system_name = form.operating_system_name.data
    new_os = OperatingSystem.query.filter_by(name=operating_system_name).first()
    if not new_os:
        new_os = OperatingSystem(name=operating_system_name)
        db.session.add(new_os)
    else:
        if not new_os.disabled:
            flash('Unable to add Operating System', "red")
            return form
        new_os.disabled = False
    db.session.commit()

    flash('Operating System was successfully added', "light-green")
    return True


def process_browser_add(form):
    """
        Handles the submission of a new Browser
    :param form: The form to process
    :return: True if is valid or the form if it is not
    """
    browser_name = form.browser_name.data

    new_browser = Browser.query.filter_by(name=browser_name).first()
    if not new_browser:
        new_browser = Browser(name=browser_name)
        db.session.add(new_browser)
    else:
        if not new_browser.disabled:
            flash('Unable to add Browser', "red")
            return form
        new_browser.disabled = False
    db.session.commit()

    flash('Browser was successfully added', "light-green")
    return True

    # return add_browser_form


def process_operating_system_delete(form):
    """
        Handles the deletion of an OperatingSystem
    :param form: The form to process
    :return: True if is valid or the form if it is not
    """
    operating_system_id = form.operating_system_id.data

    operating_system = OperatingSystem.query.filter_by(id=int(operating_system_id)).first()
    operating_system.disabled = True
    db.session.commit()

    if operating_system:
        if operating_system.disabled:
            flash('Operating System was successfully deleted', "light-green")
            return True
        else:
            flash('Unable to delete Operating System', "red")


def process_browser_delete(form):
    """
        Handles the deletion of a Browser
    :param add_browser_form: The form to process
    :return: True if is valid or the form if it is not
    """
    browser_id = form.browser_id.data

    browser = Browser.query.filter_by(id=browser_id).first()
    if browser.disabled:
        flash('Unable to delete Browser', "red")

    browser.disabled = True
    db.session.commit()

    if browser:
        flash('Browser was successfully deleted', "light-green")
        return True


def process_managed_browser_edit(form):
    """
        Handles the updating of a ManagedBrowser
    :param form: Form to process
    :return: True if the ManagedBrowser was updated or the form if it is not
    """
    # # create an user instance not yet stored in the database
    browser_id = form.edit_managed_browser_browser_id.data
    managed_browser_id = form.edit_managed_browser_id.data
    version = form.edit_managed_browser_version.data
    allow_version = True if form.edit_managed_browser_allow_version.data else False
    allow_lower_versions = True if form.edit_managed_browser_allow_lower_versions.data else False
    allow_higher_versions = True if form.edit_managed_browser_allow_higher_versions.data else False
    operating_systems_ids = form.edit_operating_systems.data

    browser = Browser.query.filter_by(id=int(browser_id)).first()
    operating_systems = []

    for operating_system_id in operating_systems_ids:
        current_app.logger.debug(operating_system_id)
        operating_system = OperatingSystem.query.filter_by(id=int(operating_system_id)).first()
        if operating_system:
            operating_systems.append(operating_system)

    new_managed_browser = ManagedBrowser.query.filter_by(id=managed_browser_id).first()

    if new_managed_browser:
        new_managed_browser.browser_id = browser.id
        new_managed_browser.version = version
        new_managed_browser.allow_version = allow_version
        new_managed_browser.allow_lower_versions = allow_lower_versions
        new_managed_browser.allow_higher_versions = allow_higher_versions
        new_managed_browser.operating_systems = operating_systems
        db.session.commit()

    if new_managed_browser:
        flash('Managed browser ' + browser.name + ' ' + version + ' was successfully updated', "light-green")
        return True
    else:
        flash('Unable to update managed browser ' + browser.name + ' ' + version, "red")
        return form


def process_managed_browser_add(form):
    """
        Handles the submission of a new ManagedBrowser
    :param form: The form to process
    :return: True if the ManagedBrowser was added or the form if it is not
    """
    # # create an user instance not yet stored in the database
    managed_form_id = form.add_managed_browser_id.data
    version = form.add_managed_browser_version.data
    allow_version = True if form.add_managed_browser_allow_version.data else False
    allow_lower_versions = True if form.add_managed_browser_allow_lower_versions.data else False
    allow_higher_versions = True if form.add_managed_browser_allow_higher_versions.data else False
    operating_systems_ids = form.add_operating_systems.data

    browser = Browser.query.filter_by(id=int(managed_form_id)).first()
    operating_systems_to_add = []
    new_managed_browser = None

    already_existsing_managed_browser = ManagedBrowser.query.filter_by(browser_id=int(managed_form_id)).first()

    if not already_existsing_managed_browser:
        for operating_system_id in operating_systems_ids:
            current_app.logger.debug(operating_system_id)
            operating_system = OperatingSystem.query.filter_by(id=int(operating_system_id)).first()
            if operating_system:
                operating_systems_to_add.append(operating_system)

        new_managed_browser = ManagedBrowser(browser_id=browser.id, version=version,
                                             allow_version=allow_version,
                                             allow_lower_versions=allow_lower_versions,
                                             allow_higher_versions=allow_higher_versions,
                                             operating_systems=operating_systems_to_add)
        db.session.add(new_managed_browser)
        db.session.commit()

    if new_managed_browser:
        flash('Managed browser ' + browser.name + ' ' + version + ' was successfully created', "light-green")
        return True
    else:
        flash('Unable to create managed browser ' + browser.name + ' ' + version, "red")
        return form


def process_managed_browser_delete_form(form):
    """
        Handles the deletion of a ManagedBrowser
    :param form: Form to process
    :return: True if the ManagedBrowser was deleted or the form if it is not
    """
    # create an user instance not yet stored in the database
    managed_browser_id = form.managed_browser_id.data
    managed_browser = ManagedBrowser.query.get_or_404(managed_browser_id)
    current_app.logger.info("Current managed_form_id")
    if managed_browser:
        db.session.delete(managed_browser)
        db.session.commit()
        flash(
            'Managed Browser ' + managed_browser.browser.name + ' ' + managed_browser.version + ' was successfully deleted',
            "light-green")
        return True
    return form
