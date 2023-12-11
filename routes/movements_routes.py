from flask import Flask, render_template, redirect, request, session, flash, jsonify, Blueprint
from mysqlconnection import connectToMySQL   # import the function that will return an instance of a connection
from routes.user_routes import check_user_id  # Import the check_user_id function from user_routes.py
from validations.validations import *
from datetime import datetime, timedelta

# app = Flask(__name__, static_folder='../static', template_folder='../templates')
# app.secret_key = 'your_secret_key_here'


app = Blueprint('movements', __name__)


# Render all_movements page.
@app.route("/movements/<movement_type>/<sort_order>")
def render_all_movements_page(movement_type, sort_order):
    checked_user = check_user_id()
    if checked_user:
        mysql = connectToMySQL('primeinventory$prime_inventory')
        if movement_type.lower() == "all":
            # Retrieve all movements with their corresponding from_location, to_location, and product names
            query = """
                SELECT m.*, l1.name AS from_location_name, l2.name AS to_location_name, p.name AS product_name
                FROM movements AS m
                LEFT JOIN locations AS l1 ON m.from_location_id = l1.location_id
                LEFT JOIN locations AS l2 ON m.to_location_id = l2.location_id
                LEFT JOIN products AS p ON m.product_id = p.product_id
                ORDER BY m.updated_at {}""".format(sort_order)
            movements = mysql.query_db(query)
        else:
            num_days = int(movement_type)
            today = datetime.now().date()
            start_date = today - timedelta(days=num_days)
            # Retrieve movements within the specified number of days with their corresponding from_location, to_location, and product names
            query = """
                SELECT m.*, l1.name AS from_location_name, l2.name AS to_location_name, p.name AS product_name
                FROM movements AS m
                LEFT JOIN locations AS l1 ON m.from_location_id = l1.location_id
                LEFT JOIN locations AS l2 ON m.to_location_id = l2.location_id
                LEFT JOIN products AS p ON m.product_id = p.product_id
                WHERE m.created_at >= %(start_date)s
                ORDER BY m.updated_at {}""".format(sort_order)
            data = {"start_date": start_date}
            movements = mysql.query_db(query, data)
        return render_template("movements/all_movements.html", all_movements=movements, checked_user=checked_user)
    return redirect("/sign_out")


# Proccessing filtering movements form on the movements page.
@app.route("/movements/filter_movements", methods=["POST"])
def filter_movements():
    checked_user = check_user_id()
    if checked_user:
        filter_days = request.form.get("filter_days")
        filter_sort = request.form.get("filter_sort")
        
        if (filter_days == ""):
            movement_type = 'all'
        else:
            try:
                num_days = int(filter_days)
                movement_type = str(num_days)
            except ValueError:
                # Handle invalid input here, e.g., display an error message to the user.
                return redirect("/movements/all/ASC", checked_user=checked_user)
        
        return redirect("/movements/{}/{}".format(movement_type, filter_sort))
    return redirect("/sign_out")


# Render view_movement page.
@app.route("/movements/view_movement/<movement_id>")
def render_view_movement_page(movement_id):
    checked_user = check_user_id()
    if checked_user:
        mysql = connectToMySQL('primeinventory$prime_inventory')
        # Retrieve the movement data based on the ID
        movement_query = """SELECT m.*, 
            CONCAT(u.first_name, ' ', u.last_name) AS creator_full_name,
            CONCAT(u2.first_name, ' ', u2.last_name) AS updater_full_name,
            p.name AS product_name,
            l.name AS from_location_name,
            l2.name AS to_location_name
            FROM movements m
                LEFT JOIN users u
                ON m.created_by = u.user_id
                LEFT JOIN users u2
                ON m.updated_by = u2.user_id
                LEFT JOIN products p
                ON m.product_id = p.product_id
                LEFT JOIN locations l
                ON m.from_location_id = l.location_id
                LEFT JOIN locations l2
                ON m.to_location_id = l2.location_id
            WHERE movement_id = %(movement_id_from_URL)s;
        """
        data = {'movement_id_from_URL': movement_id}
        movement = mysql.query_db( movement_query, data)[0]
        movement['creator_full_name'] = movement['creator_full_name'] if movement['creator_full_name'] is not None else "Deleted User"
        movement['updater_full_name'] = movement['updater_full_name'] if movement['updater_full_name'] is not None else "Deleted User"

        return render_template("movements/view_movement.html", the_movement=movement, checked_user=checked_user)
    return redirect("/sign_out")


# Render add_movement_form page.
@app.route("/movements/add_new_movement")
def render_add_movement_form():
    checked_user = check_user_id()
    if checked_user:
        mysql = connectToMySQL('primeinventory$prime_inventory')
        locations = mysql.query_db("""SELECT location_id, name 
                                        FROM locations
                                        WHERE location_id != 'del'
                                        ORDER BY 
                                        CASE WHEN location_id = 'out' THEN 0 ELSE 1 END,
                                        LOWER(name);""")
        return render_template("movements/add_movement_form.html", locations=locations, checked_user=checked_user)
    return redirect("/sign_out")


# Render update_movement_form page.
@app.route("/movements/update_movement/<movement_id>")
def render_update_movement_form(movement_id):
    checked_user = check_user_id()
    if checked_user:
        mysql = connectToMySQL('primeinventory$prime_inventory')
        # Retrieve the movement data based on the ID
        movement_query = "SELECT * FROM movements WHERE movement_id = %(movement_id_from_URL)s"
        data = {'movement_id_from_URL': movement_id}
        movement = mysql.query_db(movement_query, data)
        
        mysql = connectToMySQL('primeinventory$prime_inventory')
        # Retrieve other necessary data for the locations.
        locations = mysql.query_db("""SELECT location_id, name 
                                        FROM locations
                                        WHERE location_id != 'del'
                                        ORDER BY 
                                        CASE WHEN location_id = 'out' THEN 0 ELSE 1 END,
                                        LOWER(name);""")        
        mysql = connectToMySQL('primeinventory$prime_inventory')
        # Retrieve other necessary data for the product of the movement.
        product_query = """
            SELECT product_id, name AS product_name 
            FROM products WHERE product_id= %(product_id)s
        """
        data ['product_id']= movement[0]['product_id']
        product = mysql.query_db(product_query, data)

        return render_template("movements/update_movement_form.html", the_movement=movement[0], all_locations=locations, the_product=product[0], checked_user=checked_user)
    return redirect("/sign_out")


#  AJAX request to retrieve the corresponding based on the selected From Location in the add_movement_form.
# Get products based on location ID.
@app.route("/products/get_products_by_location/<location_id>")
def get_products_by_location(location_id):
    checked_user = check_user_id()
    if checked_user:
        mysql = connectToMySQL('primeinventory$prime_inventory')
        query = """
            SELECT p.product_id, p.name, p.price,
                (COALESCE(SUM(CASE WHEN m.to_location_id = %(location_id_form_AJAX)s THEN m.quantity ELSE 0 END), 0) - COALESCE(SUM(CASE WHEN m.from_location_id = %(location_id_form_AJAX)s THEN m.quantity ELSE 0 END), 0)) AS total_quantity
            FROM products p
            LEFT JOIN movements m ON p.product_id = m.product_id
            WHERE (m.to_location_id = %(location_id_form_AJAX)s OR m.from_location_id = %(location_id_form_AJAX)s)
            GROUP BY p.product_id, p.name, p.price
            HAVING total_quantity > 0;
        """
        data = {'location_id_form_AJAX': location_id}
        products = mysql.query_db(query, data)
        return jsonify(products)
    return redirect("/sign_out")


# AJAX request to retrieve all products
@app.route("/products/get_all_products")
def get_all_products():
    checked_user = check_user_id()
    if checked_user:
        mysql = connectToMySQL('primeinventory$prime_inventory')
        query = "SELECT product_id, name FROM products WHERE product_id != 'del' ORDER BY LOWER(name);"
        products = mysql.query_db(query)
        return jsonify(products)
    return redirect("/sign_out")


# Adding new movement to database.
@app.route("/movements/add_new_movement", methods=["POST"])
def add_new_movement():
    checked_user = check_user_id()
    if checked_user:
        data, validation_errors = validate_add_new_movement_method(request.form)

        if validation_errors:
            for error in validation_errors:
                flash(error)
            return redirect("/movements/add_new_movement")

        mysql = connectToMySQL('primeinventory$prime_inventory')
        # Add movement to the movements table with the product ID, location, and quantity.
        movement_query = """INSERT INTO movements (movement_id, product_id, quantity, from_location_id, to_location_id, created_by, updated_by)
                            VALUES (%(movement_id_from_form)s, 
                                %(product_id_from_form)s, 
                                %(movement_quantity_from_form)s,
                                %(from_location_id_from_form)s,
                                %(to_location_id_from_form)s,
                                %(creation_user_id)s,
                                %(creation_user_id)s)"""
        new_movement = mysql.query_db(movement_query, data)
        return redirect("/movements/all/DESC")
    return redirect("/sign_out")


# Update movement in the databse.
@app.route("/movements/update_movement", methods=["POST"])
def update_movement():
    checked_user = check_user_id()
    if checked_user:
        # Passing the data from the form to the validation method to validate it first then return the valid values from it.
        data, validation_errors = validate_update_movement_method(request.form)

        if validation_errors:
            for error in validation_errors:
                flash(error)
            return redirect("/movements/update_movement/" + str(data['old_movement_id_from_form']))

        mysql = connectToMySQL('primeinventory$prime_inventory')
        query = """
            UPDATE movements 
            SET movement_id = %(movement_id_from_form)s, 
                product_id = %(product_id_from_form)s, 
                quantity = %(movement_quantity_from_form)s, 
                from_location_id = %(from_location_id_from_form)s,
                to_location_id = %(to_location_id_from_form)s,
                updated_by = %(updation_user_id)s
            WHERE movement_id = %(old_movement_id_from_form)s
        """
        updated_movement = mysql.query_db(query, data)
        return redirect("/movements/all/ASC")
    return redirect("/sign_out")


# Delete a movement.
@app.route("/movements/delete_movement/<movement_id>", methods=["POST"])
def delete_movement(movement_id):
    checked_user = check_user_id()
    if checked_user:
        mysql = connectToMySQL('primeinventory$prime_inventory')
        # Delete the movement from the 'movements' table
        query = "DELETE FROM movements WHERE movement_id = %(movement_id_from_URL)s"
        data = {'movement_id_from_URL': movement_id}
        mysql.query_db(query, data)
        url = request.referrer 
        return redirect(url)
    return redirect("/sign_out")