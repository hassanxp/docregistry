import os

from flask import Flask
from flask import render_template
from flask import request
from flask import redirect
from flask_sqlalchemy import SQLAlchemy
import datetime


project_dir = os.path.dirname(os.path.abspath(__file__))
database_file = "sqlite:///{}".format(os.path.join(project_dir, "docdatabase.db"))

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = database_file

db = SQLAlchemy(app)


class Doc(db.Model):
    id = db.Column(db.String(80), unique=True, nullable=False, primary_key=True)
    title = db.Column(db.String(80), unique=True, nullable=False, primary_key=False)
    author = db.Column(db.String(80), unique=False, nullable=False, primary_key=False)
    date = db.Column(db.String(80), unique=False, nullable=False, primary_key=False)

    def __repr__(self):
        return "<Id: {}, Title: {}, Author: {}, Date: {}>".format(self.id, self.title, self.author, self.date)


@app.route("/", methods=["GET", "POST"])
def home():
    if request.form:
        now = datetime.datetime.now()
        book = Doc(id=request.form.get("id"), title=request.form.get("title"), author=request.form.get("author"), date=now.isoformat())
        db.session.add(book)
        db.session.commit()
    books = Doc.query.all()
    return render_template("home.html", books=books)

@app.route("/update", methods=["POST"])
def update():
    newtitle = request.form.get("newtitle")
    newauthor = request.form.get("newauthor")
    sid = request.form.get("id")
    book = Doc.query.filter_by(id=sid).first()
    book.title = newtitle
    book.author = newauthor
    db.session.commit()
    return redirect("/")

@app.route("/delete", methods=["POST"])
def delete():
    sid = request.form.get("id")
    book = Doc.query.filter_by(id=sid).first()
    db.session.delete(book)
    db.session.commit()
    return redirect("/")

if __name__ == "__main__":
    app.run(debug=True)