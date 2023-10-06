"""
This module takes care of starting the API Server, Loading the DB and Adding the endpoints
"""
import os
from flask import Flask, request, jsonify, url_for
from flask_migrate import Migrate
from flask_swagger import swagger
from flask_cors import CORS
from utils import APIException, generate_sitemap
from admin import setup_admin
from models import db, Characters, User, Planets, Starships, Person, user, FavoriteCharacters


app = Flask(__name__)
app.url_map.strict_slashes = False

db_url = os.getenv("DATABASE_URL")
if db_url is not None:
    app.config['SQLALCHEMY_DATABASE_URI'] = db_url.replace("postgres://", "postgresql://")
else:
    app.config['SQLALCHEMY_DATABASE_URI'] = "sqlite:////tmp/test.db"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

MIGRATE = Migrate(app, db)
db.init_app(app)
CORS(app)
setup_admin(app)

# Handle/serialize errors like a JSON object
@app.errorhandler(APIException)
def handle_invalid_usage(error):
    return jsonify(error.to_dict()), error.status_code

@app.route('/characters', methods=['GET'])
def get_characters():
    characters = Characters.query.all()
    result = [character.serialize() for character in characters]
    return jsonify(result), 200

@app.route('/characters/<int:character_id>', methods=['GET'])
def get_character(character_id):
    character = Characters.query.get(character_id)
    if character:
        return jsonify(character.serialize()), 200
    else:
        return jsonify({'message': 'Character not found'}), 404

@app.route('/people', methods=['GET'])
def get_people():
    people = Person.query.all()
    result = []
    for person in people:
        result.append(person.serialize())
    return jsonify(result), 200

@app.route('/people/<int:people_id>', methods=['GET'])
def get_person(people_id):
    person = Person.query.get(people_id)
    if person:
        return jsonify(person.serialize()), 200
    else:
        return jsonify({'message': 'Person not found'}), 404

@app.route('/planets', methods=['GET'])
def get_planets():
    planets = Planets.query.all()
    result = []
    for planet in planets:
        result.append(planet.serialize())
    return jsonify(result), 200

@app.route('/planets/<int:planet_id>', methods=['GET'])
def get_planet(planet_id):
    planet = Planets.query.get(planet_id)
    if planet:
        return jsonify(planet.serialize()), 200
    else:
        return jsonify({'message': 'Planet not found'}), 404
    

@app.route('/starships', methods=['GET'])
def get_starships():
    starships = Starships.query.all()
    result = [starship.serialize() for starship in starships]
    return jsonify(result), 200

@app.route('/starships/<int:starship_id>', methods=['GET'])
def get_starship(starship_id):
    starship = Starships.query.get(starship_id)
    if starship:
        return jsonify(starship.serialize()), 200
    else:
        return jsonify({'message': 'Starship not found'}), 404


@app.route('/')
def sitemap():
    return generate_sitemap(app)

@app.route('/user', methods=['GET'])
def handle_hello():

    response_body = {
        "msg": "Hello, this is your GET /user/<id> response ",
        "result": user.serialize()
    }

    return jsonify(response_body), 200


@app.route('/favorite/people/<int:people_id>', methods=['POST'])
def create_favorite_people(people_id):
    new_favorite_people = FavoriteCharacters(user_id=1, Characters_id=people_id)
    db.session.add(new_favorite_people)
    db.session.commit()

    response_body = {
        "msg": "Hello, this is your POST /favorite/people/<int:people_id> response ",
        "result": new_favorite_people.serialize()
    }

    return jsonify(response_body), 200

# ... (tu código existente)

@app.route('/users/favorites', methods=['GET'])
def get_user_favorites():
    
    user_favorites = FavoriteCharacters.query.filter_by(user_id=user.id).all()

    result = [favorite.serialize() for favorite in user_favorites]
    return jsonify(result), 200

@app.route('/favorite/planet/<int:planet_id>', methods=['POST'])
def create_favorite_planet(planet_id):
    new_favorite_planet = FavoriteCharacters(user_id=user.id, planet_id=planet_id)
    db.session.add(new_favorite_planet)
    db.session.commit()

    response_body = {
        "msg": "Planet added to favorites successfully",
        "result": new_favorite_planet.serialize()
    }

    return jsonify(response_body), 200

@app.route('/favorite/planet/<int:planet_id>', methods=['DELETE'])
def delete_favorite_planet(planet_id):
    favorite_planet = FavoriteCharacters.query.filter_by(user_id=user.id, planet_id=planet_id).first()

    if favorite_planet:
        db.session.delete(favorite_planet)
        db.session.commit()
        return jsonify({"msg": "Planet removed from favorites successfully"}), 200
    else:
        return jsonify({'message': 'Favorite planet not found'}), 404

@app.route('/favorite/people/<int:people_id>', methods=['DELETE'])
def delete_favorite_people(people_id):
    favorite_people = FavoriteCharacters.query.filter_by(user_id=user.id, people_id=people_id).first()

    if favorite_people:
        db.session.delete(favorite_people)
        db.session.commit()
        return jsonify({"msg": "People removed from favorites successfully"}), 200
    else:
        return jsonify({'message': 'Favorite people not found'}), 404


# this only runs if `$ python src/app.py` is executed
if __name__ == '__main__':
    PORT = int(os.environ.get('PORT', 3000))
    app.run(host='0.0.0.0', port=PORT, debug=False)