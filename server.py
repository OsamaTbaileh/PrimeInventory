from flask import Flask, render_template, redirect, request, session, flash, jsonify
import base64
from datetime import datetime, timedelta
from mysqlconnection import connectToMySQL   # import the function that will return an instance of a connection
from validations import *

app = Flask(__name__, static_folder='static')
app.secret_key = 'your_secret_key_here'


# Render the home page.
@app.route("/")
def render_home_page():
    return render_template("general/home_page.html")


# Render the normal_report_page.
@app.route("/normal_report")
def render_report_page():
    mysql = connectToMySQL('prime_inventory')
    products = mysql.query_db("""
        SELECT l.location_id, l.name AS location_name, p.product_id, p.name AS product_name, p.price,
        COALESCE(SUM(CASE WHEN m.to_location_id = l.location_id THEN m.quantity END), 0) AS total_in_quantity,
        COALESCE(SUM(CASE WHEN m.from_location_id = l.location_id THEN m.quantity END), 0) AS total_out_quantity,
        COALESCE(SUM(CASE WHEN m.to_location_id = l.location_id THEN m.quantity END), 0) - COALESCE(SUM(CASE WHEN m.from_location_id = l.location_id THEN m.quantity END), 0) AS total_quantity
        FROM locations l
        CROSS JOIN products p
        LEFT JOIN movements m ON p.product_id = m.product_id
        GROUP BY l.location_id, p.product_id
        HAVING total_in_quantity > 0;
    """)
    return render_template("general/normal_report_page.html", all_products=products)


# Render the advanced_report_page.
@app.route("/advanced_report")
def display_table():
    mysql = connectToMySQL('prime_inventory')
    query = "SELECT DISTINCT product_id, name FROM products"
    products = mysql.query_db(query)

    mysql = connectToMySQL('prime_inventory')
    query = "SELECT DISTINCT location_id, name FROM locations"
    locations = mysql.query_db(query)

    mysql = connectToMySQL('prime_inventory')
    # Fetch product quantities in each location
    query = """
        SELECT l.location_id, l.name AS location_name, p.product_id, p.name AS product_name,
            COALESCE(SUM(CASE WHEN m.to_location_id = l.location_id THEN m.quantity END), 0) -
            COALESCE(SUM(CASE WHEN m.from_location_id = l.location_id THEN m.quantity END), 0) AS total_quantity
        FROM locations l
        CROSS JOIN products p
        LEFT JOIN movements m ON l.location_id = m.to_location_id AND p.product_id = m.product_id
        GROUP BY l.location_id, p.product_id
    """
    table_data = mysql.query_db(query)

    quantity_dict = {}
    for row in table_data:
        location_id = row['location_id']
        product_id = row['product_id']
        quantity = row['total_quantity']
        if location_id not in quantity_dict:
            quantity_dict[location_id] = {}
        quantity_dict[location_id][product_id] = quantity

    return render_template('general/advanced_report_page.html', products=products, locations=locations, quantity_dict=quantity_dict)





# //////////////////////////////////////////////  LOCATIONS ROUTES  //////////////////////////////////////////////
# ////////////////////////////////////////////// ↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓ //////////////////////////////////////////////




# Render all_locations page.
@app.route("/locations")
def render_all_locations_page():
    mysql = connectToMySQL('prime_inventory')
    locations = mysql.query_db("SELECT * FROM locations;")
    return render_template("locations/all_locations.html", all_locations=locations)


# Render view_location page.
@app.route("/locations/view_location/<location_id>")
def render_view_locaiton_page(location_id):
    mysql = connectToMySQL('prime_inventory')
    # Retrieve the location's data based on the location's ID.
    location_query = "SELECT * FROM locations WHERE location_id = %(location_id_from_URL)s"
    data = {'location_id_from_URL': location_id}
    location = mysql.query_db(location_query, data)

    mysql = connectToMySQL('prime_inventory')
    # Retrieve the location's products data based on the location's ID.
    products_query = """
        SELECT p.product_id, p.name, p.price,
            COALESCE(SUM(CASE WHEN m.to_location_id = %(location_id_from_URL)s THEN m.quantity END), 0) AS total_in_quantity,
            COALESCE(SUM(CASE WHEN m.from_location_id = %(location_id_from_URL)s THEN m.quantity END), 0) AS total_out_quantity,
            COALESCE(SUM(CASE WHEN m.to_location_id = %(location_id_from_URL)s THEN m.quantity END), 0) - COALESCE(SUM(CASE WHEN m.from_location_id = %(location_id_from_URL)s THEN m.quantity END), 0) AS total_quantity
        FROM products p
        LEFT JOIN movements m ON p.product_id = m.product_id
        WHERE m.to_location_id = %(location_id_from_URL)s OR m.from_location_id = %(location_id_from_URL)s
        GROUP BY p.product_id, p.name, p.price
        HAVING total_quantity > 0;
    """
    products = mysql.query_db(products_query, data)
    return render_template("locations/view_location.html", the_location=location, all_products=products)


# Render add_location_form page.
@app.route("/locations/add_new_location")
def render_add_location_form():
    return render_template("locations/add_location_form.html")


# Render update_location_form page.
@app.route("/locations/update_location/<location_id>")
def render_update_location_form(location_id):
    mysql = connectToMySQL('prime_inventory')
    # Retrieve the location data based on the location's ID.
    query = "SELECT * FROM locations WHERE location_id = %(location_id_from_URL)s"
    data = {'location_id_from_URL': location_id,}
    location = mysql.query_db(query, data)
    return render_template("locations/update_location_form.html", the_location=location)


# Adding new location to database.
@app.route("/locations/add_new_location", methods=["POST"])
def add_new_location():
    data, validation_errors = validate_add_new_location_method(request.form, request.files)

    # Passing the data from the form to the validation method to validate it first then return the valid values from it.
    if validation_errors:
        for error in validation_errors:
            flash(error)
        return redirect("/locations/add_new_location")

    mysql = connectToMySQL('prime_inventory')
    query = """
        INSERT INTO locations (location_id, name, image_data) 
        VALUES (
            %(location_id_from_form)s, 
            %(location_name_from_form)s, 
            %(location_image_from_form)s
        )
    """
    new_location = mysql.query_db(query, data)
    return redirect("/locations")


# Update location in the database.
@app.route("/locations/update_location", methods=["POST"])
def update_location():
    data, validation_errors = validate_update_location_method(request.form, request.files)

    # Passing the data from the form to the validation method to validate it first then return the valid values from it.
    if validation_errors:
        for error in validation_errors:
            flash(error)
        return redirect("/locations/update_location/" + str(data['old_location_id_from_form']))

    # Checking if the user changed the original ID of the location:
    # If they didn't change it:
    if data['location_id_from_form'] == data['old_location_id_from_form']:
        mysql = connectToMySQL('prime_inventory')
        update_location_query = """
            UPDATE locations 
            SET name = %(location_name_from_form)s, 
                image_data = %(location_image_from_form)s 
            WHERE location_id = %(old_location_id_from_form)s
        """
        update_location = mysql.query_db(update_location_query, data)

    # If the user changed it:
    else:
        mysql = connectToMySQL('prime_inventory')
        # Get the created_at value of the old location to assign it to the new location.
        get_created_at_query = """
            SELECT created_at
            FROM locations
            WHERE location_id = %(old_location_id_from_form)s
        """
        data['old_created_at'] = mysql.query_db(get_created_at_query, data)[0]['created_at']

        mysql = connectToMySQL('prime_inventory')
        # Create a new location with the inputted data.
        insert_location_query = """
            INSERT INTO locations (location_id, name, image_data, created_at)
            VALUES (
                %(location_id_from_form)s, 
                %(location_name_from_form)s, 
                %(location_image_from_form)s,
                %(old_created_at)s
            )
        """
        new_location = mysql.query_db(insert_location_query, data)

        mysql = connectToMySQL('prime_inventory')
        # Get the movements associated with the old location.
        movements_query = """
            SELECT movement_id
            FROM movements
            WHERE from_location_id = %(old_location_id_from_form)s 
            OR to_location_id = %(old_location_id_from_form)s
        """
        movements = mysql.query_db(movements_query, data)

        # Assign the movements to the new location after checking if there are movements assigned to it.
        if movements:
            for movement in movements:
                data['movement_id'] = movement['movement_id']
                mysql = connectToMySQL('prime_inventory')
                movement_update_query = """
                    UPDATE movements
                    SET from_location_id = CASE
                        WHEN from_location_id = %(old_location_id_from_form)s THEN %(location_id_from_form)s
                        ELSE from_location_id
                    END,
                    to_location_id = CASE
                        WHEN to_location_id = %(old_location_id_from_form)s THEN %(location_id_from_form)s
                        ELSE to_location_id
                    END
                    WHERE movement_id = %(movement_id)s
                """
                mysql.query_db(movement_update_query, data)

        mysql = connectToMySQL('prime_inventory')
        # Delete the old location
        delete_location_query = """
            DELETE FROM locations
            WHERE location_id = %(old_location_id_from_form)s
        """
        mysql.query_db(delete_location_query, data)

    return redirect("/locations")



# Delete a location.
@app.route("/locations/delete_location/<location_id>", methods=["POST"])
def delete_location(location_id):
    data = {'location_id_from_URL': location_id}

    mysql = connectToMySQL('prime_inventory')
    # Update the movements with the deleted location's ID in their "from_location_id".
    update_from_movements_query = """
        UPDATE movements
        SET from_location_id = NULL
        WHERE from_location_id = %(location_id_from_URL)s;
    """
    mysql.query_db(update_from_movements_query, data)

    # Update the movements with the deleted location's ID in their "to_location_id".
    mysql = connectToMySQL('prime_inventory')
    update_to_movements_query = """
        UPDATE movements
        SET to_location_id = NULL
        WHERE to_location_id = %(location_id_from_URL)s;
    """
    mysql.query_db(update_to_movements_query, data)

    # mysql = connectToMySQL('prime_inventory')
    # # Delete the corresponding movements involving the location
    # delete_corresponding_movements_query = "DELETE FROM movements WHERE from_location_id = %(location_id_from_URL)s OR to_location_id = %(location_id_from_URL)s"
    # mysql.query_db(delete_corresponding_movements_query, data)

    mysql = connectToMySQL('prime_inventory')
    # Delete the location from the 'locations' table.
    delete_location_query = """
        DELETE FROM locations 
        WHERE location_id = %(location_id_from_URL)s
    """
    mysql.query_db(delete_location_query, data)

    return redirect("/locations")




# //////////////////////////////////////////////  PRODUCTS ROUTES  //////////////////////////////////////////////
# ////////////////////////////////////////////// ↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓ //////////////////////////////////////////////




# Render all_products page.
@app.route("/products")
def render_all_products_page():
    mysql = connectToMySQL('prime_inventory')
    products = mysql.query_db("SELECT * FROM products")
    return render_template("products/all_products.html", all_products=products)


# Render view_product page.
@app.route("/products/view_product/<product_id>")
def render_view_product_page(product_id):
    mysql = connectToMySQL('prime_inventory')
    # Retrieve the product's data based on the product's ID.
    product_query = "SELECT * FROM products WHERE product_id = %(product_id_from_URL)s;"
    data = {'product_id_from_URL': product_id}
    product = mysql.query_db(product_query, data)
    
    mysql = connectToMySQL('prime_inventory')
    # Retrieve the product's locations data based on the product's ID.
    locations_query = """
        SELECT l.location_id, l.name AS location_name,
            COALESCE(SUM(CASE WHEN m.to_location_id = l.location_id THEN m.quantity END), 0) -
            COALESCE(SUM(CASE WHEN m.from_location_id = l.location_id THEN m.quantity END), 0) AS total_quantity
        FROM locations l
        JOIN movements m ON l.location_id = m.to_location_id OR l.location_id = m.from_location_id
        WHERE m.product_id = %(product_id_from_URL)s 
        GROUP BY l.location_id, l.name
        HAVING total_quantity > 0;;
    """
    locations = mysql.query_db(locations_query, data)
    return render_template("products/view_product.html", the_product=product, all_locations=locations)


# Render add_product_form page.
@app.route("/products/add_new_product/<location_id>")   #When reached from an add button in a specefic location view page.
@app.route("/products/add_new_product")                 #When reached from an add button in the "Products" page.                           
def render_add_product_form(location_id=None):          #Whether there is a parameter passed or not, it will work.
    mysql = connectToMySQL('prime_inventory')
    # Fetch all existing products from the database.
    products = mysql.query_db("SELECT * FROM products")

    mysql = connectToMySQL('prime_inventory')
    # Fetch all existing locations from the database.
    locations = mysql.query_db("SELECT * FROM locations")

    mysql = connectToMySQL('prime_inventory')
    # Fetch the specefic location name and ID, When reached from an add button in a specefic location view page.
    query = ("SELECT location_id, name AS Location_name FROM locations WHERE location_id = %(location_id_from_URL)s;")
    data = {'location_id_from_URL': location_id}
    location = mysql.query_db(query, data)
    return render_template("products/add_product_form.html", all_locations=locations, all_products = products, the_location = location)


# Render update_product_form page.
@app.route("/products/update_product/<product_id>")
def render_update_product_form(product_id):
    mysql = connectToMySQL('prime_inventory')
    # Retrieve the product data from the database.
    product_query = "SELECT * FROM products WHERE product_id = %(product_id_from_URL)s;"
    data = {'product_id_from_URL': product_id}
    product = mysql.query_db(product_query, data)
    return render_template("products/update_product_form.html", the_product=product,)


# Adding new product to database.
@app.route("/products/add_new_product", methods=["POST"])
def add_new_product():
    # Passing the data from the form to the validation method to validate it first then return the valid values from it.
    data, validation_errors, first_sec_validation = validate_add_new_product_method(request.form)

    if validation_errors:
        for error in validation_errors:
            flash(error)
        session['first_sec_validation'] = first_sec_validation
        return redirect("/products/add_new_product")

    # If the first checkbox is checked (add existing product).
    if 'new_product_checkbox' not in request.form:
        mysql = connectToMySQL('prime_inventory')
        # Add movement to the movements table with the product ID, location, and quantity.
        movement_query = """
            INSERT INTO movements (movement_id, product_id, quantity, from_location_id, to_location_id)
            VALUES (
                %(movement_id_1_from_form)s, 
                %(product_id_from_form)s, 
                %(product_quantity_1_from_form)s,
                NULL,
                %(product_location_id_1_from_form)s
                )
        """
        new_movement = mysql.query_db(movement_query, data)
        return redirect("/locations/view_location/" + str(data['product_location_id_1_from_form']))

    # If the second checkbox is checked (add new product).
    else:
        mysql = connectToMySQL('prime_inventory')
        # Insert a new product into the products table.
        product_query = """
            INSERT INTO products (product_id, name, price)
            VALUES (
                %(product_id_2_from_form)s, 
                %(product_name_2_from_form)s, 
                %(product_price_2_from_form)s
            )
        """
        new_product = mysql.query_db(product_query, data)
        mysql = connectToMySQL('prime_inventory')
        # Add movement to the movements table with the product ID, location, and quantity.
        movement_query = """
            INSERT INTO movements (movement_id, product_id, quantity, from_location_id, to_location_id)
            VALUES (
                %(movement_id_2_from_form)s, 
                %(product_id_2_from_form)s, 
                %(product_quantity_2_from_form)s,
                NULL,
                %(product_location_id_2_from_form)s
            )
        """
        new_movement = mysql.query_db(movement_query, data)
        return redirect("/locations/view_location/" + str(data['product_location_id_2_from_form']))

    return redirect("/products/add_new_product")


# Update product in the database.
@app.route("/products/update_product", methods=["POST"])
def update_product():
    # Passing the data from the form to the validation method to validate it first then return the valid values from it.
    data, validation_errors = validate_update_product_method(request.form)

    if validation_errors:
        for error in validation_errors:
            flash(error)
        return redirect("/products/update_product/" + str(data['old_product_id_from_form']))

    # Checking if the user changed the original ID of the product:
    # If they didn't change it:
    if data['product_id_from_form'] == data['old_product_id_from_form']:
        mysql = connectToMySQL('prime_inventory')
        update_product_query = """
            UPDATE products 
            SET name = %(product_name_from_form)s, 
                price = %(product_price_from_form)s 
            WHERE product_id = %(old_product_id_from_form)s
        """
        update_product = mysql.query_db(update_product_query, data)

    # If the user changed it:
    else:
        mysql = connectToMySQL('prime_inventory')
        # Get the created_at value of the old product to assign it to the new product.
        get_created_at_query = """
            SELECT created_at
            FROM products
            WHERE product_id = %(old_product_id_from_form)s
        """
        data['old_created_at'] = mysql.query_db(get_created_at_query, data)[0]['created_at']

        mysql = connectToMySQL('prime_inventory')
        # Create a new product with the inputted data.
        insert_product_query = """
            INSERT INTO products (product_id, name, price, created_at)
            VALUES (
                %(product_id_from_form)s, 
                %(product_name_from_form)s, 
                %(product_price_from_form)s,
                %(old_created_at)s)
        """
        new_product = mysql.query_db(insert_product_query, data)

        mysql = connectToMySQL('prime_inventory')
        # Get the movements associated with the old product.
        movements_query = """
            SELECT movement_id
            FROM movements
            WHERE product_id = %(old_product_id_from_form)s 
        """
        movements = mysql.query_db(movements_query, data)
        
        # Assign the movements to the new product after checking if there are movements assigned to it.
        if movements:
            for movement in movements:
                data['movement_id'] = movement['movement_id']
                mysql = connectToMySQL('prime_inventory')
                movement_update_query = """
                    UPDATE movements
                    SET product_id = %(product_id_from_form)s
                    WHERE movement_id = %(movement_id)s
                """
                mysql.query_db(movement_update_query, data)

        mysql = connectToMySQL('prime_inventory')
        # Delete the old product
        delete_product_query = """
            DELETE FROM products
            WHERE product_id = %(old_product_id_from_form)s
        """
        mysql.query_db(delete_product_query, data)

    return redirect("/products")



# Delete a product.
@app.route("/products/delete_product/<product_id>", methods=["POST"])
def delete_product(product_id):
    data = {'product_id_from_URL': product_id}

    mysql = connectToMySQL('prime_inventory')
    # Update the movements with the deleted product's ID in their "product_id".
    update_product_ID_in_movements_query = """
        UPDATE movements
        SET product_id = NULL
        WHERE product_id = %(product_id_from_URL)s;
    """
    mysql.query_db(update_product_ID_in_movements_query, data)

    mysql = connectToMySQL('prime_inventory')
    # Delete the product from the 'products' table.
    delete_product_query = """
        DELETE FROM products 
        WHERE product_id = %(product_id_from_URL)s
    """
    mysql.query_db(delete_product_query, data)
    url = request.referrer 
    
    return redirect(url)




# //////////////////////////////////////////////  MOVEMENTS ROUTES  //////////////////////////////////////////////
# ////////////////////////////////////////////// ↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓ //////////////////////////////////////////////




# Render all_movements page.
@app.route("/movements/<movement_type>/<sort_order>")
def render_all_movements_page(movement_type, sort_order):
    mysql = connectToMySQL('prime_inventory')
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
    return render_template("movements/all_movements.html", all_movements=movements)


# Proccessing filtering movements form on the movements page.
@app.route("/movements/filter_movements", methods=["POST"])
def filter_movements():
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
            return redirect("/movements/all/ASC")
    
    return redirect("/movements/{}/{}".format(movement_type, filter_sort))


# Render view_movement page.
@app.route("/movements/view_movement/<movement_id>")
def render_view_movement_page(movement_id):
    mysql = connectToMySQL('prime_inventory')
    # Retrieve the movement data based on the ID
    query = "SELECT * FROM movements WHERE movement_id = %(movement_id)s"
    data = {'movement_id': movement_id}
    movement = mysql.query_db(query, data)
    
    mysql = connectToMySQL('prime_inventory')
    # Retrieve other necessary data for the (from_location) of the movement.
    from_location_none = [{'name': "None"}]
    query1 = "SELECT * FROM locations WHERE location_id = %(from_location)s"
    data1 = {'from_location': movement[0]['from_location_id']}
    from_location = mysql.query_db(query1, data1)
    if not from_location:
        from_location = from_location_none
    
    mysql = connectToMySQL('prime_inventory')
    # Retrieve other necessary data for the (to_location) of the movement.
    to_location_none = [{'name': "None"}]
    query2 = "SELECT * FROM locations WHERE location_id = %(to_location)s"
    data2 = {'to_location': movement[0]['to_location_id']}
    to_location = mysql.query_db(query2, data2)
    if not to_location:
        to_location = to_location_none
    
    mysql = connectToMySQL('prime_inventory')
    # Retrieve other necessary data for the (product) of the movement.
    product_none = [{'name': "Product Deleted",'product_id': "Product Deleted"}]
    query3 = "SELECT * FROM products WHERE product_id = %(product_id)s"
    data3 = {'product_id': movement[0]['product_id']}
    product = mysql.query_db(query3, data3)
    if not product:
        product = product_none

    return render_template("movements/view_movement.html", the_movement=movement, the_from_location=from_location, the_to_location=to_location, the_product=product)


# Render add_movement_form page.
@app.route("/movements/add_new_movement")
def render_add_movement_form():
    mysql = connectToMySQL('prime_inventory')
    locations = mysql.query_db("SELECT location_id, name FROM locations;")
    return render_template("movements/add_movement_form.html", locations=locations)


# Render update_movement_form page.
@app.route("/movements/update_movement/<movement_id>")
def render_update_movement_form(movement_id):
    mysql = connectToMySQL('prime_inventory')
    # Retrieve the movement data based on the ID
    movement_query = "SELECT * FROM movements WHERE movement_id = %(movement_id_from_URL)s"
    data = {'movement_id_from_URL': movement_id}
    movement = mysql.query_db(movement_query, data)
    
    mysql = connectToMySQL('prime_inventory')
    # Retrieve other necessary data for the locations.
    locations = mysql.query_db("SELECT location_id, name FROM locations")
    
    mysql = connectToMySQL('prime_inventory')
    # Retrieve other necessary data for the product of the movement.
    product_query = """
        SELECT product_id, name AS product_name 
        FROM products WHERE product_id= %(product_id)s
    """
    data ['product_id']= movement[0]['product_id']
    product = mysql.query_db(product_query, data)

    return render_template("movements/update_movement_form.html", the_movement=movement, all_locations=locations, the_product=product)


#  AJAX request to retrieve the corresponding based on the selected From Location in the add_movement_form.
# Get products based on location ID.
@app.route("/products/get_products_by_location/<location_id>")
def get_products_by_location(location_id):
    mysql = connectToMySQL('prime_inventory')
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


# AJAX request to retrieve all products
@app.route("/products/get_all_products")
def get_all_products():
    mysql = connectToMySQL('prime_inventory')
    query = "SELECT product_id, name FROM products"
    products = mysql.query_db(query)
    return jsonify(products)


# Adding new movement to database.
@app.route("/movements/add_new_movement", methods=["POST"])
def add_new_movement():
    data, validation_errors = validate_add_new_movement_method(request.form)

    if validation_errors:
        for error in validation_errors:
            flash(error)
        return redirect("/movements/add_new_movement")

    mysql = connectToMySQL('prime_inventory')
    # Add movement to the movements table with the product ID, location, and quantity.
    movement_query = """
        INSERT INTO movements (movement_id, product_id, quantity, from_location_id, to_location_id)
        VALUES (
            %(movement_id_from_form)s, 
            %(product_id_from_form)s, 
            %(movement_quantity_from_form)s,
            NULLIF(%(from_location_id_from_form)s, 'NULL'),
            NULLIF(%(to_location_id_from_form)s, 'NULL')
            )
    """
    new_movement = mysql.query_db(movement_query, data)
    return redirect("/movements/all/DESC")


# Update movement in the databse.
@app.route("/movements/update_movement", methods=["POST"])
def update_movement():
    # Passing the data from the form to the validation method to validate it first then return the valid values from it.
    data, validation_errors = validate_update_movement_method(request.form)

    if validation_errors:
        for error in validation_errors:
            flash(error)
        return redirect("/movements/update_movement/" + str(data['old_movement_id_from_form']))

    mysql = connectToMySQL('prime_inventory')
    query = """
        UPDATE movements 
        SET movement_id = %(movement_id_from_form)s, 
            product_id = %(product_id_from_form)s, 
            quantity = %(movement_quantity_from_form)s, 
            from_location_id = NULLIF(%(from_location_id_from_form)s, 'NULL'),
            to_location_id = NULLIF(%(to_location_id_from_form)s, 'NULL') 
        WHERE movement_id = %(old_movement_id_from_form)s
    """
    updated_movement = mysql.query_db(query, data)
    return redirect("/movements/all/ASC")


# Delete a movement.
@app.route("/movements/delete_movement/<movement_id>", methods=["POST"])
def delete_movement(movement_id):
    mysql = connectToMySQL('prime_inventory')
    # Delete the movement from the 'movements' table
    query = "DELETE FROM movements WHERE movement_id = %(movement_id_from_URL)s"
    data = {'movement_id_from_URL': movement_id}
    mysql.query_db(query, data)
    url = request.referrer 
    
    return redirect(url)




# ////////////////////////////////////////////////////////////////////////////////////////////////////////////////




if __name__=="__main__":   # Ensure this file is being run directly and not from a different module    
    app.run(debug=True)    # Run the app in debug mode.