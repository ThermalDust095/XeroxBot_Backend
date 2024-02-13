from flask import Flask, flash, request, redirect, url_for, send_from_directory
from flask_sqlalchemy import SQLAlchemy
from markupsafe import escape
from flask import request
from werkzeug.utils import secure_filename
import json 
import os
import random
import string


app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = "mysql://root:root@localhost/xerox"
app.config["SQLALCHEMY_TRACK_NOTIFICATIONS"] = False

UPLOAD_FOLDER = './files'
ALLOWED_EXTENSIONS = {'txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif', 'docx'}

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER


def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def randomize_filename(filname):
    file_ext= filname.split(".")
    file_ext[0] = ''.join(random.choices(string.ascii_uppercase +
                             string.digits, k=12))
    
    return '.'.join(file_ext), file_ext[1]


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

@app.route('/user/<usn>')
def show_queries(usn):
    data = {}
    user = User.query.filter_by(usn=usn.upper()).first()    

    if user == None:
        return "user_not_found"

    data["id"] = user.id
    data["name"] = user.name
    data["usn"] = user.usn
    data["orders"] = []
    for order in user.orders:
        data["orders"].append(order.id)

    return data


@app.route('/order/<order_id>')
def show_order(order_id):
    data = {}
    order = Orders.query.filter_by(id=order_id).first()

    data["id"] = order.id
    data["order_status"] = order.order_status
    data["user"] = order.user.usn
    data["name"] = order.user.name
    data["files"]= []

    for file in order.files:
        data["files"].append(file.file_path)

    return data


@app.route('/post-user', methods=['POST'])
def post_user():
    
    if request.method == "POST":
        data = json.loads(request.data)
        print(data)

        check_user = User.query.filter_by(usn=data["usn"]).first()

        if check_user == None:
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

    return json.dumps({"order_id": order.id}), 200, {'ContentType':'application/json'}


@app.route("/pending-orders")
def get_pending_orders():
    orders = Orders.query.filter_by(order_status="RECIEVED")
    data = []

    for order in orders:
        data.append(order.id)

    return {"orders" : data}

@app.route('/update-order-status', methods=['POST'])
def update_order():
    if request.method == "POST":
        data = json.loads(request.data)

        order_id = data["order_id"]
        order = Orders.query.filter_by(id=order_id).first()
        order.order_status = data["order_status"]

        print(order.id)
        print(order.order_status)
        db.session.commit()

    return json.dumps({'success':True}), 200, {'ContentType':'application/json'}


@app.route('/upload-file/<order_id>', methods=["GET","POST"])
def upload_file(order_id):
    if request.method == "POST":
        print(request.files)

        if 'file' not in request.files:
            flash("No file part")
            return redirect(request.url)
        
        file = request.files['file']
        desc = request.form["desc"]
        print(desc)
        print(file.filename)

        randomized_filename, file_ext = randomize_filename(file.filename)
        # print(randomized_filename)
        print(order_id)


        if file.filename == '':
            flash("No file selected")
            return redirect(request.url)

        if file and allowed_file(file.filename):
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], randomized_filename))
            order = Orders.query.filter_by(id=order_id).first()
            file = Files(file_path=randomized_filename, file_type=file_ext, desc=desc, orders=order)
            db.session.add(file)
            db.session.commit()

            return json.dumps({"file_path": file.file_path}), 200, {'ContentType':'application/json'}

        return 200
    
    
    return '''
    <!doctype html>
    <title>Upload new File</title>
    <h1>Upload new File</h1>
    <form method=post enctype=multipart/form-data>
      <input type=file name=file>
      <input type=submit value=Upload>
    </form>
    '''



@app.route('/download/<name>')
def download_file(name):
    return send_from_directory(app.config["UPLOAD_FOLDER"], name)

app.run(port=5000, debug=True)