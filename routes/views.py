from flask import Blueprint, render_template, session
from routes.auth import login_required

views_bp = Blueprint('views', __name__)

@views_bp.route('/')
@login_required
def dashboard():
    """Main dashboard"""
    return render_template('dashboard.html', username=session.get('username'))


