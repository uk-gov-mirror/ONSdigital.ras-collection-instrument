from flask import Flask, request, jsonify, make_response
#from flask_cors import CORS
from flask.ext.sqlalchemy import SQLAlchemy
#from models import Result
import os

# Enable cross-origin requests
app = Flask(__name__)
#CORS(app)

collection_instruments = []

#
# http://docs.sqlalchemy.org/en/latest/core/type_basics.html
#
# data_table = Table('data_table', metadata,
#    Column('id', Integer, primary_key=True),
#    Column('data', JSON)
# )
#

app.config.from_object(os.environ['APP_SETTINGS'])

#app.config.from_object("config.StagingConfig")
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

import uuid
from models import *

print "before"

a = Result.query.all()
print a

print "after"

@app.route('/collectioninstrument', methods=['GET'])
def collection():

    print "help"
    for key in a:
        print key.id

    return "hello"  #jsonify(a)


@app.route('/collectioninstrument', methods=['POST'])
def create():
    json = request.json
    if json:
        response = make_response("")
        collection_instruments.append(request.json)
        json["id"] = len(collection_instruments)
        response.headers["location"] = "/collectioninstrument/" + str(json["id"])
        return response, 201
    return jsonify({"message": "Please provide a valid Json object.",
                    "hint": "you may need to pass a content-type: application/json header"}), 400


@app.route('/collectioninstrument/id/<int:_id>', methods=['GET'])
def get_id(_id):
    """ Locate a collection instrument by row ID.

    This method is intended for locating collection instruments by a non-human-readable 'id'
    as opposed to by human-readable reference.
    """
    if _id > 0 and len(collection_instruments) >= _id:
        return jsonify(collection_instruments[_id - 1])
    return jsonify({"message": "Please provide a valid collection instrument ID.",
                    "hint": "There's currently " + str(len(collection_instruments)) + " collection instrument(s)."}), 400


@app.route('/collectioninstrument/<string:ref>', methods=['GET'])
def get_ref(ref):
    """ Locate a collection instrument by reference.

    This method is intended for locating collection instruments by a human-readable 'reference'
    as opposed to by database Id.
    """
    return jsonify({"ref": ref})


app.run(port=5051)

