from flask import Flask, render_template, redirect, request, flash, Blueprint
import base64
from datetime import datetime, timedelta
from mysqlconnection import connectToMySQL   # import the function that will return an instance of a connection
from routes.user_routes import check_user_id  # Import the check_user_id function from user_routes.py
from validations.validations import *

# app = Flask(__name__, static_folder='../static', template_folder='../templates')
# app.secret_key = 'your_secret_key_here'


app = Blueprint('locations', __name__)



# Render all_locations page. 
@app.route("/locations")
def render_all_locations_page():
    checked_user = check_user_id()
    if checked_user:
        mysql = connectToMySQL('primeinventory$prime_inventory')
        locations = mysql.query_db("SELECT * FROM locations WHERE location_id NOT IN ('del', 'out');")
        return render_template("locations/all_locations.html", all_locations=locations, checked_user=checked_user)
    return redirect("/sign_out")


# Render view_location page.
@app.route("/locations/view_location/<location_id>")
def render_view_locaiton_page(location_id):
    checked_user = check_user_id()
    if checked_user:
        mysql = connectToMySQL('primeinventory$prime_inventory')
        # Retrieve the location's data based on the location's ID.
        location_query = """SELECT l.*, CONCAT(u.first_name, ' ', u.last_name) AS creator_full_name, CONCAT(u2.first_name, ' ', u2.last_name) AS updater_full_name
            FROM locations l
            LEFT JOIN users u
            ON l.created_by = u.user_id
            LEFT JOIN users u2
            ON l.updated_by = u2.user_id
            WHERE location_id = %(location_id_from_URL)s;
        """
        data = {'location_id_from_URL': location_id}
        location = mysql.query_db(location_query, data)[0]
        location['creator_full_name'] = location['creator_full_name'] if location['creator_full_name'] is not None else "Deleted User"
        location['updater_full_name'] = location['updater_full_name'] if location['updater_full_name'] is not None else "Deleted User"

        mysql = connectToMySQL('primeinventory$prime_inventory')
        # Retrieve the location's products data based on the location's ID.
        products_query = """
            SELECT p.product_id, p.name, p.price,
                COALESCE(SUM(CASE WHEN m.to_location_id = %(location_id_from_URL)s THEN m.quantity END), 0) AS total_in_quantity,
                COALESCE(SUM(CASE WHEN m.from_location_id = %(location_id_from_URL)s THEN m.quantity END), 0) AS total_out_quantity,
                COALESCE(SUM(CASE WHEN m.to_location_id = %(location_id_from_URL)s THEN m.quantity END), 0) - COALESCE(SUM(CASE WHEN m.from_location_id = %(location_id_from_URL)s THEN m.quantity END), 0) AS total_quantity
            FROM products p
            LEFT JOIN movements m ON p.product_id = m.product_id
            WHERE p.product_id != 'del' AND (m.to_location_id = %(location_id_from_URL)s OR m.from_location_id = %(location_id_from_URL)s)
            GROUP BY p.product_id, p.name, p.price
            HAVING total_quantity >= 0;
        """
        products = mysql.query_db(products_query, data)
        return render_template("locations/view_location.html", the_location=location, all_products=products, checked_user=checked_user)
    return redirect("/sign_out")


# Render add_location_form page.
@app.route("/locations/add_new_location")
def render_add_location_form():
    checked_user = check_user_id()
    if checked_user:
        return render_template("locations/add_location_form.html", checked_user=checked_user)
    return redirect("/sign_out")


# Render update_location_form page.
@app.route("/locations/update_location/<location_id>")
def render_update_location_form(location_id):
    checked_user = check_user_id()
    if checked_user:
        mysql = connectToMySQL('primeinventory$prime_inventory')
        # Retrieve the location data based on the location's ID.
        query = "SELECT * FROM locations WHERE location_id = %(location_id_from_URL)s"
        data = {'location_id_from_URL': location_id,}
        location = mysql.query_db(query, data)
        return render_template("locations/update_location_form.html", the_location=location[0], checked_user=checked_user)
    return redirect("/sign_out")


# Adding new location to database.
@app.route("/locations/add_new_location", methods=["POST"])
def add_new_location():
    checked_user = check_user_id()
    if checked_user:
        data, validation_errors = validate_add_new_location_method(request.form, request.files)

        # Passing the data from the form to the validation method to validate it first then return the valid values from it.
        if validation_errors:
            for error in validation_errors:
                flash(error)
            return redirect("/locations/add_new_location")

        mysql = connectToMySQL('primeinventory$prime_inventory')
        query = """
            INSERT INTO locations (location_id, name, image_id, created_by, updated_by) 
            VALUES (
                %(location_id_from_form)s, 
                %(location_name_from_form)s, 
                %(location_image_from_form)s,
                %(creation_user_id)s,
                %(creation_user_id)s
            );
        """
        new_location = mysql.query_db(query, data)
        return redirect("/locations")
    return redirect("/sign_out")


# Update location in the database.
@app.route("/locations/update_location", methods=["POST"])
def update_location():
    checked_user = check_user_id()
    if checked_user:
        data, validation_errors = validate_update_location_method(request.form, request.files)

        # Passing the data from the form to the validation method to validate it first then return the valid values from it.
        if validation_errors:
            for error in validation_errors:
                flash(error)
            return redirect("/locations/update_location/" + str(data['old_location_id_from_form']))

        mysql = connectToMySQL('primeinventory$prime_inventory')
        update_location_query = """
            UPDATE locations 
            SET location_id = %(location_id_from_form)s,
                name = %(location_name_from_form)s, 
                image_id = %(location_image_from_form)s,
                updated_by = %(updation_user_id)s
            WHERE location_id = %(old_location_id_from_form)s
        """
        mysql.query_db(update_location_query, data)

        return redirect("/locations")
    return redirect("/sign_out")


# Delete a location.
@app.route("/locations/delete_location/<location_id>", methods=["POST"])
def delete_location(location_id):
    checked_user = check_user_id()
    if checked_user:
        data = {'location_id_from_URL': location_id}

        mysql = connectToMySQL('primeinventory$prime_inventory')
        # Update the movements with the deleted location's ID in their "from_location_id".
        update_from_movements_query = """
            UPDATE movements
            SET from_location_id = 'del'
            WHERE from_location_id = %(location_id_from_URL)s;
        """
        mysql.query_db(update_from_movements_query, data)

        # Update the movements with the deleted location's ID in their "to_location_id".
        mysql = connectToMySQL('primeinventory$prime_inventory')
        update_to_movements_query = """
            UPDATE movements
            SET to_location_id = 'del'
            WHERE to_location_id = %(location_id_from_URL)s;
        """
        mysql.query_db(update_to_movements_query, data)

        mysql = connectToMySQL('primeinventory$prime_inventory')
        # Delete the location from the 'locations' table.
        delete_location_query = """
            DELETE FROM locations 
            WHERE location_id = %(location_id_from_URL)s
        """
        mysql.query_db(delete_location_query, data)

        return redirect("/locations")
    return redirect("/sign_out")