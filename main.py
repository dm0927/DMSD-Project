import os
import sys
from flask import Flask
from dotenv import load_dotenv
load_dotenv()

# added so modules can be found between the two different lookup states:
# from tests and from regular running of the app

CURR_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.append(CURR_DIR)


def create_app(config_filename=''):
    app = Flask(__name__)
    app.static_folder = 'static'
    with app.app_context():
        from views.index import home
        app.register_blueprint(home)

        # an example of making a global function available in jinja templates
        # https://flask-caching.readthedocs.io/en/latest/
        @app.template_global()
        # def get_companies():
        #     from sql.db import DB
        #     try:
        #         print("get companies")
        #         # note this triggers for GET and POST
        #         result = DB.selectAll("SELECT id, name FROM IS601_MP3_Companies")
        #         if result.status:
        #             return result.rows or []
        #     except Exception as e:
        #         print(e)
        #     return []
        # DON'T DELETE, this cleans up the DB connection after each request
        # this avoids sleeping queries
        @app.teardown_request 
        def after_request_cleanup(ctx):
            from sql.db import DB
            DB.close()
        return app


app = create_app()

if __name__ == "__main__":
    app.run(debug=True, host='0.0.0.0', port=int(os.environ.get('PORT', 8000)))
