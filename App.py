# importing relevent 3rd party software.
import sqlite3
from flask import Flask, g, render_template, request, flash, session, redirect

# Varibles and constants below
app = Flask(__name__)
DATABASE = 'Movie_Data.db'

# Needed secret key for session to work will make proper key later
app.config['SECRET_KEY'] = 'cheese'

#Conecting Movie_Data.db to program. 
def get_db():
    db = getattr(g, '_database', None)
    if db is None:
        db = g._database = sqlite3.connect(DATABASE)
    return db

# Closes database after shutdown of server
@app.teardown_appcontext
def close_connection(exception):
    db = getattr(g, '_database', None)
    if db is not None:
        db.close()

# Function to make querying the database simple.
def query_db(query, args=(), one=False):
    cur = get_db().execute(query, args)
    rv = cur.fetchall()
    cur.close()
    return (rv[0] if rv else None) if one else rv 

#Testing Home Route.
@app.route("/")
def Test_Route():
    sql = '''SELECT show_id, title, Year, Rating, Poster_image
FROM Shows_display
JOIN Age_rating ON Shows_display.Rating_id = Age_Rating.Rating_id; '''
    results = query_db(sql)
    return render_template('Main.html', results=results) 

#TV Shows route
@app.route("/TV_Shows")
def TV_Route():
    sql = '''SELECT show_id, title, Year, Rating, Poster_image
FROM Shows_display
JOIN Age_rating ON Shows_display.Rating_id = Age_Rating.Rating_id
WHERE Shows_display.Type_id = 2; ''' 
    results = query_db(sql)
    return render_template('Main.html', results= results)

#Movies route
@app.route("/Movies")
def Movie_Route():
    sql = '''SELECT show_id, title, Year, Rating, Poster_image
FROM Shows_display
JOIN Age_rating ON Shows_display.Rating_id = Age_Rating.Rating_id
WHERE Shows_display.Type_id = 1; ''' 
    results = query_db(sql)
    return render_template('Main.html', results= results)

# Director_Select route
@app.route('/Director_Select')
def Director_Select():
    sql = '''SELECT Directors, Director_id FROM Director;'''
    results = query_db(sql)
    return render_template('Selection.html', results = results)

#Directors movies route
@app.route('/Director/<int:Director_id>')
def Director_Movies(Director_id):
    sql = '''SELECT Shows_display.Show_id, title, Year, Rating, Poster_image
FROM Shows_display
JOIN Age_rating ON Shows_Display.Rating_id = Age_Rating.Rating_id
JOIN Show_Director ON Shows_Display.Show_id = Show_Director.Show_id
JOIN Director on Show_director.Director_id = Director.Director_id
WHERE Show_Director.Director_id = ?; '''
    results = query_db(sql, args=(Director_id,), one= False)
    return render_template('Main.html', results = results)

#Log in route
@app.route('/Login', methods=["GET","POST"])
def login():
    if request.method=="POST":
        # find username and password
        username = request.form['username']
        password = request.form['password']
        sql = '''SELECT User_id, Username, Password FROM User_Data WHERE Username = ?; '''
        user = query_db(sql, args=(username,), one=True)
        pword = query_db(sql, args=(password,), one=True)
        # need to use User_id to keep the use of the same username for two users
        if user:
            # if user found program will check the Password
            if pword:
                session['username'] = user
                flash("Logged In")
            else:
                flash("Password incorrect")
        else:
            flash("Username does not exist")
    return render_template('Login.html')

# Used to run the app in debug mode this will be usful if error occur during devlopment.
if __name__ == "__main__":
    app.run(debug = True)