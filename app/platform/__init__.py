from flask import Blueprint

bp = Blueprint('platform', __name__)

from . import routes
