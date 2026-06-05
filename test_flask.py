from flask import Flask, render_template
import datetime

app = Flask(__name__)

@app.route("/")
def hello_world():
    data = datetime.datetime.today()
    return render_template("hello.html", data = data )

if __name__ == '__main__':
    app.run()