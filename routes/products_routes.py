from flask import Flask, render_template, redirect, request, session, flash, Blueprint
from mysqlconnection import connectToMySQL   # import the function that will return an instance of a connection
from routes.user_routes import check_user_id  # Import the check_user_id function from user_routes.py
from validations.validations import *

# app = Flask(__name__, static_folder='../static', template_folder='../templates')
# app.secret_key = 'your_secret_key_here'


app = Blueprint('products', __name__)



# Render all_products page.
@app.route("/products")
def render_all_products_page():
    checked_user = check_user_id()
    if checked_user:
        mysql = connectToMySQL('primeinventory$prime_inventory')
        products = mysql.query_db("SELECT * FROM products WHERE product_id != 'del';")
        return render_template("products/all_products.html", all_products=products, checked_user=checked_user)
    return redirect("/sign_out")


# Render view_product page.
@app.route("/products/view_product/<product_id>")
def render_view_product_page(product_id):
    checked_user = check_user_id()
    if checked_user:
        mysql = connectToMySQL('primeinventory$prime_inventory')
        # Retrieve the product's data based on the product's ID.
        product_query = """SELECT p.*, CONCAT(u.first_name, ' ', u.last_name) AS creator_full_name, CONCAT(u2.first_name, ' ', u2.last_name) AS updater_full_name
            FROM products p
            LEFT JOIN users u
            ON p.created_by = u.user_id
            LEFT JOIN users u2
            ON p.updated_by = u2.user_id
            WHERE product_id = %(product_id_from_URL)s;
        """
        data = {'product_id_from_URL': product_id}
        product = mysql.query_db(product_query, data)[0]
        product['creator_full_name'] = product['creator_full_name'] if product['creator_full_name'] is not None else "Deleted User"
        product['updater_full_name'] = product['updater_full_name'] if product['updater_full_name'] is not None else "Deleted User"

        mysql = connectToMySQL('primeinventory$prime_inventory')
        # Retrieve the product's locations data based on the product's ID.
        locations_query = """
            SELECT l.location_id, l.name AS location_name,
                COALESCE(SUM(CASE WHEN m.to_location_id = l.location_id THEN m.quantity END), 0) -
                COALESCE(SUM(CASE WHEN m.from_location_id = l.location_id THEN m.quantity END), 0) AS total_quantity
            FROM locations l
            JOIN movements m ON l.location_id = m.to_location_id OR l.location_id = m.from_location_id
            WHERE m.product_id = %(product_id_from_URL)s And l.location_id !='out'
            GROUP BY l.location_id, l.name
            HAVING total_quantity > 0;
        """
        locations = mysql.query_db(locations_query, data)
        return render_template("products/view_product.html", the_product=product, all_locations=locations, checked_user=checked_user)
    return redirect("/sign_out")


# Render add_product_form page.
@app.route("/products/add_new_product/<location_id>")   #When reached from an add button in a specefic location view page.
@app.route("/products/add_new_product")                 #When reached from an add button in the "Products" page.                           
def render_add_product_form(location_id=None):          #Whether there is a parameter passed or not, it will work.
    checked_user = check_user_id()
    if checked_user:
        mysql = connectToMySQL('primeinventory$prime_inventory')
        # Fetch all existing products from the database.
        products = mysql.query_db("SELECT * FROM products WHERE product_id != 'del' ORDER BY LOWER(name);")

        mysql = connectToMySQL('primeinventory$prime_inventory')
        # Fetch all existing locations from the database.
        locations = mysql.query_db("""SELECT * 
                                    FROM locations 
                                    WHERE location_id != 'del' 
                                    ORDER BY 
                                    CASE WHEN location_id = 'out' THEN 0 ELSE 1 END,
                                    LOWER(name);""")

        mysql = connectToMySQL('primeinventory$prime_inventory')
        # Fetch the specefic location name and ID, When reached from an add button in a specefic location view page.
        query = ("SELECT location_id, name AS Location_name FROM locations WHERE location_id = %(location_id_from_URL)s;")
        data = {'location_id_from_URL': location_id}
        location = mysql.query_db(query, data)
        return render_template("products/add_product_form.html", all_locations=locations, all_products = products, the_location = location, checked_user=checked_user)
    return redirect("/sign_out")


# Render update_product_form page.
@app.route("/products/update_product/<product_id>")
def render_update_product_form(product_id):
    checked_user = check_user_id()
    if checked_user:
        mysql = connectToMySQL('primeinventory$prime_inventory')
        # Retrieve the product data from the database.
        product_query = "SELECT * FROM products WHERE product_id = %(product_id_from_URL)s;"
        data = {'product_id_from_URL': product_id}
        product = mysql.query_db(product_query, data)
        return render_template("products/update_product_form.html", the_product=product[0], checked_user=checked_user)
    return redirect("/sign_out")


# Adding new product to database.
@app.route("/products/add_new_product", methods=["POST"])
def add_new_product():
    checked_user = check_user_id()
    if checked_user:
        # Passing the data from the form to the validation method to validate it first then return the valid values from it.
        data, validation_errors, first_sec_validation = validate_add_new_product_method(request.form)

        if validation_errors:
            for error in validation_errors:
                flash(error)
            session['first_sec_validation'] = first_sec_validation
            return redirect("/products/add_new_product")

        # If the first checkbox is checked (add existing product).
        if 'new_product_checkbox' not in request.form:
            mysql = connectToMySQL('primeinventory$prime_inventory')
            # Add movement to the movements table with the product ID, location, and quantity.
            movement_query = """
                INSERT INTO movements (movement_id, product_id, quantity, from_location_id, to_location_id, created_by, updated_by)
                VALUES (
                    %(movement_id_1_from_form)s, 
                    %(product_id_from_form)s, 
                    %(product_quantity_1_from_form)s,
                    'out',
                    %(product_to_location_id_1_from_form)s,
                    %(creation_user_id)s,
                    %(creation_user_id)s
                )
            """
            new_movement = mysql.query_db(movement_query, data)
            return redirect("/locations/view_location/" + str(data['product_to_location_id_1_from_form']))

        # If the second checkbox is checked (add new product).
        else:
            mysql = connectToMySQL('primeinventory$prime_inventory')
            # Insert a new product into the products table.
            product_query = """
                INSERT INTO products (product_id, name, price, created_by, updated_by)
                VALUES (
                    %(product_id_2_from_form)s, 
                    %(product_name_2_from_form)s, 
                    %(product_price_2_from_form)s,
                    %(creation_user_id)s,
                    %(creation_user_id)s
                )
            """
            new_product = mysql.query_db(product_query, data)
            mysql = connectToMySQL('primeinventory$prime_inventory')
            # Add movement to the movements table with the product ID, location, and quantity.
            movement_query = """
                INSERT INTO movements (movement_id, product_id, quantity, from_location_id, to_location_id, created_by, updated_by)
                VALUES (
                    %(movement_id_2_from_form)s, 
                    %(product_id_2_from_form)s, 
                    %(product_quantity_2_from_form)s,
                    'out',
                    %(product_to_location_id_2_from_form)s,
                    %(creation_user_id)s,
                    %(creation_user_id)s
                )
            """
            new_movement = mysql.query_db(movement_query, data)
            return redirect("/locations/view_location/" + str(data['product_to_location_id_2_from_form']))

        return redirect("/products/add_new_product")
    return redirect("/sign_out")


# Update product in the database.
@app.route("/products/update_product", methods=["POST"])
def update_product():
    checked_user = check_user_id()
    if checked_user:
        # Passing the data from the form to the validation method to validate it first then return the valid values from it.
        data, validation_errors = validate_update_product_method(request.form)

        if validation_errors:
            for error in validation_errors:
                flash(error)
            return redirect("/products/update_product/" + str(data['old_product_id_from_form']))

        mysql = connectToMySQL('primeinventory$prime_inventory')
        update_product_query = """
            UPDATE products 
            SET product_id = %(product_id_from_form)s,
                name = %(product_name_from_form)s, 
                price = %(product_price_from_form)s,
                updated_by = %(updation_user_id)s
            WHERE product_id = %(old_product_id_from_form)s
        """
        mysql.query_db(update_product_query, data)
        return redirect("/products")
    return redirect("/sign_out")


# Delete a product.
@app.route("/products/delete_product/<product_id>", methods=["POST"])
def delete_product(product_id):
    checked_user = check_user_id()
    if checked_user:
        data = {'product_id_from_URL': product_id}

        mysql = connectToMySQL('primeinventory$prime_inventory')
        # Update the movements with the deleted product's ID in their "product_id".
        update_product_ID_in_movements_query = """
            UPDATE movements
            SET product_id = 'del'
            WHERE product_id = %(product_id_from_URL)s;
        """
        mysql.query_db(update_product_ID_in_movements_query, data)

        mysql = connectToMySQL('primeinventory$prime_inventory')
        # Delete the product from the 'products' table.
        delete_product_query = """
            DELETE FROM products 
            WHERE product_id = %(product_id_from_URL)s
        """
        mysql.query_db(delete_product_query, data)
        url = request.referrer 
        return redirect(url)
    return redirect("/sign_out")