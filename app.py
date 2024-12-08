import os
import re

from cs50 import SQL
from flask import Flask, flash, redirect, render_template, request, session, url_for
from flask_session import Session
from werkzeug.security import check_password_hash, generate_password_hash

from helpers import apology, login_required, lookup, usd

# Configure application
app = Flask(__name__)

# Custom filter
app.jinja_env.filters["usd"] = usd

# Configure session to use filesystem (instead of signed cookies)
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# Configure CS50 Library to use SQLite database
db = SQL("sqlite:///finance.db")
quote_db = SQL("sqlite:///quote.db")

@app.after_request
def after_request(response):
    """Ensure responses aren't cached"""
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Expires"] = 0
    response.headers["Pragma"] = "no-cache"
    return response


@app.route("/")
@login_required
def index():
    group_info = quote_db.execute("SELECT name,id FROM groups WHERE id IN (SELECT group_id FROM additions WHERE user_id = ? GROUP BY group_id HAVING SUM(value) > 0)", session["user_id"])
    
    name = {}
    name["user"] = quote_db.execute("SELECT username FROM users WHERE id = ?", session["user_id"])[0]
    
    return render_template("index.html", group_info = group_info, name = name)
   

@app.route("/group/<int:group_id>")
@login_required
def group_page(group_id):
    '''
    Route to render a page specific to a group based on group_id
    '''
    # Fetch details about the specific group
    group_details = quote_db.execute("SELECT name,id FROM groups WHERE id = ?", group_id)[0]  # Assuming each group_id is unique and fetches one row
    quotes = quote_db.execute("SELECT quote_text, quote_author, location FROM quotes WHERE group_id = ?", group_id)
    # Render a group-specific template
    return render_template("group.html", group=group_details, quotes = quotes)

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

'''
@app.route("/buy", methods=["GET", "POST"])
@login_required
def buy():
    if request.method == "POST":
        symbol = request.form.get("symbol")
        shares = request.form.get("shares")

        try:
            shares = float(shares)
        except ValueError:
            return apology("number of shares must be numeric", 400)

        if not symbol:
            return apology("must provide symbol", 400)
        if not lookup(symbol):
            return apology("symbold does not exist", 400)
        if not shares.is_integer():
            return apology("number of shares must be a whole number", 400)
        if shares <= 0:
            return apology("number of shares are not valid", 400)

        user_cash = db.execute("SELECT cash FROM users WHERE id = ?", session["user_id"])[0]["cash"]
        buy_price = (lookup(symbol)["price"] * int(shares))

        if (buy_price > user_cash):
            return apology("Insufficient funds", 400)

        db.execute("INSERT INTO transactions (user_id, symbol, shares, price) VALUES(?, ?, ?, ?)",
                   session["user_id"], symbol, shares, lookup(symbol)["price"])
        db.execute("UPDATE users SET cash = ? WHERE id = ?",
                   # I use user_id to differentiate between different people's accounts
                   user_cash - buy_price, session["user_id"])
        return redirect("/")

    return render_template("buy.html")


@app.route("/request_cash", methods=["POST"])
@login_required
def request_cash():
    """Handle requesting more cash."""
    # Get the amount of cash requested from the form
    amount = request.form.get("amount")

    # Validate the amount
    if not amount or not amount.isdigit():
        return apology("amount must be a valid positive number", 400)

    amount = int(amount)
    if amount <= 0:
        return apology("amount must be greater than zero", 400)

    # Update the user's cash balance in the database
    current_cash = db.execute("SELECT cash FROM users WHERE id = ?", session["user_id"])[0]["cash"]
    db.execute("UPDATE users SET cash = ? WHERE id = ?", current_cash + amount, session["user_id"])

    # Redirect to the homepage or another page
    return redirect("/")
'''



@app.route("/join", methods = ["GET","POST"])
@login_required
def join():
    if request.method == "POST":
        if not request.form.get("groupname"):
            return apology("please provide a group name you want to join", 403)
        
        elif not request.form.get("password"):
            return apology("please provide a password for the group you want to join", 403)
        
        group_rows = quote_db.execute("SELECT * FROM groups WHERE name = ?", request.form.get("groupname"))
        if len(group_rows) != 1 or not check_password_hash(
            group_rows[0]["group_hash"], request.form.get("password")
        ):
            return apology("invalid group name and/or password", 403)
        
        quote_db.execute("INSERT INTO additions (user_id, group_id, value) VALUES (?,?,?)", session["user_id"], group_rows[0]["id"], 1) #1 indicates joining the group

        # Redirect user to home page
        return redirect("/")
    else:
        return render_template("join.html")




@app.route("/create", methods = ["GET", "POST"])
@login_required
def create():
    if request.method == "POST":
        groupname = request.form.get("groupname")
        password = request.form.get("password")
        confirmation = request.form.get("pass_confirmation")
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
        
        pass_hash = generate_password_hash(password)
        group_rows = quote_db.execute("SELECT * FROM groups WHERE name = ?", groupname)
        if len(group_rows) != 0:
            return apology("group name already taken", 403)
        
        quote_db.execute("INSERT INTO groups (name, group_hash) VALUES (?,?)", groupname, pass_hash)

        return redirect("/")

    else:
        return render_template("create.html")






@app.route("/leave", methods = ["GET", "POST"])
@login_required
def leave():
    if request.method == "POST":
        groupname = request.form.get("groupname")

        if not groupname:
            return apology("please select a group name you want to leave", 403)
         
        group_rows = quote_db.execute("SELECT * FROM groups WHERE name = ?", groupname)
        if len(group_rows) != 1:
            return apology("invalid group name selected, somehow?", 403)
        
        quote_db.execute("INSERT INTO additions (user_id, group_id, value) VALUES (?,?,?)", session["user_id"], group_rows[0]["id"], -1) #-1 indicates leaving the group

        # Redirect user to home page
        return redirect("/")
    else:
        return render_template("leave.html")


'''
@app.route("/history")
@login_required
def history():
    """Show history of transactions"""

    # Very simple as I configured my transactions database for this history task
    transactions = db.execute("SELECT * FROM transactions WHERE user_id = ?", session["user_id"])
    return render_template("history.html", transactions=transactions)

'''

@app.route("/login", methods=["GET", "POST"])
def login():
    # Forget any user_id
    session.clear()
    print("In Login Page Now")
    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":
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
        return render_template("login.html")
    
    '''
    if request.method == "POST":
        # Ensure username was submitted
        if not request.form.get("username"):
            return apology("must provide username", 403)

        # Ensure password was submitted
        elif not request.form.get("password"):
            return apology("must provide password", 403)

        # Query database for username
        rows = db.execute(
            "SELECT * FROM users WHERE username = ?", request.form.get("username")
        )

        # Ensure username exists and password is correct
        if len(rows) != 1 or not check_password_hash(
            rows[0]["hash"], request.form.get("password")
        ):
            return apology("invalid username and/or password", 403)

        # Remember which user has logged in
        session["user_id"] = rows[0]["id"]

        # Redirect user to home page
        return redirect("/")

        # User reached route via GET (as by clicking a link or via redirect)
    else:
        return render_template("login.html")
    '''

@app.route("/logout")
def logout():
    """Log user out"""

    # Forget any user_id
    session.clear()

    # Redirect user to login form
    return redirect("/")


'''
@app.route("/quote", methods=["GET", "POST"])
@login_required
def quote():
    """Get stock quote."""
    if request.method == "POST":
        symbol = request.form.get("symbol")
        if not symbol:
            return apology("missing symbol", 400)
        if not lookup(symbol):
            return apology("symbol does not exist", 400)
        else:
            return render_template("quoted.html", info=lookup(symbol))
    return render_template("quote.html")

'''

@app.route("/register", methods=["GET", "POST"])
def register():
    """Register user"""
    if request.method == "POST":
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

        password_hash = generate_password_hash(password)

        try:
            quote_db.execute("INSERT INTO users (username, pass_hash) VALUES(?, ?)", username, password_hash)
        except:
            return apology("username already exists", 400)
        return redirect("/")
    
    return render_template("register.html")
    '''


    if request.method == "POST":
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

        password_hash = generate_password_hash(password)

        try:
            db.execute("INSERT INTO users (username, hash) VALUES(?, ?)", username, password_hash)
        except:
            return apology("username already exists", 400)
        return redirect("/")

    return render_template("register.html")
    '''


'''

@app.route("/sell", methods=["GET", "POST"])
@login_required
def sell():
    """Sell shares of stock"""
    if request.method == 'POST':
        symbol = request.form.get("symbol")
        shares = request.form.get("shares")
        try:
            shares = float(shares)
        except ValueError:
            return apology("number of shares must be numeric", 400)

        if not symbol:
            return apology("must select stock to sell", 400)
        if not shares:
            return apology("you must select a number of shares to sell", 400)
        if not shares.is_integer():
            return apology("you must select a whole number of shares to sell", 400)
        if shares <= 0:
            return apology("you must select a number of shares to sell", 400)

        info = db.execute(
            "SELECT symbol, SUM(shares) AS total_shares FROM transactions WHERE user_id = ? GROUP BY symbol HAVING SUM(shares) > 0", session["user_id"])
        contains = False
        num_shares = 0
        for stock in info:
            if symbol == stock["symbol"]:
                contains = True
                num_shares = stock["total_shares"]

        if (not contains):
            return apology("you do not have that stock in your possesion", 400)
        if (num_shares == 0):
            return apology("by some miracle, you are trying to sell a stock you have 0 shares of", 400)
        if (num_shares < int(shares)):
            return apology("you do not have that many shares in your possession", 400)

        user_cash = db.execute("SELECT cash FROM users WHERE id = ?", session["user_id"])[0]["cash"]
        sell_price = (lookup(symbol)["price"] * int(shares))

        db.execute("INSERT INTO transactions (user_id, symbol, shares, price) VALUES(?, ?, ?, ?)",
                   # Selling is just like reverse buying in my code.
                   session["user_id"], symbol, (int(shares)) * -1, lookup(symbol)["price"])
        db.execute("UPDATE users SET cash = ? WHERE id = ?",
                   user_cash + sell_price, session["user_id"])
        return redirect("/")

    info = db.execute(
        "SELECT symbol, SUM(shares) AS total_shares FROM transactions WHERE user_id = ? GROUP BY symbol HAVING SUM(shares) > 0", session["user_id"])
    # I use jinja to make dynamic webpages, here I pass in info for the dynamic sell page (changes the values in the dropdown menu)
    return render_template("sell.html", info=info)
'''