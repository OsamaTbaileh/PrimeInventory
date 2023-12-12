from flask import Flask, render_template
from routes.user_routes import check_user_id

from routes.user_routes import app as user_app
from routes.locations_routes import app as locations_app
from routes.products_routes import app as products_app
from routes.movements_routes import app as movements_app
from routes.general_routes import app as general_app

app = Flask(__name__, static_folder='static', template_folder='templates')
app.secret_key = 'your_secret_key'  # Add you app secret key here

# Register routes
app.register_blueprint(user_app)
app.register_blueprint(locations_app)
app.register_blueprint(products_app)
app.register_blueprint(movements_app)
app.register_blueprint(general_app)



# Custom 404 error handler:
@app.errorhandler(404)
def not_found_error(e):
    checked_user = check_user_id()
    if checked_user:
            return render_template('general/not_found_error404.html', checked_user=checked_user), 404
    return render_template('general/not_found_error404.html'), 404


if __name__=="__main__":   # Ensure this file is being run directly and not from a different module    
    app.run(debug=True)    # Run the app in debug mode.