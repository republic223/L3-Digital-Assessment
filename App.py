# importing relevent 3rd party software.
import sqlite3
from flask import Flask, g, render_template

# Varibles and constants below
app = Flask(__name__)
DATABASE = 'Movie_Data.db'

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
    sql = '''SELECT * FROM Shows_Display; '''
    results = query_db(sql)
    return render_template('Header.html', results=results)  

# Used to run the app in debug mode this will be usful if error occur during devlopment.
if __name__ == "__main__":
    app.run(debug = True)