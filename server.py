from flask import Flask, render_template, redirect, request, session, flash, jsonify
import base64
from datetime import datetime, timedelta
from mysqlconnection import connectToMySQL   # import the function that will return an instance of a connection
app = Flask(__name__, static_folder='static')


# Render the home page.
@app.route("/")
def index():
    return render_template("index.html")


# Render the locations page.
@app.route("/locations")
def show_locations():
    mysql = connectToMySQL('stores')
    locations = mysql.query_db("SELECT * FROM locations;")
    # for location in locations:
    #     image_data = location['image']
    #     if image_data is not None:
    #         location['image'] = base64.b64encode(image_data).decode('utf-8')
    return render_template("locations.html", all_locations=locations)


# Render the All-Products page.
@app.route("/products")
def show_all_products():
    mysql = connectToMySQL('stores')
    products = mysql.query_db("""
        SELECT  products.product_id,
                products.name AS product_name,
                products.price,
                locations.location_id,
                locations.name AS location_name,
                products_has_locations.product_quantity
        FROM products
        JOIN products_has_locations ON products.product_id = products_has_locations.product_id
        JOIN locations ON products_has_locations.location_id = locations.location_id;
    """)
    return render_template("products.html", all_products=products)



# Render each location products list.
# @app.route("/locations/<location_id>")
# def show_location_products(location_id):
#     data = {"location_id": location_id}
    
#     mysql = connectToMySQL('stores')
#     query1 = """
#         SELECT products.product_id, products.name, products.price, products_has_locations.product_quantity 
#         FROM products 
#         JOIN products_has_locations ON products.product_id = products_has_locations.product_id 
#         WHERE products_has_locations.location_id = %(location_id)s;
#     """
#     products = mysql.query_db(query1, data)
    
#     mysql = connectToMySQL('stores')
#     query2 = "SELECT * FROM locations WHERE location_id = %(location_id)s;"
#     location = mysql.query_db(query2, data)
#     return render_template("products.html", all_products=products, the_location=location)


# Render the All-Movements page.
@app.route("/movements/<movement_type>/<sort_order>")
def show_movements(movement_type, sort_order):
    mysql = connectToMySQL('stores')
    if movement_type == "all":
        query = """
            SELECT movements.movement_id, products.name, movements.quantity, movements.created_at, 
            from_location.name AS from_location_name, to_location.name AS to_location_name 
            FROM movements 
            JOIN products ON movements.product_id = products.product_id 
            JOIN locations AS from_location ON movements.from_location_id = from_location.location_id 
            JOIN locations AS to_location ON movements.to_location_id = to_location.location_id
            ORDER BY movements.updated_at {} ;
        """.format(sort_order)
        movements = mysql.query_db(query)
    else:
        num_days = int(movement_type)
        today = datetime.now().date()
        start_date = today - timedelta(days=num_days)
        query = """
            SELECT movements.movement_id, products.name, movements.quantity, movements.created_at, 
            from_location.name AS from_location_name, to_location.name AS to_location_name 
            FROM movements 
            JOIN products ON movements.product_id = products.product_id 
            JOIN locations AS from_location ON movements.from_location_id = from_location.location_id 
            JOIN locations AS to_location ON movements.to_location_id = to_location.location_id
            WHERE movements.created_at >= %(start_date)s
            ORDER BY movements.updated_at {} ;
        """.format(sort_order)
        data = {"start_date": start_date}
        movements = mysql.query_db(query, data)
        
    return render_template("movements.html", all_movements=movements)


# Render the add_movement_form.html page.
@app.route("/movements/add_new_movement")
def render_add_new_movement():
    mysql = connectToMySQL('stores')
    locations = mysql.query_db("SELECT location_id, name FROM locations;")
    return render_template("add_movement_form.html", locations=locations)


#  AJAX request to retrieve the corresponding based on the selected From Location in the add_movement_form.
# Get products based on location ID.
@app.route("/products/get_products_by_location/<location_id>")
def get_products_by_location(location_id):
    mysql = connectToMySQL('stores')
    query = """
        SELECT products.product_id, products.name, products_has_locations.product_quantity 
        FROM products 
        JOIN products_has_locations ON products.product_id = products_has_locations.product_id 
        WHERE products_has_locations.location_id = %(location_id)s;
    """
    data = {'location_id': location_id}
    products = mysql.query_db(query, data)
    return jsonify(products)


# Adding new movement or update existing one to the database.
@app.route("/movements/add_or_update_movement", methods=["POST"])
def add_or_update_movement_to_db():
    mysql = connectToMySQL('stores')
    
    product_id_from_select = request.form['product_id_from_select']
    product_id_from_text = request.form['product_id_from_text']
    if product_id_from_select:
        product_id_from_form = product_id_from_select
    else:
        product_id_from_form = product_id_from_text
    
    # Check if the movement ID exists in the form data to determine if it's an update or insert
    if 'adding' not in request.form:
        # Update existing movement
        query = """
            UPDATE movements 
            SET movement_id = %(new_movement_id)s, 
                product_id = %(product_id_from_form)s, 
                quantity = %(movement_quantity_from_form)s, 
                from_location_id = %(from_location_id_from_form)s, 
                to_location_id = %(to_location_id_from_form)s 
            WHERE movement_id = %(old_movement_id)s
        """
    else:
        # Add new movement
        query = """
            INSERT INTO movements (movement_id, product_id, quantity, from_location_id, to_location_id) 
            VALUES (%(new_movement_id)s, %(product_id_from_form)s, %(movement_quantity_from_form)s, 
            %(from_location_id_from_form)s, %(to_location_id_from_form)s)
        """
    
    data = {
        'new_movement_id': request.form['movement_id'],
        'old_movement_id': request.form['old_movement_id'],
        'product_id_from_form': product_id_from_form,
        'movement_quantity_from_form': request.form['movement_quantity'],
        'from_location_id_from_form': request.form['from_location_id'],
        'to_location_id_from_form': request.form['to_location_id'],
    }
    new_or_updated_movement = mysql.query_db(query, data)
    return redirect("/movements/all/ASC")




# Render the edit_movement_form.html page.
@app.route("/movements/edit_movement/<movement_id>")
def render_edit_movement(movement_id):
    mysql = connectToMySQL('stores')
    # Retrieve the movement data based on the ID
    query = "SELECT * FROM movements WHERE movement_id = %(movement_id)s"
    data = {'movement_id': movement_id,}
    movement = mysql.query_db(query, data)
    
    mysql = connectToMySQL('stores')
    # Retrieve other necessary data for populating select inputs
    locations = mysql.query_db("SELECT location_id, name FROM locations")
    
    mysql = connectToMySQL('stores')
    # Retrieve other necessary data for populating select inputs
    query2 = ("SELECT * FROM products WHERE product_id= %(product_id)s")
    data2 = {'product_id': movement[0]['product_id']}
    product = mysql.query_db(query2, data2)
    return render_template("edit_movement_form.html", movement=movement, locations=locations, the_product=product)


# Render the view_movement_form.html page.
@app.route("/movements/view_movement/<movement_id>")
def render_view_movement(movement_id):
    mysql = connectToMySQL('stores')
    # Retrieve the movement data based on the ID
    query = "SELECT * FROM movements WHERE movement_id = %(movement_id)s"
    data = {'movement_id': movement_id}
    movement = mysql.query_db(query, data)
    
    mysql = connectToMySQL('stores')
    # Retrieve other necessary data for populating select inputs
    query1 = "SELECT * FROM locations WHERE location_id = %(from_location)s"
    data1 = {'from_location': movement[0]['from_location_id']}
    from_location = mysql.query_db(query1, data1)
    
    mysql = connectToMySQL('stores')
    # Retrieve other necessary data for populating select inputs
    query2 = "SELECT * FROM locations WHERE location_id = %(to_location)s"
    data2 = {'to_location': movement[0]['to_location_id']}
    to_location = mysql.query_db(query2, data2)
    
    mysql = connectToMySQL('stores')
    # Retrieve other necessary data for populating select inputs
    query3 = "SELECT * FROM products WHERE product_id = %(product_id)s"
    data3 = {'product_id': movement[0]['product_id']}
    product = mysql.query_db(query3, data3)
    
    return render_template("view_movement.html", the_movement=movement, the_from_location=from_location, the_to_location=to_location, the_product=product)

# Render the add_location_form.html page.
@app.route("/locations/add_new_location")
def render_add_new_location():
    return render_template("add_location_form.html")


# Adding new location to database.
@app.route("/locations/add_new_location", methods=["POST"])
def add_new_location_to_db():
    mysql = connectToMySQL('stores')
    
    image_file = request.files['location_image']
    image_data = base64.b64encode(image_file.read()).decode('utf-8')
    query = "INSERT INTO locations (location_id, name, image_data) VALUES (%(id_from_form)s, %(name_from_form)s, %(image_from_form)s)"
    data = {
        'id_from_form': request.form['location_id'],
        'name_from_form': request.form['location_name'],
        'image_from_form': image_data
    }
    new_location = mysql.query_db(query, data)
    return redirect("/locations")

# Update location to the database.
@app.route("/locations/update_location", methods=["POST"])
def update_location_to_db():
    mysql = connectToMySQL('stores')
    image_file = request.files['location_image']
    if image_file:
        image_data = base64.b64encode(image_file.read()).decode('utf-8')
    else:
        image_data = request.form['old_image']
    query = """
        UPDATE locations 
        SET location_id = %(update_location_id)s, 
            name = %(update_location_name)s, 
            image_data = %(update_location_image)s 
        WHERE location_id = %(old_location_id)s
    """
    
    data = {
        'update_location_id': request.form['location_id'],
        'old_location_id': request.form['old_location_id'],
        'update_location_name': request.form['location_name'],
        'update_location_image': image_data,
    }
    
    updated_location = mysql.query_db(query, data)
    return redirect("/locations")

# Render the add_product_form.html page.
@app.route("/products/add_new_product/<location_id>")   #When reached from an add button in a specefic location view oage.
@app.route("/products/add_new_product")                 #When reached from an add button in the "Products" page.                           
def render_add_new_product(location_id=None):           #Whether there is a parameter passed or not, it will work.
    mysql = connectToMySQL('stores')
    locations = mysql.query_db("SELECT location_id, name FROM locations;")

    return render_template("add_product_form.html", all_locations=locations,the_location_id = location_id)

# Adding new product to database.
@app.route("/products/add_new_product", methods=["POST"])
def add_new_product_to_db():
    mysql = connectToMySQL('stores')
    # Insert the new product into the `products` table
    product_query = "INSERT INTO products (product_id, name, price) VALUES (%(id_from_form)s, %(name_from_form)s, %(price_from_form)s)"
    product_data = {
        'id_from_form': request.form['product_id'],
        'name_from_form': request.form['product_name'],
        'price_from_form': request.form['product_price']
    }
    mysql.query_db(product_query, product_data)
    
    mysql = connectToMySQL('stores')
    # Insert the product and its quantity into the `products_has_locations` table
    location_query = "INSERT INTO products_has_locations (product_id, location_id, product_quantity) VALUES (%(id_from_form)s, %(location_from_form)s, %(quantity_from_form)s)"
    location_data = {
        'id_from_form': request.form['product_id'],
        'location_from_form': request.form['location_id'],
        'quantity_from_form': request.form['product_quantity']
    }
    mysql.query_db(location_query, location_data)

    return redirect("/locations/view_location/" + str(location_data['location_from_form']))


# Render the edit_location_form.html page.
@app.route("/locations/edit_location/<location_id>")
def render_edit_location(location_id):
    mysql = connectToMySQL('stores')
    # Retrieve the location data based on the ID
    query = "SELECT * FROM locations WHERE location_id = %(location_id)s"
    data = {'location_id': location_id,}
    location = mysql.query_db(query, data)
    
    return render_template("edit_location_form.html", the_location=location)


# Render the view_location_form.html page.
@app.route("/locations/view_location/<location_id>")
def render_view_locaiton(location_id):
    mysql = connectToMySQL('stores')
    # Retrieve the location data based on the ID
    location_query = "SELECT * FROM locations WHERE location_id = %(location_id)s"
    data = {'location_id': location_id}
    location = mysql.query_db(location_query, data)
    
    mysql = connectToMySQL('stores')
    products_query = """
        SELECT p.product_id, p.name AS product_name, p.price, pl.product_quantity
        FROM products p
        JOIN products_has_locations pl ON p.product_id = pl.product_id
        WHERE pl.location_id = %(location_id)s
    """
    products = mysql.query_db(products_query, data)
    print(products)
    return render_template("view_location.html", the_location=location, all_products=products)


# Render the view_product_form.html page.
@app.route("/products/view_product/<product_id>/<location_id>")
def render_view_product(product_id, location_id):
    mysql = connectToMySQL('stores')
    # Retrieve the product data including the quantity from(products_has_locations table) and with the location data.
    query = """
        SELECT p.product_id, p.name AS product_name, p.price, l.location_id, l.name AS location_name, phl.product_quantity
        FROM products p
        INNER JOIN products_has_locations phl ON p.product_id = phl.product_id
        INNER JOIN locations l ON phl.location_id = l.location_id
        WHERE p.product_id = %(product_id)s AND l.location_id = %(location_id)s;
    """
    data = {
        'product_id': product_id,
        'location_id': location_id
    }
    product = mysql.query_db(query, data)
    return render_template("view_product.html", the_product=product)

# Render the edit_product_form.html page.
@app.route("/products/edit_product/<product_id>/<location_id>")
def render_edit_product(product_id, location_id):
    mysql = connectToMySQL('stores')
    # Retrieve the product data including the quantity
    product_query = """
        SELECT p.product_id, p.name, p.price, pl.product_quantity
        FROM products p
        LEFT JOIN products_has_locations pl ON p.product_id = pl.product_id
        WHERE p.product_id = %(product_id)s
    """
    data = {'product_id': product_id}
    product = mysql.query_db(product_query, data)

    mysql = connectToMySQL('stores')
    # Retrieve other necessary data for populating select inputs
    location_query = "SELECT location_id, name FROM locations WHERE location_id = %(location_id)s"
    location_data = {'location_id': location_id}
    the_location = mysql.query_db(location_query, location_data)

    mysql = connectToMySQL('stores')
    # Retrieve other necessary data for populating select inputs
    locations = mysql.query_db("SELECT location_id, name FROM locations;")
    return render_template("edit_product_form.html", the_product=product, all_locations=locations, the_location=the_location)


# Update product to the database.
@app.route("/products/update_product", methods=["POST"])
def update_product_to_db():
    data = {
        'update_product_id': request.form['product_id'],
        'update_product_name': request.form['product_name'],
        'update_product_price': request.form['product_price'],
        'update_product_quantity': request.form['product_quantity'],
        'update_product_location_id': request.form['product_location_id'],
        'old_product_id': request.form['old_product_id'],
        'old_location_id': request.form['old_location_id']
    }

    mysql = connectToMySQL('stores')
    product_query = """
        UPDATE products 
        SET product_id = %(update_product_id)s, 
            name = %(update_product_name)s, 
            price = %(update_product_price)s
        WHERE product_id = %(old_product_id)s
    """
    mysql.query_db(product_query, data)

    mysql = connectToMySQL('stores')
    product_location_query = """
        UPDATE products_has_locations
        SET product_quantity = %(update_product_quantity)s,
            location_id = %(update_product_location_id)s
        WHERE product_id = %(update_product_id)s
        AND location_id = %(old_location_id)s
    """
    mysql.query_db(product_location_query, data)

    return redirect("/locations/view_location/" + str(data['old_location_id']))




# Delete a location.
@app.route("/locations/delete_location/<location_id>", methods=["POST"])
def delete_location(location_id):    
    # Delete the location from the 'locations' table
    mysql = connectToMySQL('stores')
    query = "DELETE FROM locations WHERE location_id = %(location_id)s"
    data = {'location_id': location_id}
    mysql.query_db(query, data)
    
    # Delete the corresponding entries from the 'products_has_locations' table
    mysql = connectToMySQL('stores')
    query = "DELETE FROM products_has_locations WHERE location_id = %(location_id)s"
    mysql.query_db(query, data)
    
    # Delete the corresponding movements involving the location
    mysql = connectToMySQL('stores')
    query = "DELETE FROM movements WHERE from_location_id = %(location_id)s OR to_location_id = %(location_id)s"
    mysql.query_db(query, data)
    
    return redirect("/locations")


# Delete a movement.
@app.route("/movements/delete_movement/<movement_id>", methods=["POST"])
def delete_movement(movement_id):
    mysql = connectToMySQL('stores')
    
    # Delete the movement from the 'movements' table
    query = "DELETE FROM movements WHERE movement_id = %(movement_id)s"
    data = {'movement_id': movement_id}
    mysql.query_db(query, data)
    
    return redirect("/movements/all/ASC")


# Delete a product.
@app.route("/products/delete_product/<product_id>", methods=["POST"])
def delete_product(product_id):
    mysql = connectToMySQL('stores')
    # Delete the product from the 'products' table
    query = "DELETE FROM products WHERE product_id = %(product_id)s"
    data = {'product_id': product_id}
    mysql.query_db(query, data)
    
    mysql = connectToMySQL('stores')
    # Delete the corresponding entries from the 'products_has_locations' table
    query = "DELETE FROM products_has_locations WHERE product_id = %(product_id)s"
    mysql.query_db(query, data)

    mysql = connectToMySQL('stores')
    # Delete the corresponding movements involving the product
    query = "DELETE FROM movements WHERE product_id = %(product_id)s"
    mysql.query_db(query, data)
    
    # Retrieve the referrer URL ( let u rediret to the page from where you press the delete button).
    referrer = request.referrer
    
    # Redirect back to the referrer URL
    return redirect(referrer)








if __name__=="__main__":   # Ensure this file is being run directly and not from a different module    
    app.run(debug=True)    # Run the app in debug mode.