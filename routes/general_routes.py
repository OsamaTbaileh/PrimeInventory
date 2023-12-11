from flask import Flask, render_template, redirect, Blueprint
from mysqlconnection import connectToMySQL   # import the function that will return an instance of a connection
from routes.user_routes import check_user_id  # Import the check_user_id function from user_routes.py
from validations.validations import *

# app = Flask(__name__, static_folder='../static', template_folder='../templates')
# app.secret_key = 'your_secret_key_here'


app = Blueprint('general', __name__)


# Render the home page.
@app.route("/")
def render_home_page():
    checked_user = check_user_id()
    if checked_user:
        return render_template("users/dashboard.html", checked_user=checked_user)
    return render_template("general/home_page.html", checked_user=checked_user)


# Render the normal_report_page.
@app.route("/normal_report")
def render_report_page():
    checked_user = check_user_id()
    if checked_user:
        mysql = connectToMySQL('primeinventory$prime_inventory')
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
        return render_template("general/normal_report_page.html", all_products=products, checked_user=checked_user)
    return redirect("/sign_out")


# Render the advanced_report_page.
@app.route("/advanced_report")
def display_table():
    checked_user = check_user_id()
    if checked_user:
        mysql = connectToMySQL('primeinventory$prime_inventory')
        query = "SELECT DISTINCT product_id, name FROM products ORDER BY LOWER(name);"
        products = mysql.query_db(query)

        mysql = connectToMySQL('primeinventory$prime_inventory')
        query = "SELECT DISTINCT location_id, name FROM locations ORDER BY LOWER(name);"
        locations = mysql.query_db(query)

        mysql = connectToMySQL('primeinventory$prime_inventory')
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

        return render_template('general/advanced_report_page.html', products=products, locations=locations, quantity_dict=quantity_dict, checked_user=checked_user)
    return redirect("/sign_out")



# # Render the photos from the server using their URLs.
# @app.route('/static/uploads/<directory>/<filename>')
# def get_user_image(directory, filename):
#     return send_from_directory('static/uploads', f'{directory}/{filename}')