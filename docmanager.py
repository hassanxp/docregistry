import os

from flask import Flask
from flask import render_template
from flask import request
from flask import redirect
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import exists
import datetime
from typing import List

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

        # Check that id and title are unique
        identifier = request.form.get("id")
        title = request.form.get("title")
        warnings=[]
        checkId(identifier, warnings)
        checkTitle(title, warnings)
        if warnings:
            docs = Doc.query.all()
            return render_template("home.html", warnings=warnings, docs=docs)

        doc = Doc(id=identifier, title=title, author=request.form.get("author"), date=now.isoformat())
        db.session.add(doc)
        db.session.commit()

    docs = Doc.query.all()
    return render_template("home.html", docs=docs)

@app.route("/update", methods=["POST"])
def update():
    newtitle = request.form.get("newtitle")
    warnings = []
    checkTitle(newtitle, warnings)
    if warnings:
        docs = Doc.query.all()
        return render_template("home.html", warnings=warnings, docs=docs)

    newauthor = request.form.get("newauthor")
    sid = request.form.get("id")
    doc = Doc.query.filter_by(id=sid).first()
    doc.title = newtitle
    doc.author = newauthor
    db.session.commit()
    return redirect("/")

@app.route("/delete", methods=["POST"])
def delete():
    sid = request.form.get("id")
    doc = Doc.query.filter_by(id=sid).first()
    db.session.delete(doc)
    db.session.commit()
    return redirect("/")


def checkId(identifier:str, warnings: List[str]):
    # https://stackoverflow.com/questions/32938475/flask-sqlalchemy-check-if-row-exists-in-table/42920524
    exists = db.session.query(db.exists().where(Doc.id == identifier)).scalar()
    if exists:
        warnings.append("Id: {} already exists".format(identifier))
    return

def checkTitle(title:str, warnings: List[str]):
    exists = db.session.query(db.exists().where(Doc.title == title)).scalar()
    if exists:
        warnings.append("Title: {} already exists".format(title))
    return

if __name__ == "__main__":
    app.run(debug=True)
