# Starting of the app
from flask import Flask
from backend.models import db
from backend.init_db import setup_admin

app = None

def setup_app():
    global app
    app = Flask(__name__)
    app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///quiz_app.sqlite3" # Having db file
    app.config["SECRET_KEY"] = "your-secret-key-here"  # Add secret key for session management
    db.init_app(app) # Flask app connected to db (SQLAlchemy)
    app.app_context().push() # Direct access to other modules
    app.debug = True
    print("Quiz Master app is started...")

# Call the setup
setup_app()



from backend.controllers import *

if __name__ == "__main__":
    setup_admin(app)
    app.run()
