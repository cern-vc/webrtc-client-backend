from flask import Blueprint, render_template, redirect, url_for, request, jsonify, current_app

from app.extensions import db
from app.decorators import requires_login, admin_required
from app.forms.browser_handling import DeleteManagedBrowserForm, AddOperatingSystemForm, AddBrowserForm, \
    DeleteBrowserForm, DeleteOperatingSystemForm, AddManagedBrowserForm, EditManagedBrowserForm, \
    process_operating_system_add, process_browser_add, process_operating_system_delete, process_browser_delete, \
    process_managed_browser_delete_form, process_managed_browser_add, process_managed_browser_edit
from app.models.browser_handling import Browser, OperatingSystem, ManagedBrowser

mod = Blueprint('browser_handling', __name__, url_prefix='/admin/browser-handling')


@mod.route('/managed-browsers/', methods=['GET', 'POST'])
@requires_login
@admin_required
def list_all():
    """
        Managed Browsers list
    :return:
    """

    operating_systems = OperatingSystem.query.filter_by(disabled=False).all()
    browsers = Browser.query.filter_by(disabled=False).all()
    managed_browsers = ManagedBrowser.query.all()

    form = DeleteManagedBrowserForm(request.form)
    if form.validate_on_submit():
        form = process_managed_browser_delete_form(form)

    add_managed_browser_form = AddManagedBrowserForm(request.form)
    if add_managed_browser_form.validate_on_submit():
        add_managed_browser_form = process_managed_browser_add(add_managed_browser_form)

    edit_managed_browser_form = EditManagedBrowserForm(request.form)
    if edit_managed_browser_form.validate_on_submit():
        edit_managed_browser_form = process_managed_browser_edit(edit_managed_browser_form)

    if True in [form, add_managed_browser_form, edit_managed_browser_form]:
        return redirect(url_for('browser_handling.list_all'))

    return render_template('browser_handling/list.html', edit_managed_browser_form=edit_managed_browser_form,
                           add_managed_browser_form=add_managed_browser_form, form=form,
                           operating_systems=operating_systems,
                           browsers=browsers,
                           managed_browsers=managed_browsers,
                           application_root=current_app.config.get("APPLICATION_ROOT", ""))


@mod.route('/configuration/', methods=['GET', 'POST'])
@requires_login
@admin_required
def configuration():
    """
        View to manage the browsers and the operating systems.
    :return:
    """
    operating_systems = OperatingSystem.query.filter_by(disabled=False).all()
    browsers = Browser.query.filter_by(disabled=False).all()

    add_os_form = AddOperatingSystemForm(request.form, prefix="add_os_form")
    if add_os_form.validate_on_submit():
        add_os_form = process_operating_system_add(add_os_form)

    add_browser_form = AddBrowserForm(request.form, prefix="add_browser_form")
    if add_browser_form.validate_on_submit():
        add_browser_form = process_browser_add(add_browser_form)

    delete_operating_system_form = DeleteOperatingSystemForm(request.form)
    if delete_operating_system_form.validate_on_submit():
        delete_operating_system_form = process_operating_system_delete(delete_operating_system_form)

    delete_browser_form = DeleteBrowserForm(request.form)
    if delete_browser_form.validate_on_submit():
        delete_browser_form = process_browser_delete(delete_browser_form)

    if True in [add_os_form, add_browser_form, delete_browser_form, delete_operating_system_form]:
        return redirect(url_for('browser_handling.configuration'))

    return render_template('browser_handling/configuration.html',
                           delete_operating_system_form=delete_operating_system_form,
                           delete_browser_form=delete_browser_form,
                           add_os_form=add_os_form,
                           add_browser_form=add_browser_form,
                           operating_systems=operating_systems,
                           browsers=browsers)


@mod.route('/_switch_managed_browser_switch/', methods=['GET'])
@requires_login
@admin_required
def _switch_managed_browser_switch():
    """
    View to manage the switch of the managed browser version. It is activated using an AJAX call.
    :return:
    """
    managed_browser_id = request.args.get('managed_browser_id', -1, type=int)
    current_app.logger.info("Managed browser " + str(managed_browser_id) + " switched.")
    if managed_browser_id is not -1:
        managed_browser = ManagedBrowser.query.filter_by(id=managed_browser_id).first()
        if managed_browser:
            managed_browser.allow_version = (not managed_browser.allow_version)
            db.session.commit()
            return jsonify(success=True)

    return jsonify(success=False)
