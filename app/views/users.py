from flask import Blueprint
from flask import flash
from flask import redirect
from flask import url_for

from flask_login import logout_user, login_required


users_bp = Blueprint('users', __name__, url_prefix='/users')


@users_bp.route('/logout')
@login_required
def logout():
    logout_user()
    flash("You have logged out")
    return redirect(url_for('main.home'))