import os
from flask import Flask, request, jsonify, abort
from sqlalchemy import exc
import json
from flask_cors import CORS

from .database.models import db_drop_and_create_all, setup_db, Drink
from .auth.auth import AuthError, requires_auth

app = Flask(__name__)
setup_db(app)
cors = CORS(app, resources={r"/*": {"origins": "*"}})

'''
@TODO uncomment the following line to initialize the datbase
!! NOTE THIS WILL DROP ALL RECORDS AND START YOUR DB FROM SCRATCH
!! NOTE THIS MUST BE UNCOMMENTED ON FIRST RUN
'''
# db_drop_and_create_all()


@app.after_request
def after_request(response):
    response.headers.add('Access-Control-Allow-Headers', 'Content-Type, Authorization, true')
    response.headers.add('Access-Control-Allow-Methods', 'GET, PUT, POST, DELETE, OPTIONS')
    return response


@app.route('/drinks')
def get_drinks():
    all_drinks = Drink.query.all()
    formatted_drinks = [drink.short() for drink in all_drinks]
    return jsonify({
        'success': formatted_drinks,
    })


@app.route('/drinks-detail')
@requires_auth('get:drinks-detail')
def get_drinks_in_detail(jwt):
    all_drinks = Drink.query.order_by(Drink.id).all()
    formatted_drinks = [drink.long() for drink in all_drinks]
    return jsonify({
        'success': formatted_drinks,
    })


@app.route('/drinks', methods=['POST'])
@requires_auth('post:drinks')
def create_drink(jwt):
    try:
        data = request.get_json()
        title = data.get('title')
        recipe = data.get('recipe')
        drink = Drink(title=title, recipe=str(recipe))
        drink.insert()
        return jsonify({
            'success': True,
        })
    except Exception:
        abort(422)


@app.route('/drinks/<int:drink_id>', methods=['PATCH'])
@requires_auth('patch:drinks')
def update_drink(jwt, drink_id):
    data = request.get_json()
    recipe = data.get('recipe', None)
    try:
        get_drink = Drink.query.filter_by(id=drink_id).one_or_none()
        if get_drink is None:
            abort(404)
        if recipe is None:
            abort(404)
        get_drink.recipe = str(recipe)
        get_drink.update()
        return jsonify({
            'success': True,
        })
    except Exception:
        abort(422)


@app.route('/drinks/<int:drink_id>', methods=['DELETE'])
@requires_auth('delete:drinks')
def delete_drink(jwt, drink_id):
    try:
        drink = Drink.query.filter(Drink.id == drink_id).one_or_none()
        if drink is None:
            abort(404)
        drink.delete()
        return jsonify({
            'success': True,
            'deleted': drink_id,
        })
    except Exception:
        abort(422)


# Error Handling
'''
Example error handling for unprocessable entity
'''
@app.errorhandler(422)
def unprocessable(error):
    return jsonify({
                    "success": False,
                    "error": 422,
                    "message": "unprocessable request"
                    }), 422


@app.errorhandler(401)
def not_authorized(error):
    return jsonify({
                    "success": False,
                    "error": 401,
                    "message": "not authorized"
                    }), 401


@app.errorhandler(404)
def not_found(error):
    return jsonify({
                    "success": False,
                    "error": 404,
                    "message": "resource not found"
                    }), 404


@app.errorhandler(500)
def server_error(error):
    return jsonify({
                    "success": False,
                    "error": 500,
                    "message": "internal server error"
                    }), 500
