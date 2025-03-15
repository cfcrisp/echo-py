from flask import Blueprint

bp = Blueprint('api', __name__)

# Import routes after creating the blueprint to avoid circular imports
from app.api import tenants, users, goals, initiatives, customers, ideas, feedback, comments