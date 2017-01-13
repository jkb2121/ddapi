#!flask/bin/python
from sqlalchemy.exc import DataError
from sqlalchemy.ext.declarative import declarative_base

from flask import Flask, jsonify
from flask import request, abort, make_response
from flask_marshmallow import Marshmallow
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
ma = Marshmallow(app)
# ----------------------------------------------------------------------------------------------------------------------
#
# Flask_SQLAlchemy Setup to talk to MySQL.
# Note:  Yes, I hard coded my username and password for my local MySQL instance.
# Do I need to do the encoding to ISO-8859-1 to deal with weird characters in my raw DB tables?
#

app.config["SQLALCHEMY_DATABASE_URI"] = 'mysql+pymysql://kitflask:TPjbaX50bq3s0EJ6@localhost/kits'
app.config["SQLALCHEMY_ECHO"] = True
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
db = SQLAlchemy(app)

Base = declarative_base()


class DurkaDurka(db.Model):
    __tablename__ = 'durkadurka'
    id = db.Column('id', db.Integer, primary_key=True)
    durka1 = db.Column(db.String(45))
    durka2 = db.Column(db.String(45))

    def __init__(self, durka1, durka2):
        self.durka1 = durka1
        self.durka2 = durka2


#
# Basic input validation.  Just get an appropriately-sized substring if its too long, or throw an error if it's None
#
def validate_durka(indurka):
    outdurka = indurka

    if indurka is None:
        raise DataError

    if len(indurka) > 45:
        outdurka = indurka[0:44]

    return outdurka


class DurkaDurkaSchema(ma.Schema):
    class Meta:
        # Fields to expose
        fields = ('id', 'durka1', 'durka2', '_links')

    # Smart hyperlinking so now we're HATEOAS.
    _links = ma.Hyperlinks({
        'self': ma.URLFor('get_dd_id', dd_id='<id>'),
        'collection': ma.URLFor('get_dd')
    })


durkadurka_schema = DurkaDurkaSchema()
durkadurkas_schema = DurkaDurkaSchema(many=True)


# ----------------------------------------------------------------------------------------------------------------------
#
# Flask Routing functions.


#
# Return some JSON in the event of an error returned.
#
@app.errorhandler(404)
def not_found(error):
    if error:
        return make_response(jsonify({'error': "{}".format(error)}), 404)
    return make_response(jsonify({'error': 'Not found'}), 404)


#
# Return all of the DurkaDurkas in the system.
#
@app.route('/ddapi/v1.0/durkadurka', methods=['GET'])
def get_dd():
    dds = db.session.query(DurkaDurka.id, DurkaDurka.durka1, DurkaDurka.durka2)
    return durkadurkas_schema.jsonify(dds)


#
# Return a specific DurkaDurka given an id.
#
@app.route('/ddapi/v1.0/durkadurka/<int:dd_id>', methods=['GET'])
def get_dd_id(dd_id):
    dds = db.session.query(DurkaDurka.id, DurkaDurka.durka1, DurkaDurka.durka2).filter(DurkaDurka.id == dd_id)
    return durkadurkas_schema.jsonify(dds)


#
# Create a new DurkaDurka by posting it.
#
@app.route('/ddapi/v1.0/durkadurka', methods=['POST'])
def create_dd():
    if not request.json or 'durka1' not in request.json or 'durka2' not in request.json:
        abort(400)
    try:
        i2 = DurkaDurka(durka1=validate_durka(request.json['durka1']),
                        durka2=validate_durka(request.json['durka2']))
        db.session.add(i2)
        db.session.commit()
        return durkadurka_schema.jsonify(i2)
    except DataError:
        abort(500)



#
# Update a DurkaDurka's fields with some new data given a DurkaDurka id.
#
@app.route('/ddapi/v1.0/durkadurka/<int:dd_id>', methods=['PUT'])
def update_dd(dd_id):
    if not request.json or 'durka1' not in request.json or 'durka2' not in request.json:
        abort(400)

    q = db.session.query(DurkaDurka).filter(DurkaDurka.id == dd_id)
    record = q.one()

    try:
        record.durka1 = validate_durka(request.json['durka1'])
        record.durka2 = validate_durka(request.json['durka2'])
        db.session.commit()
    except DataError:
        abort(500)

    return durkadurka_schema.jsonify(record)


#
# Route and Function to delete the DurkaDurka given a DurkaDurka id.
#
@app.route('/ddapi/v1.0/durkadurka/<int:dd_id>', methods=['DELETE'])
def delete_dd(dd_id):
    try:
        d = db.session.query(DurkaDurka).filter(DurkaDurka.id == dd_id).one_or_none()
    except:
        return jsonify({'result': False})

    if d is None:
        return jsonify({'result': False})
    else:
        try:
            db.session.delete(d)
            db.session.commit()
            return jsonify({'result': True})
        except:
            return jsonify({'result': False})


#
# Default route.  Not sure what typically goes here on an API.
# TODO: Figure out what goes in the default route for an API.
#
@app.route('/')
def index():
    return "DurkaDurka API"


# ----------------------------------------------------------------------------------------------------------------------
#
# Main function to kick off the Flask App.
# Notice the threaded=True--that's how to kick off multithreading (Thanks to to Paul M!)
# With the multithreading, the rollbacks don't block the database updates.
#

if __name__ == '__main__':
    app.run(debug=True, threaded=True)
