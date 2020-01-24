# wsgi.py
from flask import Flask, abort,request,jsonify,render_template
from config import Config

app = Flask(__name__)
app.config.from_object(Config)

from flask_sqlalchemy import SQLAlchemy
from flask_marshmallow import Marshmallow
db = SQLAlchemy(app)
ma = Marshmallow(app)

from models import Product
from schemas import products_schema
from schemas import product_schema


@app.route('/')
def home():
    products = db.session.query(Product).all()
    return render_template('home.html', products=products)

@app.route('/<int:id>')
def product_html(id):
    product = db.session.query(Product).get(id)
    return render_template('product.html', product=product)


@app.route('/products', methods=['GET'])
def products():
    products = db.session.query(Product).all() # SQLAlchemy request => 'SELECT * FROM products'
    return products_schema.jsonify(products)

# READ ONE
@app.route('/products/<int:product_id>', methods=['GET'])
def read_product(product_id):
    product = db.session.query(Product).get(product_id)
    if product is None:
        abort(404,'{"error":"Product not found"}')
    return product_schema.jsonify(product)

# CREATE
@app.route('/products' , methods=['POST'])
def create_product():
    content = request.json
    #Format des datas...
    if content is None:
        return jsonify({'ERROR': 'input data error'}), 422
    if "name" not in content:
        return jsonify({'ERROR': 'input data error'}), 422
    if content["name"] == "" :
        return jsonify({'ERROR': 'input data error'}), 422

    product=Product()
    product.name=content["name"]
    product.description=content.get("description")
    db.session.add(product)
    db.session.commit()
    return jsonify({'id':product.id  }),201

# DELETE
@app.route('/products/<int:product_id>' , methods=['DELETE'])
def delete_product(product_id):
    product = db.session.query(Product).get(product_id)
    if product is None:
        abort(404,'{"error":"Product not found"}')
    db.session.delete(product)
    try:
        db.session.commit()
        return "", 204
    except:
        abort(500,'{"error":"Database"}')

@app.route('/products/<int:product_id>' , methods=['PATCH'])
def update_product(product_id):
    product = db.session.query(Product).get(product_id)
    if product is None:
        abort(404,'{"error":"Product not found"}')

    content = request.json

    #Format des datas...
    if content is None:
        return jsonify({'ERROR': 'input data error'}), 422

    #update name
    if "name" in content and content["name"] !="":
        product.name=content["name"]

    #update description
    if "description" in content:
        product.description=content["description"]

    #db.session.update(product)
    db.session.commit()
    return "", 204

