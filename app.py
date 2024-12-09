# Import libraries
import os
import re

from cs50 import SQL
from flask import Flask, flash, redirect, render_template, request, session, url_for
from flask_session import Session
from werkzeug.security import check_password_hash, generate_password_hash

from helpers import apology, login_required, lookup, usd

# Configure application
app = Flask(__name__)

# Configure session to use filesystem (instead of signed cookies)
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# Initialize SQLite database
quote_db = SQL("sqlite:///quote.db")

# Ensure responses not cached
@app.after_request
def after_request(response):
    """Ensure responses aren't cached"""
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Expires"] = 0
    response.headers["Pragma"] = "no-cache"
    return response


# Homepage
@app.route("/")
@login_required
def index():
    # Find groups the user is in
    group_info = quote_db.execute("SELECT name,id FROM groups WHERE id IN (SELECT group_id FROM additions WHERE user_id = ? GROUP BY group_id HAVING SUM(value) > 0)", session["user_id"])
    
    # Find the username of the user
    name = {}
    name["user"] = quote_db.execute("SELECT username FROM users WHERE id = ?", session["user_id"])[0]
    
    # Index page
    return render_template("index.html", group_info = group_info, name = name)
   

# Group page
@app.route("/group/<int:group_id>")
@login_required
def group_page(group_id):
    '''
    Route to render a page specific to a group based on group_id
    '''
    # Fetch details about the specific group
    group_details = quote_db.execute("SELECT name,id FROM groups WHERE id = ?", group_id)[0]  # Assuming each group_id is unique and fetches one row
    quotes = quote_db.execute("SELECT id, quote_text, quote_author, location, likes FROM quotes WHERE group_id = ?", group_id)
    like_info = quote_db.execute("SELECT id FROM quotes WHERE id IN (SELECT quote_id FROM likes WHERE user_id = ? GROUP BY quote_id HAVING SUM(like_value) > 0)", session["user_id"])

    
    # Render a group-specific template
    return render_template("group.html", group=group_details, quotes = quotes, like_info = like_info)


# Add quote
@app.route("/group/<int:group_id>/add_quote", methods=["POST"])
@login_required
def add_quote(group_id):
    '''
    Route to handle adding a quote to the group
    '''
    # Get data from the form
    quote_content = request.form.get("quote")
    quote_author = request.form.get("author")
    quote_location = request.form.get("location")

    # Validate input
    if not quote_content:
        return apology("please provide text for your new quote", 403)
    elif not quote_author:
        return apology("plase provide a name for the person who said your quote", 403)
    
    
    # Insert the new quote into the database
    quote_db.execute(
        "INSERT INTO quotes (group_id, quote_text, quote_author, location) VALUES (?, ?, ?, ?)",
        group_id, quote_content, quote_author, quote_location
    )
    
    # Redirect back to the group page
    return redirect(url_for("group_page", group_id=group_id))


# Like quote
@app.route("/group/<int:group_id>/like_quote/<int:quote_id>", methods=["POST"])
@login_required
def like_quote(group_id, quote_id):
    # Check if user has liked quote
    user_like = quote_db.execute("SELECT quote_id FROM likes WHERE user_id = ? GROUP BY quote_id HAVING SUM(like_value) > 0 AND quote_id = ?", session["user_id"], quote_id)

    # If not liked, like; else, unlike
    if (len(user_like)) == 0:
        quote_db.execute("INSERT INTO likes (user_id, quote_id, like_value) VALUES (?,?,?)", session["user_id"], quote_id, 1)
        quote_db.execute("UPDATE quotes SET likes = likes + 1 WHERE id = ?", quote_id)
    else:
        quote_db.execute("INSERT INTO likes (user_id, quote_id, like_value) VALUES (?,?,?)", session["user_id"], quote_id, -1)
        quote_db.execute("UPDATE quotes SET likes = likes - 1 WHERE id = ?", quote_id)
    
    return redirect(url_for("group_page", group_id=group_id))


# Join group
@app.route("/join", methods = ["GET","POST"])
@login_required
def join():
    if request.method == "POST":
        # Validate input
        if not request.form.get("groupname"):
            return apology("please provide a group name you want to join", 403)
        elif not request.form.get("password"):
            return apology("please provide a password for the group you want to join", 403)
        
        # Check if group exists & password is correct
        group_rows = quote_db.execute("SELECT * FROM groups WHERE name = ?", request.form.get("groupname"))
        if len(group_rows) != 1 or not check_password_hash(
            group_rows[0]["group_hash"], request.form.get("password")
        ):
            return apology("invalid group name and/or password", 403)
        
        # Check if user is already in the group
        group_info = quote_db.execute("SELECT name,id FROM groups WHERE id IN (SELECT group_id FROM additions WHERE user_id = ? GROUP BY group_id HAVING SUM(value) > 0) AND name = ?", session["user_id"], request.form.get("groupname"))

        if (len(group_info)) != 0:
            return apology("you have already joined this group, you can't join it again")

        # Add user to group
        quote_db.execute("INSERT INTO additions (user_id, group_id, value) VALUES (?,?,?)", session["user_id"], group_rows[0]["id"], 1) #1 indicates joining the group

        # Redirect user to home page
        return redirect("/")
    else:
        return render_template("join.html")


# Create group
@app.route("/create", methods = ["GET", "POST"])
@login_required
def create():
    if request.method == "POST":
        # Get form data
        groupname = request.form.get("groupname")
        password = request.form.get("password")
        confirmation = request.form.get("pass_confirmation")

        # Validate input
        if not groupname:
            return apology ("please submit a name for your group", 403)
        
        elif not password:
            return apology ("please submit a password to help others join your group", 403)
        
        elif not (bool(re.search(r'\w', groupname))):
            return apology ("please submit a valid name for your group", 403)
        
        elif not (bool(re.search(r'\w', password))):
            return apology ("please submit a valid password for your group", 403)
        
        elif (confirmation != password):
            return apology ("password and password confirmation do not match", 403)
        
        # Hash password
        pass_hash = generate_password_hash(password)
        
        # Check if group name is taken
        group_rows = quote_db.execute("SELECT * FROM groups WHERE name = ?", groupname)
        if len(group_rows) != 0:
            return apology("group name already taken", 403)
        
        # Insert new group into database
        quote_db.execute("INSERT INTO groups (name, group_hash) VALUES (?,?)", groupname, pass_hash)

        # Redirect to homepage
        return redirect("/")

    else:
        # Render group creation page
        return render_template("create.html")


# Leave group
@app.route("/leave", methods = ["GET", "POST"])
@login_required
def leave():
    if request.method == "POST":
        # Get form data
        groupname = request.form.get("groupname")

        # Validate input
        if not groupname:
            return apology("please select a group name you want to leave", 403)
        
        # Check if group exists
        group_rows = quote_db.execute("SELECT * FROM groups WHERE name = ?", groupname)
        if len(group_rows) != 1:
            return apology("invalid group name selected, somehow?", 403)

        # Check if user in group
        group_info = quote_db.execute("SELECT name,id FROM groups WHERE id IN (SELECT group_id FROM additions WHERE user_id = ? GROUP BY group_id HAVING SUM(value) > 0) AND name = ?", session["user_id"], request.form.get("groupname"))

        if (len(group_info)) == 0:
            return apology("you are already not in this group, so you can't leave it")

        # Update database to reflect user leaving group
        quote_db.execute("INSERT INTO additions (user_id, group_id, value) VALUES (?,?,?)", session["user_id"], group_rows[0]["id"], -1) #-1 indicates leaving the group

        # Redirect user to home page
        return redirect("/")
    else:
        # Render leave group page
        return render_template("leave.html")


# Login
@app.route("/login", methods=["GET", "POST"])
def login():
    # Forget any user_id
    session.clear()
    print("In Login Page Now")

    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":
        # Validate input
        if not request.form.get("username"):
            return apology("must provide username", 403)
        
        elif not request.form.get("password"):
            return apology("must provide password", 403)
        
        # Query database for username
        user_rows = quote_db.execute("SELECT * FROM users WHERE username = ?", request.form.get("username"))

        # Ensure username exists and password is correct
        if len(user_rows) != 1 or not check_password_hash(
            user_rows[0]["pass_hash"], request.form.get("password")
        ):
            return apology("invalid username and/or password", 403)
        
        # Remember which user has logged in
        session["user_id"] = user_rows[0]["id"]

        # Redirect user to home page
        return redirect("/")    
    else:
        # Render login page
        return render_template("login.html")
    

# Logout
@app.route("/logout")
def logout():
    """Log user out"""

    # Forget any user_id
    session.clear()

    # Redirect user to login form
    return redirect("/")


# Register
@app.route("/register", methods=["GET", "POST"])
def register():
    """Register user"""
    if request.method == "POST":
        # Get form data
        username = request.form.get("username")
        password = request.form.get("password")
        
        # Ensure username was submitted
        if not username:
            return apology("must provide username", 400)

        # Ensure password was submitted
        elif not password:
            return apology("must provide password", 400)

        elif not request.form.get("confirmation"):
            return apology("must confirm password", 400)

        elif password != request.form.get("confirmation"):
            return apology("password and password confirm must match", 400)

        # Hash password
        password_hash = generate_password_hash(password)

        # Insert new user into database
        try:
            quote_db.execute("INSERT INTO users (username, pass_hash) VALUES(?, ?)", username, password_hash)
        except:
            # Return apology if username taken
            return apology("username already exists", 400)
        # Redirect to homepage
        return redirect("/")
    
    # Render registration
    return render_template("register.html")