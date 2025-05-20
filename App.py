# importing relevent 3rd party software.
from flask import Flask
app = Flask(__name__)

#Testing Home Route.
@app.route("/")
def Test_Route():
    return "Hello There"

# Used to run the app in debug mode this will be usful if error occur during devlopment.
if __name__ == "__main__":
    app.run(debug = True)

