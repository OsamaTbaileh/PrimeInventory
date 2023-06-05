import os
import base64

from mysqlconnection import connectToMySQL   # import the function that will return an instance of a connection


# //////////////////////////////////////////////  Locations Validations  //////////////////////////////////////////////
# ///////////////////////////////////////////////// ↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓ ////////////////////////////////////////////////



# Validations for the add_new_location method.
def validate_add_new_location_method(form_data, form_files):
    validation_errors = []
    data = {
        'location_id_from_form': form_data['location_id'],
        'location_name_from_form': form_data['location_name'],
    }

    # Validate location_id length.
    if len(data['location_id_from_form']) < 5 or len(data['location_id_from_form']) > 20:
        validation_errors.append("Location ID must be between 5 and 20 characters in length.")
    else:
        # Check if location_id already exists in the database.
        mysql = connectToMySQL('prime_inventory')
        query = "SELECT COUNT(*) AS count FROM locations WHERE location_id = %(location_id_from_form)s"
        result = mysql.query_db(query, data)
        if result[0]['count'] > 0:
            validation_errors.append("A location with the same ID already exists.")

    # Validate location's name length.
    if len(data['location_name_from_form']) < 5 or len(data['location_name_from_form']) > 20:
        validation_errors.append("Location name must be between 5 and 20 characters in length.")
    else:
        # Check if location's name already exists in the database.
        mysql = connectToMySQL('prime_inventory')
        query = "SELECT COUNT(*) AS count FROM locations WHERE name = %(location_name_from_form)s"
        result = mysql.query_db(query, data)
        if result[0]['count'] > 0:
            validation_errors.append("A location with the same name already exists.")

    # Validate location's image:
    # The "or not" condition to make sure that even if the key is present in the dic. form.files but it's vlue 
    # is empty or not provided then it will go through this conditoin. 
    if 'location_image' not in form_files or not form_files['location_image']:  
        # If the user didn't upload any image for the location, use the default image.
        default_image_path = os.path.join('static', 'img', 'default.png')   # Create string with the required path.
        with open(default_image_path, 'rb') as image_file:  # Open the image and read it as binary and store it in 
            image_data = base64.b64encode(image_file.read()).decode('utf-8')
        data['location_image_from_form'] = image_data
    else:
        # Process the uploaded image.
        image_file = form_files['location_image']
        image_data = base64.b64encode(image_file.read()).decode('utf-8')
        data['location_image_from_form'] = image_data

    return data, validation_errors



# Validations for the update_location method.
def validate_update_location_method(form_data, form_files):
    validation_errors = []
    data = {
        'location_id_from_form': form_data['location_id'],
        'old_location_id_from_form': form_data['old_location_id'],
        'location_name_from_form': form_data['location_name'],
        'old_location_name_from_form': form_data['old_location_name'],
    }

    # Validate location_id length.
    if len(data['location_id_from_form']) < 5 or len(data['location_id_from_form']) > 20:
        validation_errors.append("Location ID must be between 5 and 20 characters in length.")
    else:
        # Check if location_id already exists in the database.
        mysql = connectToMySQL('prime_inventory')
        query = "SELECT COUNT(*) AS count FROM locations WHERE location_id = %(location_id_from_form)s"
        result = mysql.query_db(query, data)
        if result[0]['count'] > 0 and data['location_id_from_form'] != data['old_location_id_from_form']:
            validation_errors.append("A location with the same ID already exists.")

    # Validate location's name length.
    if len(data['location_name_from_form']) < 5 or len(data['location_name_from_form']) > 20:
        validation_errors.append("Location name must be between 5 and 20 characters in length.")
    else:
        # Check if location's name already exists in the database.
        mysql = connectToMySQL('prime_inventory')
        query = "SELECT COUNT(*) AS count FROM locations WHERE name = %(location_name_from_form)s"
        result = mysql.query_db(query, data)
        if result[0]['count'] > 0 and data['location_name_from_form'] != data['old_location_name_from_form']:
            validation_errors.append("A location with the same name already exists.")

    # Validate location's image:
    #Checking if the user inputted a new image or not.
    if 'location_image' not in form_files or not form_files['location_image']:  
        # If no, then the old image is going to be used.
        image_data = form_data['old_image']
    else:
        # If yes, then its will be proccessed to the database.
        image_file = form_files['location_image']
        image_data = base64.b64encode(image_file.read()).decode('utf-8')
    data['location_image_from_form'] = image_data,

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
        }

        # Validate product_id when the user doesn't select any neither from the select menu nor typing down an ID in the text input.
        if 'product_id_select_1' in form_data and 'product_id_input_1' in form_data:
            validation_errors.append("You must choose a product either from the select menu or type its ID directly in the text area.")
        # If the user entered a product_id manually in the text input.
        elif 'product_id_input_1' in form_data:
            data['product_id_from_form'] = form_data['product_id_input_1']
            # Check if product_id exists in the database.
            mysql = connectToMySQL('prime_inventory')
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
            mysql = connectToMySQL('prime_inventory')
            query = "SELECT COUNT(*) AS count FROM movements WHERE movement_id = %(movement_id_1_from_form)s"
            result = mysql.query_db(query, data)
            if result[0]['count'] > 0:
                validation_errors.append("A movement with the same ID already exists.")

        # Validate from_location_id is present and selected by the user.
        if 'product_location_id_1' not in form_data or form_data['product_location_id_1'] == "":
            validation_errors.append("You must select a Location.")
        else:
            data["product_location_id_1_from_form"] = form_data['product_location_id_1']

    # If the second checkbox is checked (add new product).
    else:
        first_sec_validation = False
        data = {
            'product_id_2_from_form' : form_data['product_id_2'],
            'product_name_2_from_form' : form_data['product_name_2'],
            'product_price_2_from_form' : form_data['product_price_2'],
            'product_quantity_2_from_form' : form_data['product_quantity_2'],
            'movement_id_2_from_form' : form_data['movement_id_2'],
        }

        # Validate product_id length.
        if len(data['product_id_2_from_form']) < 5 or len(data['product_id_2_from_form']) > 20:
            validation_errors.append("product ID must be between 5 and 20 characters in length.")
        else:
            # Check if product_id already exists in the database.
            mysql = connectToMySQL('prime_inventory')
            query = "SELECT COUNT(*) AS count FROM products WHERE product_id = %(product_id_2_from_form)s"
            result = mysql.query_db(query, data)
            if result[0]['count'] > 0:
                validation_errors.append("A product with the same ID already exists.")
        
        # Validate product's name length.
        if len(data['product_name_2_from_form']) < 3 or len(data['product_name_2_from_form']) > 20:
            validation_errors.append("Product name must be between 3 and 20 characters in length.")
        else:
            # Check if product's name already exists in the database.
            mysql = connectToMySQL('prime_inventory')
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
            mysql = connectToMySQL('prime_inventory')
            query = "SELECT COUNT(*) AS count FROM movements WHERE movement_id = %(movement_id_2_from_form)s"
            result = mysql.query_db(query, data)
            if result[0]['count'] > 0:
                validation_errors.append("A movement with the same ID already exists.")

        # Validate location_id is present and selected by the user.
        if 'product_location_id_2' not in form_data or form_data['product_location_id_2'] == "":
            validation_errors.append("You must select a Location.")
        else:
            data["product_location_id_2_from_form"] = form_data['product_location_id_2']

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
    }

    # Validate product_id length.
    if len(data['product_id_from_form']) < 5 or len(data['product_id_from_form']) > 20:
        validation_errors.append("Product ID must be between 5 and 20 characters in length.")
    else:
        # Check if product_id already exists in the database.
        mysql = connectToMySQL('prime_inventory')
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
        mysql = connectToMySQL('prime_inventory')
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
    }

    # Validate movement_id length.
    if len(data['movement_id_from_form']) < 5 or len(data['movement_id_from_form']) > 20:
        validation_errors.append("Movement ID must be between 5 and 20 characters in length.")
    else:
        # Check if movement_id already exists in the database.
        mysql = connectToMySQL('prime_inventory')
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
            # Validate product_id when the user used the text input to enter a product id manually if he chosed any location rather None as a "From Location".
            elif form_data['product_id_input'] != "" and form_data['from_location_id'] != "NULL":
                # Validate product_id availability in from_location when the user writes the product ID (product quantity in location > 0).
                data['product_id_from_form'] = form_data['product_id_input']
                mysql = connectToMySQL('prime_inventory')
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
            # Validate product_id when the user used the text input to enter a product id manually if he chosed None as a "From Location".
            elif form_data['product_id_input'] != "" and form_data['from_location_id'] == "NULL":
                # Validate product_id is available in all products.
                data['product_id_from_form'] = form_data['product_id_input']
                mysql = connectToMySQL('prime_inventory')
                query = """
                    SELECT COUNT(*) AS product_count FROM products WHERE product_id = %(product_id_from_form)s
                """
                result = mysql.query_db(query, data)
                matched_products = result[0]['product_count']
                if matched_products == 0:
                    validation_errors.append("The selected product ID is not available.")

            # Validate the quantity of the movement if the user left it blank or not.
            if data['movement_quantity_from_form'] == "":
                validation_errors.append("Please insert a number in the quantity area.")
            else:
                movement_quantity = float(data['movement_quantity_from_form'])
                # Validate the quantity if it's less than or equal to zero or has decimal values.
                if movement_quantity <= 0 or not movement_quantity.is_integer():
                    validation_errors.append("Please insert a positive integer number as the quantity.")
                else:
                    if form_data['from_location_id'] != "NULL":
                        # Validate product_id availability in from_location (if the quantity in the location is more than or equal to movement's quantity).
                        mysql = connectToMySQL('prime_inventory')
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
        'old_movement_quantity': form_data['old_movement_quantity']
    }
    print("xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx")
    print(data)
    # Validate movement_id length.
    if len(data['movement_id_from_form']) < 5 or len(data['movement_id_from_form']) > 20:
        validation_errors.append("Movement ID must be between 5 and 20 characters in length.")
    else:
        # Check if movement_id already exists in the database.
        mysql = connectToMySQL('prime_inventory')
        query = "SELECT COUNT(*) AS count FROM movements WHERE movement_id = %(movement_id_from_form)s"
        result = mysql.query_db(query, data)
        if result[0]['count'] > 0 and data['movement_id_from_form'] != data['old_movement_id_from_form']:
            validation_errors.append("A movement with the same ID already exists.")

    # If the user used the select menu to choose a product.
    if 'product_id_select' in form_data and 'product_id_input' not in form_data:
        data['product_id_from_form'] = form_data['product_id_select']


    # Validate product_id availability in from_location when the user writes the product ID (product quantity in location > 0).
    elif ('product_id_input' in form_data and 'product_id_select' not in form_data) or (form_data['product_id_input'] != "" and form_data['product_id_select'] == ""):
        data['product_id_from_form'] = form_data['product_id_input']

        # If "From Location" is None.
        if data['from_location_id_from_form'] == "NULL":
            # Validate product_id when the user used the text input to enter a product id manually if he chosed None as a "From Location".
            # Validate product_id is available in "all products".
            data['product_id_from_form'] = form_data['product_id_input']
            mysql = connectToMySQL('prime_inventory')
            query = """
                SELECT COUNT(*) AS product_count FROM products WHERE product_id = %(product_id_from_form)s
            """
            result = mysql.query_db(query, data)
            matched_products = result[0]['product_count']
            if matched_products == 0:
                validation_errors.append("The selected product ID is not available.")
            # Validate the quantity of the movement if the user left it blank or not.
            if data['movement_quantity_from_form'] == "":
                validation_errors.append("Please insert a number in the quantity area.")
            else:
                movement_quantity = float(data['movement_quantity_from_form'])
                # Validate the quantity if it's less than or equal to zero or has decimal values.
                if movement_quantity <= 0 or not movement_quantity.is_integer():
                    validation_errors.append("Please insert a positive integer number as the quantity.")

        # If "From Location" didnt change.
        elif (data['from_location_id_from_form'] == data['old_from_location_id']) or (data['from_location_id_from_form'] == data['old_to_location_id']):
            # Validate product_id availability in from_location when the user writes the product ID (product quantity in location > 0).
            mysql = connectToMySQL('prime_inventory')
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
                elif(data['from_location_id_from_form'] == data['old_to_location_id']) and (data['product_id_from_form'] == data['old_product_id']) :
                    total_quantity = total_quantity - int(data["old_movement_quantity"])
            if total_quantity <= 0:
                validation_errors.append("The selected product is not available in the 'from' location.")
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
                        mysql = connectToMySQL('prime_inventory')
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
                            elif(data['from_location_id_from_form'] == data['old_to_location_id']) and (data['product_id_from_form'] == data['old_product_id']) :
                                total_quantity = total_quantity - int(data["old_movement_quantity"])
                        if total_quantity <= 0:
                            validation_errors.append("The selected product is not available in the 'from' location.")

        else:
            # Validate product_id availability in from_location when the user writes the product ID (product quantity in location > 0).
            mysql = connectToMySQL('prime_inventory')
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
                total_quantity = total_quantity - int(data["old_movement_quantity"])
            if total_quantity <= 0:
                validation_errors.append("The selected product is not available in the 'from' location.")
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
                        mysql = connectToMySQL('prime_inventory')
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
                            elif(data['from_location_id_from_form'] == data['old_to_location_id']) and (data['product_id_from_form'] == data['old_product_id']) :
                                total_quantity = total_quantity - int(data["old_movement_quantity"])
                        if total_quantity <= 0:
                            validation_errors.append("The selected product is not available in the 'from' location.")

    # If the user didn't choose any product ID neither from the select noe from the text input.
    elif form_data['product_id_input'] == "" and form_data['product_id_select'] == "":
        validation_errors.append("you must select a product or enter valid product ID.")

    return data, validation_errors


















