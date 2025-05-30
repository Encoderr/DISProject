from flask import Flask
from controllers import songs
from database import init_db

init_db()

app = Flask(__name__)

@app.route("/")
def hello_world():
    return "<p>Hello, World!</p>"

app.register_blueprint(songs.bp)

