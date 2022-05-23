from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from utils import open_file
from datetime import datetime

app = Flask(__name__)
app.config['DEBUG'] = True
app.config['JSON_AS_ASCII'] = False
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///test.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)


class User(db.Model):
    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String(20))
    last_name = db.Column(db.String(20))
    age = db.Column(db.Integer)
    email = db.Column(db.String(50))
    role = db.Column(db.String(20))
    phone = db.Column(db.String(15))


class Order(db.Model):
    __tablename__ = "orders"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(20))
    description = db.Column(db.String(200))
    start_date = db.Column(db.Date)
    end_date = db.Column(db.Date)
    address = db.Column(db.String(150))
    price = db.Column(db.Integer)
    customer_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    executor_id = db.Column(db.Integer, db.ForeignKey('users.id'))


class Offer(db.Model):
    __tablename__ = "offers"

    id = db.Column(db.Integer, primary_key=True)
    order_id = db.Column(db.Integer, db.ForeignKey('orders.id'))
    executor_id = db.Column(db.Integer, db.ForeignKey('users.id'))


db.create_all()


def insert_users(users_):
    users = []
    for user_ in users_:
        users.append(
            User(
                first_name=user_['first_name'],
                last_name=user_['last_name'],
                age=user_['age'],
                email=user_['email'],
                role=user_['role'],
                phone=user_['phone']
            )
        )
    with db.session.begin():
        db.session.add_all(users)


def insert_orders(orders_):
    orders = []
    for order_ in orders_:
        orders.append(
            Order(
                name=order_['name'],
                description=order_['description'],
                start_date=datetime.strptime(order_['start_date'], '%m/%d/%Y'),
                end_date=datetime.strptime(order_['end_date'], '%m/%d/%Y'),
                address=order_['address'],
                price=order_['price'],
                customer_id=order_['customer_id'],
                executor_id=order_['executor_id']
            )
        )
    with db.session.begin():
        db.session.add_all(orders)


def insert_offers(offers_):
    offers = []
    for offer_ in offers_:
        offers.append(
            Offer(
                order_id=offer_['order_id'],
                executor_id=offer_['executor_id']
            )
        )
    with db.session.begin():
        db.session.add_all(offers)


users_ = open_file("user_json.json")
orders_ = open_file("order_json.json")
offers_ = open_file("offer_json.json")
# insert_users(users_)
# insert_orders(orders_)
# insert_offers(offers_)


@app.route("/users/", methods=['GET', 'POST'])
def users_all():
    if request.method == 'GET':
        users_list = []
        for user in User.query.all():
            users_list.append({
                "id": user.id,
                "first_name": user.first_name,
                "last_name": user.last_name,
                "age": user.age,
                "email": user.email,
                "role": user.role,
                "phone": user.phone
            })
        return jsonify(users_list)
    elif request.method == 'POST':
        data = request.get_json()
        new_user = User(
            first_name=data['first_name'],
            last_name=data['last_name'],
            age=data['age'],
            email=data['email'],
            role=data['role'],
            phone=data['phone']
        )
        with db.session.begin():
            db.session.add(new_user)
        return "Добавлен новый пользователь!"


@app.route("/users/<int:uid>", methods=['GET', 'PUT', 'DELETE'])
def selected_user(uid):
    user = User.query.get(uid)
    if request.method == 'GET':
        user_json = {
                    "id": user.id,
                    "first_name": user.first_name,
                    "last_name": user.last_name,
                    "age": user.age,
                    "email": user.email,
                    "role": user.role,
                    "phone": user.phone
                }
        return jsonify(user_json)
    elif request.method == 'PUT':
        new_user = request.json

        user.first_name = new_user.get('first_name', user.first_name)
        user.last_name = new_user.get('last_name', user.last_name)
        user.age = new_user.get('age', user.age)
        user.email = new_user.get('email', user.email)
        user.role = new_user.get('role', user.role)
        user.phone = new_user.get('phone', user.phone)

        db.session.add(user)
        db.session.commit()
        return "Обновление информации о пользователе выполнено!"

    elif request.method == 'DELETE':
        db.session.delete(user)
        db.session.commit()
        return "Удаление пользователя выполнено!"


@app.route("/orders/", methods=['GET', 'POST'])
def orders_all():
    if request.method == 'GET':
        orders_list = []
        for order in Order.query.all():
            orders_list.append({
                "id": order.id,
                "name": order.name,
                "description": order.description,
                "start_date": order.start_date,
                "end_date": order.end_date,
                "address": order.address,
                "price": order.price,
                "customer_id": order.customer_id,
                "executor_id": order.executor_id
            })
        return jsonify(orders_list)
    elif request.method == 'POST':
        data = request.get_json()
        new_order = Order(
            name=data.get('name'),
            description=data.get('description'),
            start_date=datetime.strptime(data['start_date'], '%m/%d/%Y'),
            end_date=datetime.strptime(data['end_date'], '%m/%d/%Y'),
            address=data.get('address'),
            price=data.get('price'),
            customer_id=data.get('customer_id'),
            executor_id=data.get('executor_id')
        )
        with db.session.begin():
            db.session.add(new_order)
        return "Добавлен новый заказ!"


@app.route("/orders/<int:uid>", methods=['GET', 'PUT', 'DELETE'])
def selected_order(uid):
    order = Order.query.get(uid)
    if request.method == 'GET':
        order_json = {
                "id": order.id,
                "name": order.name,
                "description": order.description,
                "start_date": order.start_date,
                "end_date": order.end_date,
                "address": order.address,
                "price": order.price,
                "customer_id": order.customer_id,
                "executor_id": order.executor_id
                }
        return jsonify(order_json)
    elif request.method == 'PUT':
        new_order = request.json

        order.name = new_order.get('name', order.name)
        order.description = new_order.get('description', order.description)
        order.start_date = datetime.strptime(new_order.get('start_date', order.start_date), '%m/%d/%Y')
        order.end_date = datetime.strptime(new_order.get('end_date', order.end_date), '%m/%d/%Y')
        order.address = new_order.get('address', order.address)
        order.price = new_order.get('price', order.price)
        order.customer_id = new_order.get('customer_id', order.customer_id)
        order.executor_id = new_order.get('executor_id', order.executor_id)

        db.session.add(order)
        db.session.commit()
        return "Обновление информации о заказе выполнено!"

    elif request.method == 'DELETE':
        db.session.delete(order)
        db.session.commit()
        return "Удаление заказа выполнено!"


@app.route("/offers/", methods=['GET', 'POST'])
def offers_all():
    if request.method == 'GET':
        offers_list = []
        for offer in Offer.query.all():
            offers_list.append({
                "id": offer.id,
                "order_id": offer.order_id,
                "executor_id": offer.executor_id
            })
        return jsonify(offers_list)
    elif request.method == 'POST':
        data = request.json
        new_offer = Offer(
            order_id=data.get('order_id'),
            executor_id=data.get('executor_id')
        )
        with db.session.begin():
            db.session.add(new_offer)
        return "Добавлено новое предложение!"


@app.route("/offers/<int:uid>", methods=['GET', 'PUT', 'DELETE'])
def selected_offer(uid):
    offer = Offer.query.get(uid)
    if request.method == 'GET':
        offer_json = {
                "id": offer.id,
                "order_id": offer.order_id,
                "executor_id": offer.executor_id
                }
        return jsonify(offer_json)
    elif request.method == 'PUT':
        new_offer = request.json

        offer.order_id = new_offer.get('order_id', offer.order_id)
        offer.executor_id = new_offer.get('executor_id', offer.executor_id)

        db.session.add(offer)
        db.session.commit()
        return 'Обновление информации о предложении выполнено!'

    elif request.method == 'DELETE':
        db.session.delete(offer)
        db.session.commit()
        return 'Удаление предложения выполнено!'


app.run()
