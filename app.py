from flask import Flask
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = "mysql://root:Root-123@localhost/xerox"
app.config["SQLALCHEMY_TRACK_NOTIFICATIONS"] = False

db =SQLAlchemy(app)

print("done..")

class user(db.Model):
    id = db.Column(db.Integer, primary_key = True)
    name = db.Column(db.String(50))
    email = db.Column(db.String(50), unique=True)

    def __repr__(self):
        return f'<User: {self.name}>'


with app.app_context():
    print(user.query.all())