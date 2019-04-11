# We create the authentication Blueprint
from flask import Blueprint

bp = Blueprint('auth', __name__)

from . import routes
from ..models import Permission


@bp.app_context_processor
def inject_permissions():
    return dict(Permission=Permission)
