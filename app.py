from app import create_app, db
from flask import url_for, get_flashed_messages

from app.models import User, Group

app = create_app()

@app.shell_context_processors
def make_shell_context():
    return {'db': db, 'User': User, 'Group': Group}

if __name__ == '__main__':
    app.run(debug=True)

