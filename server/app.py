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
def restaurant():
    if request.method == 'GET':
        restaurants = Restaurant.query.all()

        return make_response(
            jsonify([restaurant.to_dict() for restaurant in restaurants]),
            200,
        )
    else:
        return make_response(
            jsonify({"message": "No restaurants found."})
        )
    
@app.route('/restaurants/<int:id>', methods=['GET'])
def get_restaurant(id):
    restaurant = Restaurant.query.get(id)
    
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
        return make_response(
            jsonify([pizza.to_dict() for pizza in pizzas]),
            200
        )
    else:
        return make_response(
            jsonify({"message": "No pizzas found."})
        )

if __name__ == "__main__":
    app.run(port=5555, debug=True)
