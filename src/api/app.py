''' Initialize the app '''

from flask import Flask

from src.api import routes
from src.database import database

def create_app():
    ''' create the app '''

    # create and configure the app
    app = Flask(__name__, instance_relative_config=True)

    # init the database
    database.init_db(app)

    # init the routes
    routes.init_routes(app)

    return app

if __name__ == '__main__':
    create_app().run(host='0.0.0.0', port=8000, debug=True)
