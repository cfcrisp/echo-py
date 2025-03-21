from flask import Flask
from app import create_app
from app.models import *
from app.extensions import db

app = create_app()

@app.shell_context_processor
def make_shell_context():
    """Configure shell context for Flask shell."""
    return {
        'db': db,
        'Tenant': Tenant,
        'User': User,
        'Goal': Goal,
        'Initiative': Initiative,
        'Customer': Customer,
        'Idea': Idea,
        'Feedback': Feedback,
        'Comment': Comment
    }

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)