# importing relevent 3rd party software.
import sqlite3
from flask import Flask, g, render_template, request, flash, session, redirect
from werkzeug.security import generate_password_hash, check_password_hash

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
def query_db(query, args=(), one=False, commit=False):
    db = get_db()
    cur = db.cursor()
    cur.execute(query, args)
    # added to ensure results commit to the database
    if commit:
        db.commit()
    rv =cur.fetchall()    
    cur.close()
    return (rv[0] if rv else None) if one else rv 

# Error code Handlers go here
@app.errorhandler(404)
def Page_Not_Found(error):
    return render_template('404.html')

@app.errorhandler(500)
def Server_error(error):
    return render_template('500.html')

@app.errorhandler(505)
def HTTP_version_incorrect(error):
    render_template('505.html')

# Used to develop the error pages only temporary will be removed 
@app.route("/1")
def error_page():
    return render_template('505.html')

#Testing Home Route.
@app.route("/")
def Test_Route():
    sql = '''SELECT show_id, title, Year, Rating_image, Poster_image, Rating
FROM Shows_display
JOIN Age_rating ON Shows_display.Rating_id = Age_Rating.Rating_id
ORDER BY title ASC; '''
    results = query_db(sql)
    return render_template('Home.html', results=results)

# Show page route
@app.route("/Show_page/<int:Show_id>")
def Show_page(Show_id):
    sql = '''SELECT Shows_display.Show_id, title, 
GROUP_CONCAT(DISTINCT Director.Directors) AS Directors,
GROUP_CONCAT(DISTINCT Country.Country ) AS Country,
GROUP_CONCAT(DISTINCT Genre.Genre) AS Genre, 
actors, Date_added, Year, Rating_image, Duration, Description, Poster_image, Director.Director_id, Country.Country_id, Genre.Genre_id, Rating
FROM Shows_display
JOIN Age_rating ON Shows_Display.Rating_id = Age_Rating.Rating_id
left JOIN Show_Director ON Shows_Display.Show_id = Show_Director.Show_id
left JOIN Director on Show_director.Director_id = Director.Director_id
left JOIN Show_Country ON Shows_Display.Show_id = Show_Country.Show_id
left JOIN Country on Show_Country.Country_id = Country.Country_id
left JOIN Show_Genre ON Shows_Display.Show_id = Show_Genre.Show_id
left JOIN Genre on Show_Genre.Genre_id = Genre.Genre_id
WHERE Shows_display.Show_id = ?;'''
    results = query_db(sql, args=(Show_id,), one=False)
    return render_template('Show_page.html', results = results) 

#TV Shows route
@app.route("/TV_Shows")
def TV_Route():
    sql = '''SELECT show_id, title, Year, Rating_image, Poster_image, Rating, Type
FROM Shows_display
JOIN Age_rating ON Shows_display.Rating_id = Age_Rating.Rating_id
JOIN Movie_types ON Shows_display.Type_id = Movie_types.Type_id
WHERE Shows_display.Type_id = 2
ORDER BY title ASC; ''' 
    results = query_db(sql)
    return render_template('TV_Show.html', results= results)

#Movies route
@app.route("/Movies")
def Movie_Route():
    sql = '''SELECT show_id, title, Year, Rating_image, Poster_image, Rating, Type
FROM Shows_display
JOIN Age_rating ON Shows_display.Rating_id = Age_Rating.Rating_id
JOIN Movie_types ON Shows_display.Type_id = Movie_types.Type_id
WHERE Shows_display.Type_id = 1
ORDER BY title ASC; ''' 
    results = query_db(sql)
    return render_template('Movie.html', results= results)

# Director_Select route
@app.route('/Director_Select')
def Director_Select():
    sql = '''SELECT Directors, Director_id FROM Director
    ORDER BY Directors ASC;'''
    results = query_db(sql)
    return render_template('Director_Select.html', results = results)

#Directors movies route
@app.route('/Director/<int:Director_id>')
def Director_Movies(Director_id):
    sql = '''SELECT Shows_display.Show_id, title, Year, Rating_image, Poster_image, Rating, Director.Directors
FROM Shows_display
JOIN Age_rating ON Shows_Display.Rating_id = Age_Rating.Rating_id
JOIN Show_Director ON Shows_Display.Show_id = Show_Director.Show_id
JOIN Director on Show_director.Director_id = Director.Director_id
WHERE Show_Director.Director_id = ?
; '''
    results = query_db(sql, args=(Director_id,), one= False)
    return render_template('Selection.html', results = results)

# Country_Select route
@app.route('/Country_Select')
def Country_Select():
    sql= '''SELECT Country, Country_id FROM Country
            ORDER BY Country ASC;'''
    results = query_db(sql)
    return render_template('Country_Select.html', results = results)

#Countries movies route
@app.route('/Country/<int:Country_id>')
def Country_Movies(Country_id):
    sql = '''SELECT Shows_display.Show_id, title, Year, Rating_image, Poster_image, Rating, Country.Country
FROM Shows_display
JOIN Age_rating ON Shows_Display.Rating_id = Age_Rating.Rating_id
JOIN Show_Country ON Shows_Display.Show_id = Show_Country.Show_id
JOIN Country on Show_Country.Country_id = Country.Country_id
WHERE Show_Country.Country_id = ?; '''
    results = query_db(sql, args=(Country_id,), one= False)
    return render_template('Selection.html', results = results)

# Genre_Select route
@app.route('/Genre_Select')
def Genre_Select():
    sql = '''SELECT Genre, Genre_id FROM Genre
    ORDER BY Genre ASC;'''
    results = query_db(sql)
    return render_template('Genre_Select.html', results = results)

#Countries movies route
@app.route('/Genre/<int:Genre_id>')
def Genre_Movies(Genre_id):
    sql = '''SELECT Shows_display.Show_id, title, Year, Rating_image, Poster_image, Rating, Genre.Genre
FROM Shows_display
JOIN Age_rating ON Shows_Display.Rating_id = Age_Rating.Rating_id
JOIN Show_Genre ON Shows_Display.Show_id = Show_Genre.Show_id
JOIN Genre on Show_Genre.Genre_id = Genre.Genre_id
WHERE Show_Genre.Genre_id = ?; '''
    results = query_db(sql, args=(Genre_id,), one= False)
    return render_template('Selection.html', results = results)

#Copyright Disclaimer route
@app.route("/Copyright_Disclaimer")
def Copyright_Disclaimer():
    return render_template('Copyright.html')

# About page route
@app.route("/About")
def About():
    return render_template("About.html")

# Issues route
@app.route("/Issues", methods=["GET","POST"])
def Issues():
    if request.method == "POST":
        Issue = request.form["Issue"]
        User = session['username']
        sql = '''INSERT INTO Issues (Issue, User_id) VALUES (?,?)'''
        query_db(sql, args=(Issue, User,), commit=True)   
    
    sql = ''' Select User_data.Username, Issue 
            FROM Issues
            Join User_data ON Issues.User_id = User_data.User_id; '''
    results = query_db(sql)
    return render_template("Issues.html", results = results)

# Sign Up route
@app.route('/Sign_up', methods=["GET","POST"])
def Sign_up():
    if request.method == "POST":
        Username = request.form['username']
        password0 = request.form['password0']
        password1 = request.form['password1']
        # check to see if passwords match
        if password0 == password1:
            Hash_Password = generate_password_hash(password0)
            sql = '''INSERT INTO User_Data (Username,Password) VALUES (?,?)'''
            query_db(sql, args=(Username, Hash_Password,), commit=True)
            flash("Sign up successful")
            return redirect('/Check_Number',)
        else:
            flash("Please ensure both Passwords match")
    return render_template('Sign_up.html')

# Check Number Route
@app.route('/Check_Number')
def Check_number():
    # Check Number at the momment is the Max Value of the user ID so they can be uniquly identified
    # will need to be improved on if users want to delete data
    sql = '''Select MAX(User_ID) FROM User_Data;'''
    results = query_db(sql)
    return render_template('Check_Num.html', results=results)

#Log in route
@app.route('/Login', methods=["GET","POST"])
def login():
    if request.method=="POST":
        # find username and password
        username = request.form['username']
        password = request.form['password']
        Check_Num = request.form['Check_Num']
        sql = '''SELECT User_id, Username, Password FROM User_Data WHERE Username = ?; '''
        user = query_db(sql, args=(username,), one=True)
        # need to use User_id to keep the use of the same username for two users
        if user:
            # if user found program will check the Password
            if int(Check_Num) == user[0]:
                if check_password_hash(password=password, pwhash=user[2]):
                    session['username'] = user[0]
                    flash("Logged In")
                # if password does not match program will flash password incorrect
                else:
                    flash("Password incorrect")
            # if check number incorrect program will let user know
            else:
               flash("Check Number Incorrect")      
        # if username not found program will let user know
        else:
            flash("Username does not exist")
    return render_template('Login.html')

# sign out route
@app.route("/Sign_out")
def Sign_out():
    # clears session and returns user to the homepage
    session['username'] = None
    return redirect('/')
    

# Used to run the app in debug mode this will be usful if error occur during devlopment.
if __name__ == "__main__":
    app.run(debug = True)