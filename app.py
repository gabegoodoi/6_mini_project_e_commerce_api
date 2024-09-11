from flask import Flask, jsonify, request
from flask_sqlalchemy import SQLAlchemy
from datetime import timedelta, datetime
from flask_marshmallow import Marshmallow
from marshmallow import ValidationError, fields
from password import mypassword

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = f'mysql+mysqlconnector://root:{mypassword}@localhost/e_commerce_db'
db = SQLAlchemy(app)
ma = Marshmallow(app)

with app.app_context():
    db.create_all()

class Account(db.Model):
    __tablename__ = 'Customer_Accounts'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(255), unique=True, nullable=False)
    password = db.Column(db.String(255), nullable=False)
    customer_id = db.Column(db.Integer, db.ForeignKey('Customers.id'))
    customer = db.relationship('Customer', backref='customer_account', uselist=False)

class Customer(db.Model):
    __tablename__ = 'Customers'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), nullable=False)
    email = db.Column(db.String(320))
    phone = db.Column(db.String(15))

class Product(db.Model):
    __tablename__ = 'Products'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), nullable=False)
    price = db.Column(db.Float, nullable=False)

order_product = db.Table('Order_Product',
        db.Column('order_id', db.Integer, db.ForeignKey('Orders.id'), primary_key=True),
        db.Column('product_id', db.Integer, db.ForeignKey('Products.id'), primary_key=True)
)

class Order(db.Model):
    __tablename__ = 'Orders'
    id = db.Column(db.Integer, primary_key=True)
    order_date = db.Column(db.Date, nullable=False)
    expected_delivery_date = db.Column(db.Date, nullable=False, default=None)
    customer_id = db.Column(db.Integer, db.ForeignKey('Customers.id'))
    customer = db.relationship('Customer', backref='orders')
    products = db.relationship('Product', secondary=order_product, backref=db.backref('orders'))

    def __init__(self, order_date, customer_id):
        self.order_date = order_date
        self.customer_id = customer_id
        self.expected_delivery_date = self.calculate_expected_delivery_date()

    def calculate_expected_delivery_date(self):
        return self.order_date + timedelta(days=3)
    
class AccountsSchema(ma.Schema):
    username = fields.String(required=True)
    password = fields.String(required=True)

    class Meta:
        fields = ('username', 'password', 'customer_id', 'id')

account_schema = AccountsSchema()
accounts_schema = AccountsSchema(many=True)

class CustomersSchema(ma.Schema):
    name = fields.String(required=True)
    email = fields.String(required=True)
    phone = fields.String(required=True)

    class Meta:
        fields = ('name', 'email', 'phone', 'id')

customer_schema = CustomersSchema()
customers_schema = CustomersSchema(many=True)

class ProductsSchema(ma.Schema):
    name = fields.String(required=True)
    price = fields.Float(required=True)

    class Meta:
        fields = ('name', 'price', 'id')

product_schema = ProductsSchema()
products_schema = ProductsSchema(many=True)

class CustomerAccountDetailSchema(ma.Schema):
    username = fields.String(required=True)
    password = fields.String(required=True)
    customer = fields.Nested(CustomersSchema)

    class Meta:
        fields = ('username', 'password', 'customer')

customer_account_detail_schema = CustomerAccountDetailSchema()
customers_accounts_detail_schema = CustomerAccountDetailSchema(many=True)

class OrderViewSchema(ma.Schema):
    order_date = fields.Date(required=True)
    expected_delivery_date = fields.Date()
    customer_id = fields.Integer(required=True)
    product_ids = fields.Method("get_product_ids")

    class Meta:
        fields = ('order_date', 'expected_delivery_date', 'customer_id', 'product_ids', 'id')

    def get_product_ids(self, object):
        return [product.id for product in object.products]

order_view_schema = OrderViewSchema()
orders_view_schema = OrderViewSchema(many=True)

class OrderManipSchema(ma.Schema):
    order_date = fields.Date(required=True)
    expected_delivery_date = fields.Date(dump_only=True)
    customer_id = fields.Integer(required=True)
    product_ids = fields.List(fields.Integer, required=True)

    class Meta:
        fields = ('order_date', 'expected_delivery_date', 'customer_id', 'product_ids', 'id')

order_manip_schema = OrderManipSchema()
orders_manip_schema = OrderManipSchema(many=True)

@app.route('/')
def home():
    return "Welcome to the home page"

@app.route('/customers', methods=['GET'])
def get_customers():
    customers = Customer.query.all()
    return customers_schema.jsonify(customers)

@app.route('/customers/<int:id>', methods=['GET'])
def get_customer_by_id(id):
    customer = Customer.query.get_or_404(id)
    return customer_schema.jsonify(customer)

@app.route('/customers', methods=['POST'])
def add_customer():
    try:
        customer_data = customer_schema.load(request.json)

    except ValidationError as e:
        return jsonify(e.messages), 400
    
    new_customer = Customer(name=customer_data['name'], email=customer_data['email'], phone=customer_data['phone'])
    db.session.add(new_customer)
    db.session.commit()
    return jsonify({"message": "New customer added successfully"})

@app.route('/customers/<int:id>', methods=['PUT'])
def update_customer(id):
    customer = Customer.query.get_or_404(id)
    try:
        customer_data = customer_schema.load(request.json)
    except ValidationError as e:
        return jsonify(e.messages), 400
    
    customer.name = customer_data['name']
    customer.email = customer_data['email']
    customer.phone = customer_data['phone']
    db.session.commit()
    return jsonify({"message": "customer details updated successfully"})

@app.route('/customers/<int:id>', methods=['DELETE'])
def delete_customer(id):
    customer = Customer.query.get_or_404(id)
    db.session.delete(customer)
    db.session.commit()
    return jsonify({"message": "customer deleted successfully"})

@app.route('/accounts', methods=['POST'])
def add_account():
    try:
        account_data = account_schema.load(request.json)

    except ValidationError as e:
        return jsonify(e.messages), 400
    
    new_account = Account(username=account_data['username'], password=account_data['password'], customer_id=account_data['customer_id'])
    db.session.add(new_account)
    db.session.commit()
    return jsonify({"message": "New account added successfully"})

@app.route('/accounts/<int:id>', methods=['GET'])
def get_account_with_customer(id):
    account = Account.query.get_or_404(id)
    return customer_account_detail_schema.jsonify(account)

@app.route('/accounts/<int:id>', methods=['PUT'])
def update_account(id):
    account = Account.query.get_or_404(id)
    try:
        account_data = account_schema.load(request.json)
    except ValidationError as e:
        return jsonify(e.messages), 400
    
    account.username = account_data['username']
    account.password = account_data['password']
    db.session.commit()
    return jsonify({"message": "account details updated successfully"})

@app.route('/accounts/<int:id>', methods=['DELETE'])
def delete_account(id):
    account = Account.query.get_or_404(id)
    db.session.delete(account)
    db.session.commit()
    return jsonify({"message": "account deleted successfully"})


@app.route('/products/<int:id>', methods=['GET'])
def get_product_by_id(id):
    product = Product.query.get_or_404(id)
    return product_schema.jsonify(product)

@app.route('/products', methods=['GET'])
def get_products():
    products = Product.query.all()
    return products_schema.jsonify(products)

@app.route('/products', methods=['POST'])
def add_product():
    try:
        product_data = product_schema.load(request.json)

    except ValidationError as e:
        return jsonify(e.messages), 400
    
    new_product = Product(name=product_data['name'], price=product_data['price'])
    db.session.add(new_product)
    db.session.commit()
    return jsonify({"message": "New product added successfully"})

@app.route('/products/<int:id>', methods=['PUT'])
def update_product(id):
    product = Product.query.get_or_404(id)
    try:
        product_data = product_schema.load(request.json)
    except ValidationError as e:
        return jsonify(e.messages), 400
    
    product.name = product_data['name']
    product.price = product_data['price']
    db.session.commit()
    return jsonify({"message": "product details updated successfully"})

@app.route('/products/<int:id>', methods=['DELETE'])
def delete_products(id):
    product = Product.query.get_or_404(id)
    db.session.delete(product)
    db.session.commit()
    return jsonify({"message": "product deleted successfully"})

@app.route('/orders', methods=['GET'])
def get_orders():
    orders = Order.query.all()
    return orders_view_schema.jsonify(orders)

@app.route('/orders/<int:id>', methods=['GET'])
def get_order_by_id(id):
    order = Order.query.get_or_404(id)
    return order_view_schema.jsonify(order)

@app.route('/order/status/<int:id>', methods=['GET'])
def print_delivery_status(id):
    order = Order.query.get_or_404(id)
    today = datetime.today().date()

    if order.expected_delivery_date < today:
        message = f"Delivered on: {order.expected_delivery_date}"
    else:
        message = f"Expected delivery date: {order.expected_delivery_date}"

    return jsonify({'status': message})
    
@app.route('/orders', methods=['POST'])
def place_order():
    try:
        order_data = order_manip_schema.load(request.json)

    except ValidationError as e:
        return jsonify(e.messages), 400
    
    new_order = Order(order_date=order_data['order_date'], customer_id=order_data['customer_id'])
    db.session.add(new_order)
    db.session.commit()

    for product_id in order_data['product_ids']:
        product = Product.query.get(product_id)
        if product:
            new_order.products.append(product)
    
    db.session.commit()
    
    return jsonify({"message": "New order placed successfully"})

if __name__ == '__main__':
    app.run(debug=True)