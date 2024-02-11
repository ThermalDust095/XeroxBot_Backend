from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from markupsafe import escape
from flask import request
import json 


app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = "mysql://root:Root-123@localhost/xerox"
app.config["SQLALCHEMY_TRACK_NOTIFICATIONS"] = False

db =SQLAlchemy(app)

class User(db.Model):
    id = db.Column(db.Integer, primary_key = True)
    name = db.Column(db.String(20))
    usn = db.Column(db.String(20), unique=True)
    orders = db.relationship('Orders', backref="user")
    
    def __repr__(self):
        return f'<User id={self.id} name={self.name}>'

class Orders(db.Model):
    id = db.Column(db.Integer, primary_key = True)
    order_status = db.Column(db.String(10))
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    files = db.relationship('Files', backref = "orders")

    def __repr__(self):
        return f'<Order id={self.id} status={self.order_status}>'    

class Files(db.Model):
    id = db.Column(db.Integer, primary_key = True)
    file_path = db.Column(db.String(20))
    file_type = db.Column(db.String(15))
    desc = db.Column(db.String(100))
    order_id = db.Column(db.Integer, db.ForeignKey('orders.id'))

    def __repr__(self):
        return f'<File id={self.id} path={self.file_path}>'


with app.app_context():
    db.create_all()

@app.route('/')
def hello():
    return 'hello'

@app.route('/user/<username>')
def show_queries(username):
    data = {}
    user = User.query.filter_by(name=username).first()

    data["id"] = user.id
    data["name"] = user.name
    data["usn"] = user.usn

    return data


@app.route('/post-user', methods=['POST'])
def post_user():
    
    if request.method == "POST":
        data = json.loads(request.data)
        print(data)

        user = User(name=data["name"], usn=data["usn"].upper())
        db.session.add(user)
        db.session.commit()

    return json.dumps({'success':True}), 200, {'ContentType':'application/json'} 


@app.route('/post-order/<usn>', methods=['POST'])
def post_order(usn):

    if request.method == "POST":
        user = User.query.filter_by(usn=usn).first()
        data = json.loads(request.data)

        print(data)

        order = Orders(order_status="RECIEVED",user=user)
        db.session.add(order)
        db.session.commit()

    return json.dumps({'success':True}), 200, {'ContentType':'application/json'}

print("done!!!")

app.run(port=5000, debug=True)