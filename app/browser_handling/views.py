import re
from flask import Blueprint, render_template, abort, redirect, url_for, request, jsonify, flash
from jinja2 import TemplateNotFound

# from app import db
# from app.users.forms import RegisterForm, LoginForm
from app.browser_handling.decorators import requires_login
from app.browser_handling.forms import DeleteManagedBrowserForm, AddOperatingSystemForm, AddBrowserForm, \
    DeleteBrowserForm, DeleteOperatingSystemForm, AddManagedBrowserForm, EditManagedBrowserForm
from app.browser_handling.models import Browser, OperatingSystem, ManagedBrowser, OperatingSystemFactory, \
    BrowserFactory, \
    ManagedBrowserFactory
from flask import current_app


mod = Blueprint('browser_handling', __name__, url_prefix='/browser-handling')


@mod.route('/managed-browsers/', methods=['GET', 'POST'])
@requires_login
def list_all():
    operating_systems = OperatingSystemFactory.fetch_all()
    browsers = BrowserFactory.fetch_all()
    managed_browsers = ManagedBrowserFactory.fetch_all()

    form = process_managed_browser_delete_form()

    add_managed_browser_form = process_managed_browser_add()

    edit_managed_browser_form, operating_systems = process_managed_browser_edit(operating_systems)

    return render_template('browser_handling/list.html', edit_managed_browser_form=edit_managed_browser_form,
                           add_managed_browser_form=add_managed_browser_form, form=form,
                           operating_systems=operating_systems,
                           browsers=browsers,
                           managed_browsers=managed_browsers)


def process_managed_browser_edit(operating_systems):
    edit_managed_browser_form = EditManagedBrowserForm(request.form)
    if edit_managed_browser_form.validate_on_submit():
        current_app.logger.debug("Edit form")
        # # create an user instance not yet stored in the database
        browser_id = edit_managed_browser_form.edit_managed_browser_browser_id.data
        managed_browser_id = edit_managed_browser_form.edit_managed_browser_id.data
        version = edit_managed_browser_form.edit_managed_browser_version.data
        disabled = True if edit_managed_browser_form.edit_managed_browser_disabled.data else False
        operating_systems_ids = edit_managed_browser_form.edit_operating_systems.data
        # current_app.logger.debug(operating_systems_ids)

        browser = BrowserFactory.find_by_id(int(browser_id))
        operating_systems = []

        for operating_system_id in operating_systems_ids:
            current_app.logger.debug(operating_system_id)
            # current_app.logger.debug(operating_system_id['value'])
            operating_system = OperatingSystemFactory.find_by_id(int(operating_system_id))
            if operating_system:
                operating_systems.append(operating_system)

        new_managed_browser = ManagedBrowserFactory.update(managed_browser_id=managed_browser_id, browser_id=browser.id,
                                                           version=version,
                                                           allow_version=disabled,
                                                           op_systems=operating_systems)
        # new_managed_browser = None
        if new_managed_browser:
            flash('Managed browser <strong>' + browser.name + ' ' + version + '</strong> was successfully updated')
            # redirect user to the 'home' method of the user module.
        else:
            flash('Unable to update managed browser <strong>' + browser.name + ' ' + version + '</strong>')
            # redirect user to the 'home' method of the user module.
    return edit_managed_browser_form, operating_systems


def process_managed_browser_add():
    add_managed_browser_form = AddManagedBrowserForm(request.form)
    if add_managed_browser_form.validate_on_submit():
        current_app.logger.debug("Add form")
        # # create an user instance not yet stored in the database
        managed_form_id = add_managed_browser_form.add_managed_browser_id.data
        version = add_managed_browser_form.add_managed_browser_version.data
        disabled = True if add_managed_browser_form.add_managed_browser_disabled.data else False
        operating_systems_ids = add_managed_browser_form.add_operating_systems.data
        # current_app.logger.debug(operating_systems_ids)

        browser = BrowserFactory.find_by_id(int(managed_form_id))
        operating_systems_to_add = []

        for operating_system_id in operating_systems_ids:
            current_app.logger.debug(operating_system_id)
            # current_app.logger.debug(operating_system_id['value'])
            operating_system = OperatingSystemFactory.find_by_id(int(operating_system_id))
            if operating_system:
                operating_systems_to_add.append(operating_system)

        new_managed_browser = ManagedBrowserFactory.create(browser_id=browser.id, version=version,
                                                           allow_version=disabled,
                                                           op_systems=operating_systems_to_add, save=True)
        # new_managed_browser = None
        if new_managed_browser:
            flash('Managed browser <strong>' + browser.name + ' ' + version + '</strong> was successfully created')
            # redirect user to the 'home' method of the user module.
        else:
            flash('Unable to create managed browser <strong>' + browser.name + ' ' + version + '</strong>')
            # redirect user to the 'home' method of the user module.
    return add_managed_browser_form


def process_managed_browser_delete_form():
    form = DeleteManagedBrowserForm(request.form)
    if form.validate_on_submit():
        current_app.logger.debug("Delete form")
        # create an user instance not yet stored in the database
        managed_form_id = form.managed_browser_id.data
        managed_browser = ManagedBrowserFactory.find_by_id(managed_form_id)
        current_app.logger.info("Current managed_form_id")
        if managed_browser:
            was_deleted = ManagedBrowserFactory.delete(managed_browser)
            if was_deleted:
                flash(
                        'Managed Browser <strong>' + managed_browser.browser.name + ' ' + managed_browser.version + '</strong> was successfully deleted')
            else:
                flash(
                        'Unable to delete managed browser <strong>' + managed_browser.browser.name + ' ' + managed_browser.version + '</strong>')
    return form


@mod.route('/configuration/', methods=['GET', 'POST'])
@requires_login
def configuration():
    operating_systems = OperatingSystemFactory.fetch_all()
    browsers = BrowserFactory.fetch_all()

    operating_system_form = process_operating_system_add()

    browser_form = process_browser_add()

    delete_operating_system_form = process_operating_system_delete()

    delete_browser_form = process_browser_delete()
    try:
        return render_template('browser_handling/configuration.html',
                               delete_operating_system_form=delete_operating_system_form,
                               delete_browser_form=delete_browser_form,
                               operating_system_form=operating_system_form,
                               browser_form=browser_form,
                               operating_systems=operating_systems,
                               browsers=browsers)
    except TemplateNotFound:
        abort(404)


@mod.route('/_switch_managed_browser_switch/', methods=['GET'])
@requires_login
def _switch_managed_browser_switch():
    managed_browser_id = request.args.get('managed_browser_id', -1, type=int)

    if managed_browser_id is not -1:
        managed_browser = ManagedBrowserFactory.find_by_id(managed_browser_id)
        if managed_browser:
            result = ManagedBrowserFactory.update(managed_browser_id=managed_browser_id,
                                                  browser_id=managed_browser.browser.id,
                                                  version=managed_browser.version,
                                                  allow_version=(not managed_browser.allow_version),
                                                  op_systems=managed_browser.operating_systems)
            if result:
                return jsonify(success=True)

    return jsonify(success=False)


def process_operating_system_add():
    operating_system_form = AddOperatingSystemForm(request.form)
    if operating_system_form.validate_on_submit():
        operating_system_name = operating_system_form.operating_system_name.data

        new_os = OperatingSystemFactory.create_operating_system(name=operating_system_name, save=True)

        if new_os:
            flash('Operating System was successfully added')
        else:
            flash('Unable to add Operating System')
    return operating_system_form


def process_browser_add():
    browser_form = AddBrowserForm(request.form)
    if browser_form.validate_on_submit():
        browser_name = browser_form.browser_name.data

        new_browser = BrowserFactory.create_browser(name=browser_name, save=True)

        if new_browser:
            flash('Browser was successfully added')
        else:
            flash('Unable to add Browser')
    return browser_form


def process_operating_system_delete():
    delete_operating_system_form = DeleteOperatingSystemForm(request.form)
    if delete_operating_system_form.validate_on_submit():
        operating_system_id = delete_operating_system_form.operating_system_id.data

        operating_system = OperatingSystemFactory.find_by_id(operating_system_id)

        if operating_system:
            was_deleted = OperatingSystemFactory.delete_operating_system(operating_system)
            if was_deleted:
                flash('Operating System was successfully deleted')
            else:
                flash('Unable to delete Operating System')
    return delete_operating_system_form


def process_browser_delete():
    delete_browser_form = DeleteBrowserForm(request.form)
    if delete_browser_form.validate_on_submit():
        browser_id = delete_browser_form.browser_id.data

        browser = BrowserFactory.find_by_id(browser_id)

        if browser:
            was_deleted = BrowserFactory.delete_browser(browser)
            if was_deleted:
                flash('Browser was successfully deleted')
            else:
                flash('Unable to delete Browser')
    return delete_browser_form
