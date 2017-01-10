#!flask/bin/python
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
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = True
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


class DurkaDurkaSchema(ma.Schema):
    class Meta:
        # Fields to expose
        fields = ('id', 'durka1', 'durka2')

    # Smart hyperlinking
    _links = ma.Hyperlinks({
        'self': ma.URLFor('id', id='<id>'),
        'collection': ma.URLFor('durka1')
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
def not_found():
    return make_response(jsonify({'error': 'Not found'}), 404)


#
# Return all of the DurkaDurkas in the system.
#
@app.route('/ddapi/v1.0/durkadurka', methods=['GET'])
def get_dd():
    # dd = []
    # for durk in db.session.query(DurkaDurka.id, DurkaDurka.durka1, DurkaDurka.durka2):
    #     dd.append({"id": durk.id, "durka1": durk.durka1, "durka2": durk.durka2})
    #
    # if len(dd) == 0:
    #     abort(404)
    #
    # return jsonify({'durkadurka': dd})
    return durkadurkas_schema.jsonify(db.session.query(DurkaDurka.id, DurkaDurka.durka1, DurkaDurka.durka2))

#
# Return a specific DurkaDurka given an id.
#
@app.route('/ddapi/v1.0/durkadurka/<int:dd_id>', methods=['GET'])
def get_dd_id(dd_id):
    # dd = []
    # for dt in db.session.query(DurkaDurka.id, DurkaDurka.durka1, DurkaDurka.durka2).filter(DurkaDurka.id == int(dd_id)):
    #     print dt
    #     dd.append({"id": dt.id, "durka1": dt.durka1, "durka2": dt.durka2})
    #
    # if len(dd) == 0:
    #     abort(404)
    # return jsonify({'durkadurka': dd})
    dds = db.session.query(DurkaDurka.id, DurkaDurka.durka1, DurkaDurka.durka2).filter(DurkaDurka.id == dd_id)
    return durkadurkas_schema.jsonify(dds)
    # return jsonify({'error': 'Not found'})


#
# Create a new DurkaDurka by posting it.
# TODO: Probably need some basic input validation on the stuff being passed in.
#
@app.route('/ddapi/v1.0/durkadurka', methods=['POST'])
def create_dd():
    if not request.json or 'durka1' not in request.json or 'durka2' not in request.json:
        abort(400)

    i2 = DurkaDurka(durka1=request.json['durka1'], durka2=request.json['durka2'])
    db.session.add(i2)
    db.session.commit()
    db.session.flush()

    #
    # I think this is where a declarative_base() may have come in handy--I could just create the .return_json()
    # function in the class instead of querying the DB and manually creating the JSON response here. :(
    #
    # dq = db.session.query(DurkaDurka.id, DurkaDurka.durka1, DurkaDurka.durka2) \
    #     .filter(DurkaDurka.durka1 == request.json['durka1']) \
    #    .filter(DurkaDurka.durka2 == request.json['durka2']) \
    #    .one()
    # db.session.flush()
    # dd = {"id": dq.id, "durka1": dq.durka1, "durka2": dq.durka2}

    # return jsonify({'durkadurka': dd}), 201
    return durkadurka_schema.jsonify(i2)

#
# Update a DurkaDurka's fields with some new data given a DurkaDurka id.
#
@app.route('/ddapi/v1.0/durkadurka/<int:dd_id>', methods=['PUT'])
def update_dd(dd_id):
    if not request.json or 'durka1' not in request.json or 'durka2' not in request.json:
        abort(400)

    q = db.session.query(DurkaDurka).filter(DurkaDurka.id == dd_id)
    record = q.one()
    record.durka1 = request.json['durka1']
    record.durka2 = request.json['durka2']
    db.session.commit()
    db.session.flush()
    # I'll have to come back to this, but postman responded quickly with this second .flush(), slow with the first.
    db.session.flush()

    # dd = {"id": dd_id, "durka1": request.json['durka1'], "durka2": request.json["durka2"]}
    # return jsonify({'durkadurka': dd}), 201

    return durkadurka_schema.jsonify(record)


#
# Route and Function to delete the DurkaDurka given a DurkaDurka id.
# TODO: session.flush() shouldn't be needed that many times.  Something in the DB is blocking the response, I'd guess...
#
@app.route('/ddapi/v1.0/durkadurka/<int:dd_id>', methods=['DELETE'])
def delete_dd(dd_id):
    d = db.session.query(DurkaDurka).filter(DurkaDurka.id == dd_id).one_or_none()
    db.session.flush()

    if d is None:
        db.session.flush()
        return jsonify({'result': False})
    else:
        try:
            db.session.delete(d)
            db.session.commit()
            db.session.flush()
            db.session.flush()  # Trying a second one to get a quick response back.
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
if __name__ == '__main__':
    app.run(debug=True)
