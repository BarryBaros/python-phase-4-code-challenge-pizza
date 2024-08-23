#!/usr/bin/env python3
from models import db, Restaurant, RestaurantPizza, Pizza
from flask_migrate import Migrate
from flask import Flask, request, make_response, jsonify
from flask_restful import Api, Resource
import os

BASE_DIR = os.path.abspath(os.path.dirname(__file__))
DATABASE = os.environ.get("DB_URI", f"sqlite:///{os.path.join(BASE_DIR, 'app.db')}")

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = DATABASE
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.json.compact = False

migrate = Migrate(app, db)

db.init_app(app)

api = Api(app)

@app.route("/")
def index():
    return "<h1>Code challenge</h1>"

@app.route('/restaurants', methods=['GET'])
def restaurants():
    if request.method == 'GET':
        restaurants = Restaurant.query.all()

        return make_response(
            jsonify([restaurant.to_dict() for restaurant in restaurants]),
            200,
        )
    else:
        return make_response(
            jsonify({"message": "No restaurants found."}),
            404
        )
    
@app.route('/restaurants/<int:id>', methods=['GET'])
def get_restaurant(id):
    restaurant = db.session.get(Restaurant, id)
    
    if restaurant:
        response = {
            "id": restaurant.id,
            "name": restaurant.name,
            "address": restaurant.address,
            "restaurant_pizzas": []
        }
        for rp in restaurant.restaurant_pizzas:
            pizza_data = {
                "id": rp.id,
                "price": rp.price,
                "restaurant_id": rp.restaurant_id,
                "pizza_id": rp.pizza_id,
                "pizza": {
                    "id": rp.pizza.id,
                    "name": rp.pizza.name,
                    "ingredients": rp.pizza.ingredients
                }
            }
            response["restaurant_pizzas"].append(pizza_data)
        
        return jsonify(response), 200
    
    return jsonify({"error": "Restaurant not found"}), 404

@app.route('/pizzas', methods=["GET"])
def get_pizzas():
    if request.method == "GET":
        pizzas = Pizza.query.all()
        return jsonify([pizza.to_dict() for pizza in pizzas]), 200
    return jsonify({"message": "No pizzas found."}), 404

@app.route('/restaurants/<int:id>', methods=['DELETE'])
def delete_restaurant(id):
    restaurant = db.session.get(Restaurant, id)
    if restaurant:
        db.session.delete(restaurant)
        db.session.commit()
        return '', 204
    return jsonify({"error": "Restaurant not found"}), 404

    
@app.route('/restaurant_pizzas', methods=["POST"])
def create_restaurant_pizza():
    data = request.get_json()

    try:
        # Validate the price
        price = data.get('price')
        if not isinstance(price, int) or price <= 0:
            raise ValueError("validation errors")

        # Validate pizza_id and restaurant_id
        pizza_id = data.get('pizza_id')
        restaurant_id = data.get('restaurant_id')

        pizza = db.session.get(Pizza, pizza_id)
        restaurant = db.session.get(Restaurant, restaurant_id)

        if not pizza or not restaurant:
            raise ValueError("validation errors")

        # Create the RestaurantPizza
        restaurant_pizza = RestaurantPizza(
            price=price,
            pizza_id=pizza_id,
            restaurant_id=restaurant_id
        )

        db.session.add(restaurant_pizza)
        db.session.commit()

        response = {
            "id": restaurant_pizza.id,
            "price": restaurant_pizza.price,
            "pizza_id": restaurant_pizza.pizza_id,
            "restaurant_id": restaurant_pizza.restaurant_id,
            "pizza": {
                "id": pizza.id,
                "name": pizza.name,
                "ingredients": pizza.ingredients
            },
            "restaurant": {
                "id": restaurant.id,
                "name": restaurant.name,
                "address": restaurant.address
            }
        }

        return jsonify(response), 201
    
    except ValueError as e:
        return jsonify({"errors": [str(e)]}), 400
    
    except Exception as e:
        return jsonify({"errors": ["Something went wrong."]}), 500

if __name__ == "__main__":
    app.run(port=5555, debug=True)
