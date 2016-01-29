from flask import Blueprint, render_template, abort, redirect, url_for
from jinja2 import TemplateNotFound

mod = Blueprint('main', __name__, url_prefix='')


@mod.route('/')
def index():
    return redirect(url_for('main.home'))


@mod.route('/home')
def home():
    try:
        return render_template('home.html')
    except TemplateNotFound:
        abort(404)
