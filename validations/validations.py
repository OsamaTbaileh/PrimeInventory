import os, re, uuid
from flask import session
from werkzeug.utils import secure_filename
from flask_bcrypt import Bcrypt
from mysqlconnection import connectToMySQL   # import the function that will return an instance of a connection



# //////////////////////////////////////////////  Locations Validations  //////////////////////////////////////////////
# ///////////////////////////////////////////////// ↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓ ////////////////////////////////////////////////



# Validations for the add_new_location method.
def validate_add_new_location_method(form_data, form_files):
    validation_errors = []
    data = {
        'location_id_from_form': form_data['location_id'],
        'location_name_from_form': form_data['location_name'],
        'creation_user_id': form_data['user_id']
    }

    # Validate location_id length.
    if len(data['location_id_from_form']) < 5 or len(data['location_id_from_form']) > 20:
        validation_errors.append("Location ID must be between 5 and 20 characters in length.")
    else:
        # Check if location_id already exists in the database.
        mysql = connectToMySQL('primeinventory$prime_inventory')
        query = "SELECT COUNT(*) AS count FROM locations WHERE location_id = %(location_id_from_form)s"
        result = mysql.query_db(query, data)
        if result[0]['count'] > 0:
            validation_errors.append("A location with the same ID already exists.")

    # Validate location's name length.
    if len(data['location_name_from_form']) < 5 or len(data['location_name_from_form']) > 20:
        validation_errors.append("Location name must be between 5 and 20 characters in length.")
    else:
        # Check if location's name already exists in the database.
        mysql = connectToMySQL('primeinventory$prime_inventory')
        query = "SELECT COUNT(*) AS count FROM locations WHERE name = %(location_name_from_form)s"
        result = mysql.query_db(query, data)
        if result[0]['count'] > 0:
            validation_errors.append("A location with the same name already exists.")

    # Validate location's image:
    # If the user decided to uplaod a photo file:
    file = None
    if "location_image" in form_files:
        file = form_files['location_image']
        if file.filename != '':
            # Check the type of the photo file.
            ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}
            # file = request.files['location_image']
            if '.' not in file.filename or file.filename.rsplit('.', 1)[1].lower() not in ALLOWED_EXTENSIONS:
                validation_errors.append("The file must be a photo type.")
            else:
                # Get the current file's directory.
                current_directory = os.path.dirname(__file__)
                # Define the relative path to the target directory (one level up).
                relative_path = '../static/uploads/locations_photos'
                # Construct the complete path to save the image.
                image_path = os.path.join(current_directory, relative_path)
                # Process the uploaded image.
                file = form_files['location_image']
                original_filename = secure_filename(file.filename)
                # Generate a unique filename (image_id) using UUID.
                image_id = f"{uuid.uuid4()}_{original_filename}"
                # Append the image_id to the path.
                image_path = os.path.join(image_path, image_id)
                # Save the file.
                file.save(image_path)
    
    # Validate location's image:
    if 'location_image' not in form_files or file.filename == '':  
        image_id = "default_location.png"

    data['location_image_from_form'] = image_id
    return data, validation_errors



# Validations for the update_location method.
def validate_update_location_method(form_data, form_files):
    validation_errors = []
    data = {
        'location_id_from_form': form_data['location_id'],
        'old_location_id_from_form': form_data['old_location_id'],
        'location_name_from_form': form_data['location_name'],
        'old_location_name_from_form': form_data['old_location_name'],
        'updation_user_id': form_data['user_id'],
        'old_image_from_form': form_data['old_image']
    }

    # Validate location_id length.
    if len(data['location_id_from_form']) < 5 or len(data['location_id_from_form']) > 20:
        validation_errors.append("Location ID must be between 5 and 20 characters in length.")
    else:
        # Check if location_id already exists in the database.
        mysql = connectToMySQL('primeinventory$prime_inventory')
        query = "SELECT COUNT(*) AS count FROM locations WHERE location_id = %(location_id_from_form)s"
        result = mysql.query_db(query, data)
        if result[0]['count'] > 0 and data['location_id_from_form'] != data['old_location_id_from_form']:
            validation_errors.append("A location with the same ID already exists.")

    # Validate location's name length.
    if len(data['location_name_from_form']) < 5 or len(data['location_name_from_form']) > 20:
        validation_errors.append("Location name must be between 5 and 20 characters in length.")
    else:
        # Check if location's name already exists in the database.
        mysql = connectToMySQL('primeinventory$prime_inventory')
        query = "SELECT COUNT(*) AS count FROM locations WHERE name = %(location_name_from_form)s"
        result = mysql.query_db(query, data)
        if result[0]['count'] > 0 and data['location_name_from_form'] != data['old_location_name_from_form']:
            validation_errors.append("A location with the same name already exists.")

    # Validate location's image:
    # If the user decided to uplaod a new photo file:
    file = None
    if "location_image" in form_files:
        file = form_files['location_image']
        if file.filename != '':
            # Check the type of the photo file.
            ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}
            # file = request.files['location_image']
            if '.' not in file.filename or file.filename.rsplit('.', 1)[1].lower() not in ALLOWED_EXTENSIONS:
                validation_errors.append("The file must be a photo type.")
            else:
                # Get the current file's directory.
                current_directory = os.path.dirname(__file__)
                # Define the relative path to the target directory (one level up).
                relative_path = '../static/uploads/locations_photos'

                # Construct the path to the old image to replace it with the new one.
                # (You can remove the next 5 lines if u want to keep the old image along with the new one)
                old_image_path = os.path.join(current_directory, relative_path, form_data['old_image'])
                # Check if the old image file exists and it's not the default image before trying to delete it
                if os.path.exists(old_image_path) and form_data['old_image'] != 'default_location.png':
                    # Delete the old image file
                    os.remove(old_image_path)

                # Construct the complete path to save the image.
                image_path = os.path.join(current_directory, relative_path)
                # Process the uploaded image.
                file = form_files['location_image']
                original_filename = secure_filename(file.filename)
                # Generate a unique filename (image_id) using UUID.
                image_id = f"{uuid.uuid4()}_{original_filename}"
                # Append the image_id to the path.
                image_path = os.path.join(image_path, image_id)
                # Save the file.
                file.save(image_path)

    # Validate location's image if the user didnt update it, then use the old one:
    if 'location_image' not in form_files or file.filename == '':
        image_id =  data['old_image_from_form']

    data['location_image_from_form'] = image_id
    return data, validation_errors




# //////////////////////////////////////////////  Products Validations  //////////////////////////////////////////////
# //////////////////////////////////////////////// ↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓ ////////////////////////////////////////////////




# Validations for the add_new_product method.
def validate_add_new_product_method(form_data):
    validation_errors = []
    first_sec_validation = None

    # If the first checkbox is checked (add existing product).
    if 'new_product_checkbox' not in form_data:
        first_sec_validation = True
        data = {
            'product_quantity_1_from_form' : form_data['product_quantity_1'],
            'movement_id_1_from_form' : form_data['movement_id_1'],
            'creation_user_id': form_data['user_id']
        }

        # Validate product_id when the user doesn't select any neither from the select menu nor typing down an ID in the text input.
        if 'product_id_select_1' in form_data and 'product_id_input_1' in form_data:
            validation_errors.append("You must choose a product either from the select menu or type its ID directly in the text area.")
        # If the user entered a product_id manually in the text input.
        elif 'product_id_input_1' in form_data:
            data['product_id_from_form'] = form_data['product_id_input_1']
            # Check if product_id exists in the database.
            mysql = connectToMySQL('primeinventory$prime_inventory')
            query = "SELECT COUNT(*) AS count FROM products WHERE  product_id = %(product_id_from_form)s" 
            result = mysql.query_db(query, data)
            # If entered product_id didn't match any product ID in the database.
            if result[0]['count'] == 0:
                validation_errors.append("No product ID matched the entered one, please try again with valid ID.")
        # If the user chosed a product_id from the select menu.
        elif 'product_id_select_1' in form_data:
            data['product_id_from_form'] = form_data['product_id_select_1']

        # Validate the quantity of the product if the user left it blank or not.
        if data['product_quantity_1_from_form'] == "":
            validation_errors.append("Please insert a number in the quantity area.")
        else:
            movement_quantity = float(data['product_quantity_1_from_form'])
            # Validate the quantity if it's less than or equal to zero or has decimal values.
            if movement_quantity <= 0 or not movement_quantity.is_integer():
                validation_errors.append("Please insert a positive integer number as the quantity.")

        # Validate movement_id length.
        if len(data['movement_id_1_from_form']) < 5 or len(data['movement_id_1_from_form']) > 20:
            validation_errors.append("Movement ID must be between 5 and 20 characters in length.")
        else:
            # Check if movement_id already exists in the database.
            mysql = connectToMySQL('primeinventory$prime_inventory')
            query = "SELECT COUNT(*) AS count FROM movements WHERE movement_id = %(movement_id_1_from_form)s"
            result = mysql.query_db(query, data)
            if result[0]['count'] > 0:
                validation_errors.append("A movement with the same ID already exists.")

        # Validate from_location_id is present and selected by the user.
        if 'product_location_id_1' not in form_data or form_data['product_location_id_1'] == "":
            validation_errors.append("You must select a Location.")
        else:
            data["product_to_location_id_1_from_form"] = form_data['product_location_id_1']

    # If the second checkbox is checked (add new product).
    else:
        first_sec_validation = False
        data = {
            'product_id_2_from_form' : form_data['product_id_2'],
            'product_name_2_from_form' : form_data['product_name_2'],
            'product_price_2_from_form' : form_data['product_price_2'],
            'product_quantity_2_from_form' : form_data['product_quantity_2'],
            'movement_id_2_from_form' : form_data['movement_id_2'],
            'creation_user_id': form_data['user_id']
        }

        # Validate product_id length.
        if len(data['product_id_2_from_form']) < 5 or len(data['product_id_2_from_form']) > 20:
            validation_errors.append("Product ID must be between 5 and 20 characters in length.")
        else:
            # Check if product_id already exists in the database.
            mysql = connectToMySQL('primeinventory$prime_inventory')
            query = "SELECT COUNT(*) AS count FROM products WHERE product_id = %(product_id_2_from_form)s"
            result = mysql.query_db(query, data)
            if result[0]['count'] > 0:
                validation_errors.append("A product with the same ID already exists.")
        
        # Validate product's name length.
        if len(data['product_name_2_from_form']) < 3 or len(data['product_name_2_from_form']) > 20:
            validation_errors.append("Product name must be between 3 and 20 characters in length.")
        else:
            # Check if product's name already exists in the database.
            mysql = connectToMySQL('primeinventory$prime_inventory')
            query = "SELECT COUNT(*) AS count FROM products WHERE  name = %(product_name_2_from_form)s"
            result = mysql.query_db(query, data)
            if result[0]['count'] > 0:
                validation_errors.append("A product with the same name already exists.")

        # Validate product's price.'
        if data['product_price_2_from_form'] == "":
            validation_errors.append("Please insert a price for the product.")
        elif float(data['product_price_2_from_form']) <= 0:
            validation_errors.append("Please insert a positive number as a price.")

        # Validate the quantity of the product if the user left it blank or not.
        if data['product_quantity_2_from_form'] == "":
            validation_errors.append("Please insert a number in the quantity area.")
        else:
            movement_quantity = float(data['product_quantity_2_from_form'])
            # Validate the quantity if it's less than or equal to zero or has decimal values.
            if movement_quantity <= 0 or not movement_quantity.is_integer():
                validation_errors.append("Please insert a positive integer number as the quantity.")

        # Validate movement_id length.
        if len(data['movement_id_2_from_form']) < 5 or len(data['movement_id_2_from_form']) > 20:
            validation_errors.append("Movement ID must be between 5 and 20 characters in length.")
        else:
            # Check if movement_id already exists in the database.
            mysql = connectToMySQL('primeinventory$prime_inventory')
            query = "SELECT COUNT(*) AS count FROM movements WHERE movement_id = %(movement_id_2_from_form)s"
            result = mysql.query_db(query, data)
            if result[0]['count'] > 0:
                validation_errors.append("A movement with the same ID already exists.")

        # Validate location_id is present and selected by the user.
        if 'product_location_id_2' not in form_data or form_data['product_location_id_2'] == "":
            validation_errors.append("You must select a Location.")
        else:
            data["product_to_location_id_2_from_form"] = form_data['product_location_id_2']

    return data, validation_errors, first_sec_validation



# Validations for the update_product method.
def validate_update_product_method(form_data):
    validation_errors = []
    data = {
        'product_id_from_form': form_data['product_id'],
        'old_product_id_from_form': form_data['old_product_id'],
        'product_name_from_form': form_data['product_name'],
        'old_product_name_from_form': form_data['old_product_name'],
        'product_price_from_form': form_data['product_price'],
        'updation_user_id': form_data['user_id']
    }

    # Validate product_id length.
    if len(data['product_id_from_form']) < 5 or len(data['product_id_from_form']) > 20:
        validation_errors.append("Product ID must be between 5 and 20 characters in length.")
    else:
        # Check if product_id already exists in the database.
        mysql = connectToMySQL('primeinventory$prime_inventory')
        query = "SELECT COUNT(*) AS count FROM products WHERE  product_id = %(product_id_from_form)s" 
        result = mysql.query_db(query, data)
        # If the user didn't cahnge the ID:
        if result[0]['count'] > 0 and data['product_id_from_form'] != data['old_product_id_from_form']:
            validation_errors.append("A product with the same ID already exists.")

    # Validate product's name length.
    if len(data['product_name_from_form']) < 3 or len(data['product_name_from_form']) > 20:
        validation_errors.append("Product name must be between 3 and 20 characters in length.")
    else:
        # Check if product's name already exists in the database.
        mysql = connectToMySQL('primeinventory$prime_inventory')
        query = "SELECT COUNT(*) AS count FROM products WHERE  name = %(product_name_from_form)s"
        result = mysql.query_db(query, data)
        if result[0]['count'] > 0 and data['product_name_from_form'] != data['old_product_name_from_form']:
            validation_errors.append("A product with the same name already exists.")

    # Validate product's price.'
    if data['product_price_from_form'] == "":
        validation_errors.append("Please insert a price for the product.")
    elif float(data['product_price_from_form']) <= 0:
        validation_errors.append("Please insert a positive number as a price.")

    return data, validation_errors




# //////////////////////////////////////////////  Movements Validations  ///////////////////////////////////////////////
# //////////////////////////////////////////////// ↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓ /////////////////////////////////////////////////




# Validations for the add_new_movement method.
def validate_add_new_movement_method(form_data):
    validation_errors = []

    data = {
        'movement_id_from_form': form_data['movement_id'],
        'movement_quantity_from_form': form_data['movement_quantity'],
        'creation_user_id': form_data['user_id']
    }

    # Validate movement_id length.
    if len(data['movement_id_from_form']) < 5 or len(data['movement_id_from_form']) > 20:
        validation_errors.append("Movement ID must be between 5 and 20 characters in length.")
    else:
        # Check if movement_id already exists in the database.
        mysql = connectToMySQL('primeinventory$prime_inventory')
        query = "SELECT COUNT(*) AS count FROM movements WHERE movement_id = %(movement_id_from_form)s"
        result = mysql.query_db(query, data)
        if result[0]['count'] > 0:
            validation_errors.append("A movement with the same ID already exists.")

    # Validate from_location_id is present and selected by the user.
    if 'from_location_id' not in form_data:
        validation_errors.append("You must select a 'From Location' first!")
    else:
        data["from_location_id_from_form"] = form_data['from_location_id']
        data["to_location_id_from_form"] = form_data['to_location_id']

        # Validate product_id when the user doesn't select any neither from the select menu nor typing down an ID in the text input.
        if 'product_id_input'in form_data and 'product_id_select' in form_data:
            validation_errors.append("You must choose a product either from the select menu or type its ID directly in the text area.")
        else:
            # Validate product_id when the user used the select input to choose a product.
            if 'product_id_select' in form_data and 'product_id_input' not in form_data:
                data['product_id_from_form'] = form_data['product_id_select']
            # Validate product_id when the user used the text input to enter a product id manually if he chosed any location rather "Out Sourcing" as a "From Location".
            elif form_data['product_id_input'] != "" and form_data['from_location_id'] != "out":
                # Validate product_id length.
                if len(form_data['product_id_input']) < 5 or len(form_data['product_id_input']) > 20:
                    validation_errors.append("Product ID must be between 5 and 20 characters in length.")
                    return data, validation_errors
                # Validate product_id availability in from_location when the user writes the product ID (product quantity in location > 0).
                data['product_id_from_form'] = form_data['product_id_input']
                mysql = connectToMySQL('primeinventory$prime_inventory')
                query = """
                    SELECT 
                        COALESCE(SUM(CASE WHEN m.to_location_id = %(from_location_id_from_form)s THEN m.quantity ELSE 0 END), 0) -
                        COALESCE(SUM(CASE WHEN m.from_location_id = %(from_location_id_from_form)s THEN m.quantity ELSE 0 END), 0) AS total_quantity
                    FROM movements m
                    WHERE m.product_id = %(product_id_from_form)s
                """
                result = mysql.query_db(query, data)
                total_quantity = result[0]['total_quantity']
                if total_quantity < 1:
                    validation_errors.append("The selected product is not available in the 'from' location.")
                    return data, validation_errors
            # Validate product_id when the user used the text input to enter a product id manually if he chosed "Out Sourcing" as a "From Location".
            elif form_data['product_id_input'] != "" and form_data['from_location_id'] == "out":
                # Validate product_id length.
                if len(form_data['product_id_input']) < 5 or len(form_data['product_id_input']) > 20:
                    validation_errors.append("Product ID must be between 5 and 20 characters in length.")
                    return data, validation_errors
                # Validate product_id is available in all products.
                data['product_id_from_form'] = form_data['product_id_input']
                mysql = connectToMySQL('primeinventory$prime_inventory')
                query = """
                    SELECT COUNT(*) AS product_count FROM products WHERE product_id = %(product_id_from_form)s
                """
                result = mysql.query_db(query, data)
                matched_products = result[0]['product_count']
                if matched_products == 0:
                    validation_errors.append("The selected product ID is not available.")
                    return data, validation_errors

            # Validate the quantity of the movement if the user left it blank or not.
            if data['movement_quantity_from_form'] == "":
                validation_errors.append("Please insert a number in the quantity area.")
            else:
                movement_quantity = float(data['movement_quantity_from_form'])
                # Validate the quantity if it's less than or equal to zero or has decimal values.
                if movement_quantity <= 0 or not movement_quantity.is_integer():
                    validation_errors.append("Please insert a positive integer number as the quantity.")
                else:
                    if form_data['from_location_id'] != "out":
                        # Validate product_id availability in from_location (if the quantity in the location is more than or equal to movement's quantity).
                        mysql = connectToMySQL('primeinventory$prime_inventory')
                        query = """
                            SELECT 
                                COALESCE(SUM(CASE WHEN m.to_location_id = %(from_location_id_from_form)s THEN m.quantity ELSE 0 END), 0) -
                                COALESCE(SUM(CASE WHEN m.from_location_id = %(from_location_id_from_form)s THEN m.quantity ELSE 0 END), 0) AS total_quantity
                            FROM movements m
                            WHERE m.product_id = %(product_id_from_form)s
                        """
                        result = mysql.query_db(query, data)
                        total_quantity = result[0]['total_quantity']
                        if total_quantity < int(movement_quantity):
                            validation_errors.append("The selected quantity is more than the available quantity.")

    return data, validation_errors



# Validations for the update_movement method.
def validate_update_movement_method(form_data):
    validation_errors = []

    data = {
        'movement_id_from_form': form_data['movement_id'],
        'old_movement_id_from_form': form_data['old_movement_id'],
        'movement_quantity_from_form': form_data['movement_quantity'],
        'from_location_id_from_form': form_data['from_location_id'],
        'to_location_id_from_form': form_data['to_location_id'],
        'old_from_location_id': form_data['old_from_location_id'],
        'old_to_location_id': form_data['old_to_location_id'],
        'old_product_id': form_data['old_product_id'],
        'old_movement_quantity': form_data['old_movement_quantity'],
        'updation_user_id': form_data['user_id']
    }

    # Validate movement_id length.
    if len(data['movement_id_from_form']) < 5 or len(data['movement_id_from_form']) > 20:
        validation_errors.append("Movement ID must be between 5 and 20 characters in length.")
    else:
        # Check if movement_id already exists in the database.
        mysql = connectToMySQL('primeinventory$prime_inventory')
        query = "SELECT COUNT(*) AS count FROM movements WHERE movement_id = %(movement_id_from_form)s"
        result = mysql.query_db(query, data)
        if result[0]['count'] > 0 and data['movement_id_from_form'] != data['old_movement_id_from_form']:
            validation_errors.append("A movement with the same ID already exists.")

    # If the user used the select menu to choose a product.
    if 'product_id_select' in form_data and 'product_id_input' not in form_data:
        data['product_id_from_form'] = form_data['product_id_select']

        # If "From Location" is "Out Sourcing".
        if data['from_location_id_from_form'] == "out":
            # Validate the quantity of the movement if the user left it blank or not.
            if data['movement_quantity_from_form'] == "":
                validation_errors.append("Please insert a number in the quantity area.")
            else:
                movement_quantity = float(data['movement_quantity_from_form'])
                # Validate the quantity if it's less than or equal to zero or has decimal values.
                if movement_quantity <= 0 or not movement_quantity.is_integer():
                    validation_errors.append("Please insert a positive integer number as the quantity.")
            return data, validation_errors

        else:
            # Validate the quantity of the movement if the user left it blank or not.
            if data['movement_quantity_from_form'] == "":
                validation_errors.append("Please insert a number in the quantity area.")
            else:
                movement_quantity = float(data['movement_quantity_from_form'])
                # Validate the quantity if it's less than or equal to zero or has decimal values.
                if movement_quantity <= 0 or not movement_quantity.is_integer():
                    validation_errors.append("Please insert a positive integer number as the quantity.")
                else:
                    # Validate product_id availability in from_location (if the quantity in the location is more than or equal to movement's quantity).
                    mysql = connectToMySQL('primeinventory$prime_inventory')
                    query = """
                        SELECT 
                            COALESCE(SUM(CASE WHEN m.to_location_id = %(from_location_id_from_form)s THEN m.quantity ELSE 0 END), 0) -
                            COALESCE(SUM(CASE WHEN m.from_location_id = %(from_location_id_from_form)s THEN m.quantity ELSE 0 END), 0) AS total_quantity
                        FROM movements m
                        WHERE m.product_id = %(product_id_from_form)s
                    """
                    result = mysql.query_db(query, data)
                    total_quantity = result[0]['total_quantity']
                    # If the product also didn't change.
                    if data['product_id_from_form'] == data['old_product_id']:
                        if (data['from_location_id_from_form'] == data['old_from_location_id']) and (data['product_id_from_form'] == data['old_product_id']) :
                            total_quantity = total_quantity + int(data["old_movement_quantity"])
                            print("kkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkk")
                        elif(data['from_location_id_from_form'] == data['old_to_location_id']) and (data['product_id_from_form'] == data['old_product_id']) :
                            total_quantity = total_quantity - int(data["old_movement_quantity"])
                    if total_quantity <= 0:
                        validation_errors.append("The selected product is not available in the 'from' location.")
                    elif movement_quantity > total_quantity:
                        validation_errors.append("The selected quantity is more than the available quantity.")
            return data, validation_errors

    # If the user used the text input choose a product.
    # Validate product_id availability in from_location when the user writes the product ID (product quantity in location > 0).
    elif ('product_id_input' in form_data and 'product_id_select' not in form_data) or (form_data['product_id_input'] != "" and form_data['product_id_select'] == ""):
        # If the length of the ID is not enough (less than 5 chracters).
        if len(form_data['product_id_input']) < 5 or len(form_data['product_id_input']) > 20:
            validation_errors.append("Product ID must be between 5 and 20 characters in length.")
            return data, validation_errors

        data['product_id_from_form'] = form_data['product_id_input']
        # If "From Location" is "Out Sourcing".
        if data['from_location_id_from_form'] == "out":
            # Validate product_id when the user used the text input to enter a product id manually if he chosed None as a "From Location".
            # Validate product_id is available in "all products".
            data['product_id_from_form'] = form_data['product_id_input']
            mysql = connectToMySQL('primeinventory$prime_inventory')
            query = """
                SELECT COUNT(*) AS product_count FROM products WHERE product_id = %(product_id_from_form)s
            """
            result = mysql.query_db(query, data)
            matched_products = result[0]['product_count']
            if matched_products == 0:
                validation_errors.append("The selected product ID is not available.")
            # Validate the quantity of the movement if the user left it blank or not.
            elif data['movement_quantity_from_form'] == "":
                validation_errors.append("Please insert a number in the quantity area.")
            else:
                movement_quantity = float(data['movement_quantity_from_form'])
                # Validate the quantity if it's less than or equal to zero or has decimal values.
                if movement_quantity <= 0 or not movement_quantity.is_integer():
                    validation_errors.append("Please insert a positive integer number as the quantity.")
            return data, validation_errors

        else:
            # Validate product_id availability in from_location (if the quantity in the location is more than or equal to movement's quantity).
            mysql = connectToMySQL('primeinventory$prime_inventory')
            query = """
                SELECT 
                    COALESCE(SUM(CASE WHEN m.to_location_id = %(from_location_id_from_form)s THEN m.quantity ELSE 0 END), 0) -
                    COALESCE(SUM(CASE WHEN m.from_location_id = %(from_location_id_from_form)s THEN m.quantity ELSE 0 END), 0) AS total_quantity
                FROM movements m
                WHERE m.product_id = %(product_id_from_form)s
            """
            result = mysql.query_db(query, data)
            total_quantity = result[0]['total_quantity']
            print("vvvvvvvvvvvvvvvvvvvvvv")
            print(total_quantity)
            # If the product also didn't change.
            if data['product_id_from_form'] == data['old_product_id']:
                if (data['from_location_id_from_form'] == data['old_from_location_id']) and (data['product_id_from_form'] == data['old_product_id']) :
                    total_quantity = total_quantity + int(data["old_movement_quantity"])
                    print("kkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkk")
                    print(total_quantity)
                elif(data['from_location_id_from_form'] == data['old_to_location_id']) and (data['product_id_from_form'] == data['old_product_id']) :
                    total_quantity = total_quantity - int(data["old_movement_quantity"])
            if total_quantity <= 0:
                validation_errors.append("The selected product is not available in the 'from' location.")
            # Validate the quantity of the movement if the user left it blank or not.
            elif data['movement_quantity_from_form'] == "":
                validation_errors.append("Please insert a number in the quantity area.")
            else:
                movement_quantity = float(data['movement_quantity_from_form'])
                # Validate the quantity if it's less than or equal to zero or has decimal values.
                if movement_quantity <= 0 or not movement_quantity.is_integer():
                    validation_errors.append("Please insert a positive integer number as the quantity.")
                if movement_quantity > total_quantity:
                    validation_errors.append("The selected quantity is more than the available quantity.")
            return data, validation_errors

    # If the user didn't choose any product ID neither from the select noe from the text input.
    elif form_data['product_id_input'] == "" and form_data['product_id_select'] == "":
        validation_errors.append("You must select a product or enter valid product ID.")
        return data, validation_errors




# //////////////////////////////////////////////  Users Validations  ///////////////////////////////////////////////
# //////////////////////////////////////////////// ↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓ /////////////////////////////////////////////////




# Validations for the update_user_profile method.
def validate_update_user_profile_method(form_data, form_files, checked_user):
    EMAIL_REGEX = re.compile(r'^[a-zA-Z0-9.+_-]+@[a-zA-Z0-9._-]+\.[a-zA-Z]+$') 
    NAME_REGEX = re.compile(r"^[a-zA-Z ,.'-]+$")
    validation_errors = []

    data = {
        'first_name_from_form': form_data['first_name'],         
        'last_name_from_form': form_data['last_name'],
        'email_from_form': form_data['email'],
        'gender_from_form': form_data['gender'],
        'phone_from_form': form_data['phone'],
        'job_title_from_form': form_data['job_title'],
        'country_from_form': form_data['country'],
        'city_from_form': form_data['city'],
        'street_from_form': form_data['street'],
        'postal_code_from_form': form_data['postal_code'],
        'user_id_from_session': session['user_id'],
        'old_email_form_form': form_data['old_email']
    }

    # First Name:
    if len(form_data['first_name']) < 2:
        validation_errors.append(("First Name must be at least 2 characters.", 'first_name'))
        print("the error in first name2")
    elif not NAME_REGEX.match(form_data['first_name']):
        validation_errors.append(("First Name field can not contain numbers or unusual signs.", 'first_name'))
        print("the error in first name1")
    if len(form_data['first_name']) > 50:
        validation_errors.append(("First Name must be at most 50 characters.", 'first_name'))
        print("the error in first name3")

    # Last Name:
    if len(form_data['last_name']) < 2:
        validation_errors.append(("Last Name must be at least 2 characters.", 'last_name'))
        print("the error in last name2")
    elif not NAME_REGEX.match(form_data['last_name']):
        validation_errors.append(("Last Name field can not contain numbers or unusual signs.", 'last_name'))
        print("the error in last name1")
    if len(form_data['last_name']) > 50:
        validation_errors.append(("Last Name must be at most 50 characters.", 'last_name'))
        print("the error in last name 3")

    # Email:
    if len(form_data['email']) < 1:
        validation_errors.append(("Please, enter your email.", 'email'))
        print("the error in last name2")
    elif not EMAIL_REGEX.match(form_data['email']):
        validation_errors.append(("Invalid email address.", 'email'))
        print("the error in email 1")
    # Check if the entered email already used before.
    mysql = connectToMySQL('primeinventory$prime_inventory')
    emails_query = "SELECT COUNT(*) AS count FROM users WHERE email = %(email_from_form)s;"
    result = mysql.query_db(emails_query, data)
    if result[0]['count'] > 0 and data['email_from_form'] != data['old_email_form_form']:
        validation_errors.append("A location with the same ID already exists.", 'email')

    # Gender:
    if ('gender' not in form_data) or (form_data['gender'] == ""):
        validation_errors.append(("Please select your gender.", 'gender'))
        print("the error in gender 1")
        # print(request.form['gender'])

    # Phone Number:
    if ('phone' not in form_data) or (form_data['phone'] == ""):
        validation_errors.append(("Please enter your phone number.", 'phone'))
        print("the error in phone 1")
        # print(request.form['phone'])

    # Job Title.
    if ('job_title' not in form_data) or (form_data['job_title'] == ""):
        validation_errors.append(("Please select your job title.", 'job_title'))
        print("the error in job title 1")
        # print(request.form['job_title'])
    
    # Country:
    if ('country' not in form_data) or (form_data['country'] == ""):
        validation_errors.append(("Please select your country.", 'country'))
        print("the error in country 1")
        # print(request.form['country'])

    # City:
    if len(form_data['city']) < 2:
        validation_errors.append(("City name must be at least 2 characters.", 'city'))
        print("the error in city 1")
    elif len(form_data['city']) > 50:
        validation_errors.append(("City name must be at most 50 characters.", 'city'))
        print("the error in city 2")

    # Street:
    if len(form_data['street']) < 2:
        validation_errors.append(("Street name must be at least 2 characters.", 'street'))
        print("the error in street 1")
    elif len(form_data['street']) > 50:
        validation_errors.append(("Street name must be at most 50 characters.", 'street'))
        print("the error in street 2")

    # Postal Code:
    if len(form_data['postal_code']) < 1:
        validation_errors.append(("Please enter your postal code.", 'postal_code'))
        print("the error in postal code 1")
    elif len(form_data['postal_code']) > 10:
        validation_errors.append(("Postal code can't be more than 10 characters.", 'postal_code'))
        print("the error in postal code 2")

    # Validate user's image:
    # If the user decided to uplaod a new photo file:
    file = None
    if "user_image" in form_files:
        file = form_files['user_image']
        if file.filename != '':
            # Check the type of the photo file.
            ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}
            # file = request.files['location_image']
            if '.' not in file.filename or file.filename.rsplit('.', 1)[1].lower() not in ALLOWED_EXTENSIONS:
                validation_errors.append(("The file must be a photo type.",' user_iamge'))
            else:
                # Get the current file's directory.
                current_directory = os.path.dirname(__file__)
                # Define the relative path to the target directory (one level up).
                relative_path = '../static/uploads/users_photos'

                # Construct the path to the old image to replace it with the new one.
                # (You can remove the next 5 lines if u want to keep the old image along with the new one)
                old_image_path = os.path.join(current_directory, relative_path, checked_user['user_image_id'])
                # Check if the old image file exists and it's not the default image before trying to delete it
                if os.path.exists(old_image_path) and checked_user['user_image_id'] not in['female_default_user.jpg', 'male_default_user_jpg']:
                    # Delete the old image file
                    os.remove(old_image_path)

                # Construct the complete path to save the image.
                image_path = os.path.join(current_directory, relative_path)
                # Process the uploaded image.
                file = form_files['user_image']
                original_filename = secure_filename(file.filename)
                # Generate a unique filename (image_id) using UUID.
                image_id = f"{uuid.uuid4()}_{original_filename}"
                # Append the image_id to the path.
                image_path = os.path.join(image_path, image_id)
                # Save the file.
                file.save(image_path)

    # Validate location's image if the user didnt update it, then use the old one:
    if 'user_image' not in form_files or file.filename == '':
        image_id =  checked_user['user_image_id']

    data['user_image_from_form'] = image_id
    return data, validation_errors



# Validations for the change_user_account_password method.
def validate_change_user_account_password(form_data):
    PASSWORD_REGEX = re.compile(r'^(?=.*\d)(?=.*\W)(?=.*[A-Z]).+$')
    bcrypt = Bcrypt()  # Create an instance of the Bcrypt class
    validation_errors = []

    data = {
        'old_password_from_form': form_data['old_password'],
        'new_password_from_form': form_data['new_password'],
        'confirm_new_passwrd_from_form': form_data['confirm_new_password'], 
        'user_id_from_session': session['user_id']
    }

    # The next 3 if statements is to validate the old passord input: 
    if len(form_data['old_password']) < 1:
        validation_errors.append(("Please, enter your password.", 'old_password'))
        return data, validation_errors

    if len(form_data['old_password']) < 10:
        validation_errors.append(("Definitely your old password isn't this short!", 'old_password'))
        return data, validation_errors

    mysql = connectToMySQL('primeinventory$prime_inventory')
    password_query = "SELECT password from users where user_id = %(user_id_from_session)s;"
    result = mysql.query_db(password_query, data)
    if not bcrypt.check_password_hash(result[0]['password'], form_data['old_password']):
        validation_errors.append(("That's not your old password!", 'old_password'))
        return data, validation_errors

    # The next if statements is to validate the new password input:
    if len(form_data['new_password']) < 1:
        validation_errors.append(("Please, enter your new password.", 'new_password'))
        return data, validation_errors

    if len(form_data['new_password']) < 10:
        validation_errors.append(("The new password must be at least 10 characters.", 'new_password'))
        # return data, validation_errors

    if not PASSWORD_REGEX.match(form_data['new_password']):
        validation_errors.append((
            "The new password must contain at least one digit, one symbol, and one uppercase letter.", 'new_password'
        ))
        return data, validation_errors

    # The next if statements is to validate the "confirm new password" input:
    if form_data['new_password'] != form_data['confirm_new_password']:
        validation_errors.append(("Passwords do not match!", 'confirm_new_password'))

    return data, validation_errors