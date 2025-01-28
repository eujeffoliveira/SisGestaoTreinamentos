from flask import Blueprint

bp = Blueprint('cargo', __name__, url_prefix='/cargos')

from app.cargo import routes
