from flask import Blueprint, render_template, redirect, request, session, flash, jsonify
from mysqlconnection import connectToMySQL   # import the function that will return an instance of a connection
from flask_bcrypt import Bcrypt
from werkzeug.utils import secure_filename
from validations.validations import *
import os, re, uuid


app = Blueprint('user', __name__)



# Render the SignUp/SignIn page.
@app.route("/sign_in")
def render_login_page():
    # Save flash messages before clearing the session
    flash_messages = session.get('_flashes', [])

    # Clear everything in the session
    session.clear()

    # Restore flash messages
    session['_flashes'] = flash_messages
    return render_template("login_register/login_register.html")


EMAIL_REGEX = re.compile(r'^[a-zA-Z0-9.+_-]+@[a-zA-Z0-9._-]+\.[a-zA-Z]+$') 
NAME_REGEX = re.compile(r"^[a-zA-Z ,.'-]+$")
PASSWORD_REGEX = re.compile(r'^(?=.*\d)(?=.*\W)(?=.*[A-Z]).+$')
bcrypt = Bcrypt()  # Create an instance of the Bcrypt class

@app.route("/create_user", methods=['POST'])
def create_user():
    error = False
    # Check if the entered email already used before.
    mysql = connectToMySQL('primeinventory$prime_inventory')
    data = { "email_from_form" : request.form['email'] }
    emails_query = "SELECT user_id FROM users WHERE email = %(email_from_form)s;"
    emails = mysql.query_db(emails_query, data)

    # First Name:
    if len(request.form['first_name']) < 2:
        flash("First Name must be at least 2 characters.", 'first_name')
        error = True
    elif not NAME_REGEX.match(request.form['first_name']):
        flash("First Name field can not contain numbers or unusual signs.", 'first_name')
        error = True
    if len(request.form['first_name']) > 50:
        flash("First Name must be at most 50 characters.", 'first_name')
        error = True

    # Last Name:
    if len(request.form['last_name']) < 2:
        flash("Last Name must be at least 2 characters.", 'last_name')
        error = True
    elif not NAME_REGEX.match(request.form['last_name']):
        flash("Last Name field can not contain numbers or unusual signs.", 'last_name')
        error = True
    if len(request.form['last_name']) > 50:
        flash("Last Name must be at most 50 characters.", 'last_name')
        error = True

    # Email:
    if len(request.form['email']) < 1:
        flash("Please, enter your email.", 'email')
        error = True
    elif not EMAIL_REGEX.match(request.form['email']):
        flash("Invalid email address.", 'email')
        error = True
    elif emails:
        flash("This email is already used.", 'email')
        error = True

    # Password:
    if len(request.form['password']) < 1:
        flash("Please, enter your password.", 'password')
        error = True
    elif len(request.form['password']) < 10:
        flash("Password must be at least 10 characters.", 'password')
        error = True
    elif request.form['password'] != request.form['confirm_password']:
        flash("Passwords do not match", 'password')
        error = True
    # if not PASSWORD_REGEX.match(request.form['password']):
    #     flash("Password must contain at least one digit, one symbol, and one uppercase letter.", 'password')
    #     error = True

    # Gender:
    if ('gender' not in request.form) or (request.form['gender'] == ""):
        flash("Please select your gender.", 'gender')
        error = True

    # Phone Number:
    if ('phone' not in request.form) or (request.form['phone'] == ""):
        flash("Please enter your phone number.", 'phone')
        error = True

    # Job Title.
    if ('job_title' not in request.form) or (request.form['job_title'] == ""):
        flash("Please select your job title.", 'job_title')
        error = True

    # Country:
    if ('country' not in request.form) or (request.form['country'] == ""):
        flash("Please select your country.", 'country')
        error = True

    # City:
    if len(request.form['city']) < 2:
        flash("City name must be at least 2 characters.", 'city')
        error = True
    elif len(request.form['city']) > 50:
        flash("City name must be at most 50 characters.", 'city')
        error = True

    # Street:
    if len(request.form['street']) < 2:
        flash("Street name must be at least 2 characters.", 'street')
        error = True
    elif len(request.form['street']) > 50:
        flash("Street name must be at most 50 characters.", 'street')
        error = True

    # Postal Code:
    if len(request.form['postal_code']) < 1:
        flash("Please enter your postal code.", 'postal_code')
        error = True
    elif len(request.form['postal_code']) > 10:
        flash("Postal code can't be more than 10 characters.", 'postal_code')
        error = True

    # User Image:
    # If the user decided to uplaod a photo file:
    file = None
    if "user_image" in request.files:
        file = request.files['user_image']
        if file.filename != '':
            # Check the type of the photo file.
            ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}
            # file = request.files['user_image']
            if '.' not in file.filename or file.filename.rsplit('.', 1)[1].lower() not in ALLOWED_EXTENSIONS:
                flash("The file must be a photo type.", 'user_image')
                error = True

    if error == True:
        flash("error", 'error')
        return redirect('/sign_in') 
    else:
        # Validate user's image:
        if 'user_image' not in request.files or file.filename == '':  
            if request.form['gender'] == 'f':
                image_id = "female_default_user.jpg"
            else:
                image_id = "male_default_user.jpg"
        else:
            # Get the current file's directory.
            current_directory = os.path.dirname(__file__)
            # Define the relative path to the target directory (one level up).
            relative_path = '../static/uploads/users_photos'
            
            # Construct the complete path to save the image.
            image_path = os.path.join(current_directory, relative_path)
            # Process the uploaded image.
            file = request.files['user_image']
            original_filename = secure_filename(file.filename)
            # Generate a unique filename (image_id) using UUID.
            image_id = f"{uuid.uuid4()}_{original_filename}"
            # Append the image_id to the path.
            image_path = os.path.join(image_path, image_id)
            # Save the file.
            file.save(image_path)
        # create the hash
        register_pass_hash = bcrypt.generate_password_hash(request.form['password'])  
        mysql = connectToMySQL("primeinventory$prime_inventory")
        data = {
            "fname_from_form": request.form['first_name'],
            "lname_from_form": request.form['last_name'],
            "email_from_form": request.form['email'],
            "register_pass_hash": register_pass_hash,
            "gender_from_form": request.form['gender'],
            "phone_from_form": request.form['phone'],
            "user_image_from_form": image_id,
            "job_title_from_form": request.form['job_title'],
            "country_from_form": request.form['country'],
            "city_from_form": request.form['city'],
            "street_form_form": request.form['street'],
            "postal_code_from_form": request.form['postal_code']
        }
        register_query = """ 
            INSERT INTO users (first_name, last_name, email, password, gender, phone, image_id, job_title) 
            VALUES (%(fname_from_form)s, %(lname_from_form)s, %(email_from_form)s, %(register_pass_hash)s, 
            %(gender_from_form)s, %(phone_from_form)s, %(user_image_from_form)s, %(job_title_from_form)s);
        """ 
        mysql.query_db(register_query,data)

        # adding the user's address to the database:
        mysql = connectToMySQL("primeinventory$prime_inventory")
        fetch_the_new_user_id_query = "SELECT user_id FROM users WHERE email = %(email_from_form)s;"
        data['new_user_id'] = mysql.query_db(fetch_the_new_user_id_query,data)[0]['user_id']
        mysql = connectToMySQL("primeinventory$prime_inventory")
        adding_address_query = """
            INSERT INTO addresses (country, city, street, postal_code, user_id) 
            VALUES (%(country_from_form)s, %(city_from_form)s, %(street_form_form)s, %(postal_code_from_form)s, %(new_user_id)s);
        """ 
        mysql.query_db(adding_address_query,data)

        flash("Registration Successful! Thank you for registering, you may now sign in!", 'success')
        return redirect("/sign_in")


@app.route("/signing_in", methods=["POST"])
def sign_in():
    mysql = connectToMySQL('primeinventory$prime_inventory')
    data = { "email_from_form": request.form['email'] }
    check_email_query = "SELECT * FROM users WHERE email = %(email_from_form)s;"
    user = mysql.query_db(check_email_query,data)
    if user:
        if user[0]['email'] == request.form['email']:
            if bcrypt.check_password_hash(user[0]['password'], request.form['password']):
                session['user_id'] = user[0]['user_id']
                session['user_first_name'] = user[0]['first_name']
                session['user_last_name'] = user[0]['last_name']
                session['user_image_id'] = user[0]['image_id']
                session['user_job_title'] = replace_job_title(user[0]['job_title'])
                salted_created_at = str(user[0]['created_at']) + "saltyCoMmAander9/5"
                session['hashed_created_at'] = bcrypt.generate_password_hash(salted_created_at)
                return redirect('/dashboard')
    flash("Unauthorized Access: Sign In credentials are invalid!", 'fail')
    return redirect("/sign_in")


# This function will be excuted before each moevemnt and each route excution the validate the identity of the user.
def check_user_id():
    if 'user_id' in session:
        mysql = connectToMySQL('primeinventory$prime_inventory')
        query = "SELECT first_name, last_name, image_id, job_title, created_at FROM users WHERE user_id = %(user_id)s;"
        data = { 'user_id': session['user_id'] }
        user = mysql.query_db(query, data)
        salted_created_at = str(user[0]['created_at']) + "saltyCoMmAander9/5"
        if user and bcrypt.check_password_hash(session['hashed_created_at'], salted_created_at):
            return {
                "user_job_title": replace_job_title(user[0]['job_title']),
                "user_first_name": user[0]['first_name'],                
                "user_last_name": user[0]['last_name'],
                "user_image_id": user[0]['image_id']
            }
    return False


# replace the job_title and gender from the database with correct values.
def replace_job_title(inputt):
    job_titles = {
        1: "Head Master",
        2: "Manager",
        3: "Worker"
    }
    if type(inputt) == list:
        for member in inputt:
            member['job_title'] = job_titles[member['job_title']]
        return inputt
    return job_titles[inputt]


# Render dashboard page.
@app.route("/dashboard")
def home_index():
    checked_user = check_user_id()
    if checked_user:
        return render_template("users/dashboard.html", checked_user=checked_user)
    return redirect("/sign_out")


# Render user_profile page.
@app.route("/users/<user_id>")
def render_user_profile(user_id):
    checked_user = check_user_id()
    if checked_user:
        mysql = connectToMySQL('primeinventory$prime_inventory')
        # Retrieve the user's data based on the user's ID.
        user_query = """SELECT
                            u1.*,
                            u2.first_name AS supervisor_first_name,
                            u2.last_name AS supervisor_last_name
                        FROM users u1
                        LEFT JOIN users u2 ON u1.supervisor_id = u2.user_id
                        WHERE
                            u1.user_id = %(user_id_from_URL)s;"""
        data = {'user_id_from_URL': user_id}
        user = mysql.query_db(user_query, data)
        user = user[0]
        job_titles = {
            1: "Head Master",
            2: "Manager",
            3: "Worker"
        }
        genders = {
            "m": "Male",
            "f": "Female",
            "o": "Other"
        }
        user['job_title'] = job_titles[user['job_title']]
        user['gender'] = genders[user['gender']]

        mysql = connectToMySQL('primeinventory$prime_inventory')
        # Retrieve the user's Address based on the user's ID.
        address_query = "SELECT country, city, street, postal_code FROM addresses WHERE user_id = %(user_id_from_URL)s;"
        address = mysql.query_db(address_query, data)
        return render_template("users/user_profile.html", the_user=user, the_address = address[0], checked_user=checked_user)
    return render_template("general/home_page.html", checked_user=checked_user)


# Render update_profile_form page.
@app.route("/users/update_profile", methods=['GET'])
def render_update_profile_form():
    checked_user = check_user_id()
    if checked_user:
        mysql = connectToMySQL('primeinventory$prime_inventory')
        # Retrieve the user's data based on the user's ID.
        user_query = """SELECT
                            u1.*,
                            u2.first_name AS supervisor_first_name,
                            u2.last_name AS supervisor_last_name
                        FROM users u1
                        LEFT JOIN users u2 ON u1.supervisor_id = u2.user_id
                        WHERE
                            u1.user_id = %(user_id_from_session)s;"""
        data = {'user_id_from_session': session['user_id']}
        user = mysql.query_db(user_query, data)
        user = user[0]
        job_titles = {
            1: "Head Master",
            2: "Manager",
            3: "Worker"
        }
        genders = {
            "m": "Male",
            "f": "Female",
            "o": "Other"
        }
        user['job_title'] = job_titles[user['job_title']]
        user['gender'] = genders[user['gender']]

        mysql = connectToMySQL('primeinventory$prime_inventory')
        # Retrieve the user's Address based on the user's ID.
        address_query = "SELECT country, city, street, postal_code FROM addresses WHERE user_id = %(user_id_from_session)s;"
        address = mysql.query_db(address_query, data)
        return render_template("users/update_profile_form.html", the_user=user, the_address = address[0], checked_user=checked_user)
    return render_template("general/home_page.html", checked_user=checked_user)


# Update user rofile in the database.
@app.route("/users/update_user_profile", methods=["POST"])
def update_user_profile():
    checked_user = check_user_id()
    if checked_user:
        # Passing the data from the form to the validation method to validate it first then return the valid values from it.
        data, validation_errors = validate_update_user_profile_method(request.form, request.files, checked_user)

        if validation_errors:
            for error in validation_errors:
                flash(error[0], error[1])
            return redirect("/users/update_profile")

        # If the user changed his job_title from Manager to Worker then he will loose his team:
        if checked_user['user_job_title'] == "Manager" and data['job_title_from_form'] == 3:
            mysql = connectToMySQL('primeinventory$prime_inventory')
            update_team_query = """
                UPDATE users 
                SET supervisor_id = NULL,
                WHERE supervisor_id = %(user_id_from session)s
            """
            mysql.query_db(update_team_query, data)

        # If the user changed his job_title from Worker to Manager then he will loose his supervisor and will have the ability to have his own team:
        elif checked_user['user_job_title'] == "Worker" and data['job_title_from_form'] == 2:
            mysql = connectToMySQL('primeinventory$prime_inventory')
            update_team_query = """
                UPDATE users 
                SET supervisor_id = NULL,
                WHERE user_id = %(user_id_from session)s
            """
            mysql.query_db(update_team_query, data)

        # If the user didn't change his job_title (no need to change team or supervisor):
        mysql = connectToMySQL('primeinventory$prime_inventory')
        update_user_query = """
            UPDATE users 
            SET first_name = %(first_name_from_form)s,
                last_name = %(last_name_from_form)s, 
                email = %(email_from_form)s,
                gender = %(gender_from_form)s,
                phone = %(phone_from_form)s,
                image_id = %(user_image_from_form)s,
                job_title = %(job_title_from_form)s
            WHERE user_id = %(user_id_from_session)s
        """
        mysql.query_db(update_user_query, data)

        # update the user address:
        mysql = connectToMySQL('primeinventory$prime_inventory')
        update_user_address_query = """
            UPDATE addresses 
            SET country = %(country_from_form)s,
                city = %(city_from_form)s, 
                street = %(street_from_form)s,
                postal_code = %(postal_code_from_form)s
            WHERE user_id = %(user_id_from_session)s
        """
        mysql.query_db(update_user_address_query, data)

        return redirect("/users/" + str(session['user_id']))
    return redirect("/sign_out")


# Render change_account_password_form page.
@app.route("/users/update_profile/change_account_password")
def render_change_account_password_form():
    checked_user = check_user_id()
    if checked_user:
        return render_template("users/change_account_password_form.html", checked_user=checked_user)
    return redirect("/sign_out")

# Update user account password in the database.
@app.route("/users/update_profile/change_user_account_password", methods = ['POST'])
def change_user_account_password():
    checked_user = check_user_id()
    if checked_user:
        # Passing the data from the form to the validation method to validate it first then return the valid values from it.
        data, validation_errors = validate_change_user_account_password(request.form)

        if validation_errors:
            for error in validation_errors:
                flash(error[0], error[1])
            url = request.referrer 
            return redirect(url)
        
        # Update the password of the user:
        new_password_hash = bcrypt.generate_password_hash(data['new_password_from_form'])
        data['new_password_hash'] = new_password_hash
        mysql = connectToMySQL('primeinventory$prime_inventory')
        update_user_password_query = """
            UPDATE users 
            SET password = %(new_password_hash)s
            WHERE user_id = %(user_id_from_session)s
        """
        mysql.query_db(update_user_password_query, data)
        return redirect("/users/" + str(session['user_id']))
    return redirect("/sign_out")


# Add the choosen user to the current user team (set the current user as a supervisor to the choosen user).
# This route is only for users who got a job_title of manager.
@app.route("/teams/add_to_team/<user_id>")
def add_user_to_my_team(user_id):
    checked_user = check_user_id()
    if checked_user['user_job_title'] == "Manager":
        # Check if the logged user is a supervisor for the chosen user:
        data = {
            'chosen_user_id': user_id,
            'supervisor_id': session['user_id']
        }
        mysql = connectToMySQL('primeinventory$prime_inventory')
        chosen_user_query = "SELECT supervisor_id FROM users WHERE user_id = %(chosen_user_id)s;"
        chosen_user_supervisor_id = mysql.query_db(chosen_user_query, data)

        if chosen_user_supervisor_id[0]['supervisor_id'] == None:
            # Set the looged user as a supervisor for the choosen user:
            mysql = connectToMySQL('primeinventory$prime_inventory')
            add_user_to_my_team_query = """
                UPDATE users 
                SET supervisor_id = %(supervisor_id)s
                WHERE user_id = %(chosen_user_id)s
            """
            mysql.query_db(add_user_to_my_team_query, data)
            return redirect("/teams/my_team")
    return redirect("/sign_out")


# Render my_team page.
@app.route("/teams/my_team")
def render_my_team():
    checked_user = check_user_id()
    # If the logged in user is "Worker":
    if checked_user:
        if checked_user['user_job_title'] == "Worker":

            mysql = connectToMySQL('primeinventory$prime_inventory')
            # Retrieve the user's supervisor's information.
            supervisor_query = """SELECT u2.user_id, u2.first_name, u2.last_name, u2.job_title, u2.image_id
                            FROM users u1
                            JOIN users u2
                            ON u1.supervisor_id = u2.user_id
                            WHERE u1.user_id = %(user_id)s;"""
            data = {'user_id': session['user_id']}
            supervisor = mysql.query_db(supervisor_query, data)
            team=()
            if len(supervisor)>0:
                supervisor = supervisor[0]
                supervisor['job_title'] = replace_job_title(supervisor['job_title'])
                data['supervisor_id'] = supervisor['user_id']

                mysql = connectToMySQL('primeinventory$prime_inventory')
                # Retrieve the user's team data based on the user's supervisor's ID.
                team_query = """SELECT user_id, first_name, last_name, job_title, image_id
                                FROM users
                                WHERE supervisor_id = %(supervisor_id)s;"""
                team = mysql.query_db(team_query, data)
                if len(team)>0:
                    team = replace_job_title(team)
            return render_template("users/my_team.html", the_supervisor=supervisor, the_team=team, checked_user=checked_user)

        # If the logged in user is "Manager":
        elif checked_user['user_job_title'] == "Manager":
            mysql = connectToMySQL('primeinventory$prime_inventory')
            # Retrieve the user's team data based on the user's supervisor's ID.
            team_query = """SELECT user_id, first_name, last_name, job_title, image_id
                            FROM users
                            WHERE supervisor_id = %(user_id)s;"""
            data = {'user_id': session['user_id']}
            team = mysql.query_db(team_query, data)
            if len(team)>0:
                team = replace_job_title(team)
            supervisor = {
                "user_id":session['user_id'],
                "first_name": checked_user['user_first_name'],
                "last_name": checked_user['user_last_name'],
                "job_title": checked_user['user_job_title'],
                "image_id": checked_user['user_image_id']
            }
            return render_template("users/my_team.html", the_supervisor=supervisor, the_team=team, checked_user=checked_user)

        else:
            return redirect("/sign_out")
    return render_template("general/home_page.html", checked_user=checked_user)


# Remove the choosen user from the current user team (remove the logged user id from the supervisor_id data of the choosen user).
# This route is only for users who got a job_title of manager.
@app.route("/teams/remove_from_team/<user_id>")
def remove_user_from_my_team(user_id):
    checked_user = check_user_id()
    if checked_user['user_job_title'] == "Manager":
        # Check if the logged user is a supervisor for the chosen user:
        data = {
            'chosen_user_id': user_id,
            'supervisor_id': session['user_id']
        }
        mysql = connectToMySQL('primeinventory$prime_inventory')
        chosen_user_query = "SELECT supervisor_id FROM users WHERE user_id = %(chosen_user_id)s;"
        chosen_user_supervisor_id = mysql.query_db(chosen_user_query, data)

        if chosen_user_supervisor_id[0]['supervisor_id'] == session['user_id']:
            # Set the supervisor_id for the choosen user as NULL:
            mysql = connectToMySQL('primeinventory$prime_inventory')
            add_user_to_my_team_query = """
                UPDATE users 
                SET supervisor_id = NULL
                WHERE user_id = %(chosen_user_id)s
            """
            mysql.query_db(add_user_to_my_team_query, data)
            return redirect("/teams/my_team")
    return redirect("/sign_out")


# Render all_users page.
@app.route("/users")
def render_all_users_page():
    checked_user = check_user_id()
    if checked_user:
        return render_template("users/all_users.html", checked_user=checked_user)
    return redirect("/sign_out")

# AJAX route to load all users
@app.route("/load_users/all")
def load_all_users():
    checked_user = check_user_id()
    if checked_user:
        # Get all users from the database:
        mysql = connectToMySQL('primeinventory$prime_inventory')
        all_users_query = """
            SELECT user_id, first_name, last_name, image_id, job_title
            FROM users
            ORDER BY job_title, first_name;
        """
        all_users = mysql.query_db(all_users_query)
        if len(all_users) == 0:
            return jsonify(False)
        all_users = replace_job_title(all_users)
        return jsonify(all_users)
    return redirect("/sign_out")

# AJAX route to load managers
@app.route("/load_users/managers")
def load_managers():
    checked_user = check_user_id()
    if checked_user:
        # Get all users from the database:
        mysql = connectToMySQL('primeinventory$prime_inventory')
        managers_query = """
            SELECT user_id, first_name, last_name, image_id, job_title
            FROM users
            Where job_title = 2
            ORDER BY  first_name;
        """
        managers = mysql.query_db(managers_query)
        if len(managers) == 0:
            return jsonify(False)
        managers = replace_job_title(managers)
        return jsonify(managers)
    return redirect("/sign_out")

# AJAX route to load workers
@app.route("/load_users/workers")
def load_workers():
    checked_user = check_user_id()
    if checked_user:
        # Get all users from the database:
        mysql = connectToMySQL('primeinventory$prime_inventory')
        workers_query = """
            SELECT user_id, first_name, last_name, image_id, job_title
            FROM users
            Where job_title = 3
            ORDER BY  first_name;
        """
        workers = mysql.query_db(workers_query)
        if len(workers) == 0:
            return jsonify(False)
        workers = replace_job_title(workers)
        return jsonify(workers)
    return redirect("/sign_out")

# AJAX route to load new_workers (with no team/supervisor yet).
@app.route("/load_users/new_workers")
def load_new_workers():
    checked_user = check_user_id()
    if checked_user:
        # Get all users from the database:
        mysql = connectToMySQL('primeinventory$prime_inventory')
        new_workers_query = """
            SELECT user_id, first_name, last_name, image_id, job_title
            FROM users
            Where job_title = 3 AND supervisor_id IS NULL
            ORDER BY  first_name;
        """
        new_workers = mysql.query_db(new_workers_query)
        if len(new_workers) == 0:
            return jsonify(False)
        new_workers = replace_job_title(new_workers)
        return jsonify(new_workers)
    return redirect("/sign_out")


# Delete a user.
@app.route("/users/<user_id_url>/delete_user")
def delete_user(user_id_url):
    checked_user = check_user_id()
    # Prevent the Admin from deleting his own account.
    if checked_user['user_job_title'] == "Head Master" and int(user_id_url) == 1:
        return redirect("/sign_out")

    # Only the admin can delete any account & the user can delete his own account
    elif checked_user['user_job_title'] == "Head Master" or session['user_id'] == int(user_id_url):
        mysql = connectToMySQL('primeinventory$prime_inventory')
        # Delete the user's address from the 'adresses' table.
        delete_user_address_query = """
            DELETE FROM addresses
            WHERE user_id = %(user_id_from_URL)s
        """
        data = {'user_id_from_URL': user_id_url}
        mysql.query_db(delete_user_address_query, data)

        mysql = connectToMySQL('primeinventory$prime_inventory')
        # Delete the user from the 'users' table.
        delete_user_query = """
            DELETE FROM users 
            WHERE user_id = %(user_id_from_URL)s
        """
        data = {'user_id_from_URL': user_id_url}
        mysql.query_db(delete_user_query, data)

        if checked_user['user_job_title'] == "Head Master":
            return redirect("/users")
    return redirect("/sign_out")


# Proccess the signing out of the user and clearing the session
@app.route("/sign_out")
def signout():
    session.clear()
    return redirect("/")