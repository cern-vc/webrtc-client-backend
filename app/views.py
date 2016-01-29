from flask import Blueprint, render_template, abort, redirect, url_for
from jinja2 import TemplateNotFound

mod = Blueprint('main', __name__, url_prefix='/')


@mod.route('/')
def about():
    try:
        return render_template('about.html')
    except TemplateNotFound:
        abort(404)