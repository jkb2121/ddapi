#!flask/bin/python
from sqlalchemy import create_engine
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import scoped_session, sessionmaker

from flask import Flask, jsonify
from flask import request, abort, make_response

app = Flask(__name__)
# ----------------------------------------------------------------------------------------------------------------------
#
# SQLAlchemy Setup to talk to MySQL.
# Note:  Yes, I hard coded my username and password for my local MySQL instance.
# Change echo=True to false to quiet down the output.
# Also encoding to ISO-8859-1 to deal with weird characters in my raw DB tables.
#
engine = create_engine('mysql+pymysql://kitflask:TPjbaX50bq3s0EJ6@localhost/kits', convert_unicode=True,
                       echo=True, encoding="ISO-8859-1")

# TODO: Automap Stuff--this is probably where I need to swap it out for the Declarative...
Base = automap_base()
Base.prepare(engine, reflect=True)
DurkaDurka = Base.classes.durkadurka

session = scoped_session(sessionmaker(bind=engine))

# ----------------------------------------------------------------------------------------------------------------------
#
# Flask Routing functions.


#
# Return some JSON in the event of an error returned.  I should also return a more informative note if one is passed
# into the function.
#
@app.errorhandler(404)
def not_found(error):
    return make_response(jsonify({'error': 'Not found'}), 404)


#
# Return all of the DurkaDurkas in the system.
#
@app.route('/ddapi/v1.0/durkadurka', methods=['GET'])
def get_dd():
    dd = []
    for durk in session.query(DurkaDurka.id, DurkaDurka.durka1, DurkaDurka.durka2):
        dd.append({"id": durk.id, "durka1": durk.durka1, "durka2": durk.durka2})

    if len(dd) == 0:
        abort(404)

    return jsonify({'durkadurka': dd})


#
# Return a specific DurkaDurka given an id.
#
@app.route('/ddapi/v1.0/durkadurka/<int:dd_id>', methods=['GET'])
def get_dd_id(dd_id):
    dd = []
    for dt in session.query(DurkaDurka.id, DurkaDurka.durka1, DurkaDurka.durka2).filter(DurkaDurka.id == int(dd_id)):
        print dt
        dd.append({"id": dt.id, "durka1": dt.durka1, "durka2": dt.durka2})

    if len(dd) == 0:
        abort(404)
    return jsonify({'durkadurka': dd})


#
# Create a new DurkaDurka by posting it.
# TODO: Probably need some basic input validation on the stuff being passed in.
#
@app.route('/ddapi/v1.0/durkadurka', methods=['POST'])
def create_dd():
    if not request.json or 'durka1' not in request.json or 'durka2' not in request.json:
        abort(400)

    i2 = DurkaDurka(durka1=request.json['durka1'], durka2=request.json['durka2'])
    session.add(i2)
    session.commit()
    session.flush()

    #
    # I think this is where a declarative_base() may have come in handy--I could just create the .return_json()
    # function in the class instead of querying the DB and manually creating the JSON response here. :(
    #
    dq = session.query(DurkaDurka.id, DurkaDurka.durka1, DurkaDurka.durka2) \
        .filter(DurkaDurka.durka1 == request.json['durka1']) \
        .filter(DurkaDurka.durka2 == request.json['durka2']) \
        .one()
    session.flush()
    dd = {"id": dq.id, "durka1": dq.durka1, "durka2": dq.durka2}

    return jsonify({'durkadurka': dd}), 201


#
# Update a DurkaDurka's fields with some new data given a DurkaDurka id.
#
@app.route('/ddapi/v1.0/durkadurka/<int:dd_id>', methods=['PUT'])
def update_dd(dd_id):
    if not request.json or 'durka1' not in request.json or 'durka2' not in request.json:
        abort(400)

    q = session.query(DurkaDurka).filter(DurkaDurka.id == dd_id)
    record = q.one()
    record.durka1 = request.json['durka1']
    record.durka2 = request.json['durka2']
    session.commit()
    session.flush()
    # I'll have to come back to this, but postman responded quickly with this second .flush(), slow with the first.
    session.flush()

    #
    # TODO: I think I need to switch to a declarative_base() from the automap_base()
    # Again, the declarative_base() may have come in handy here--I could just create the .return_json()
    # function in the class instead of manually creating the JSON response here. :(
    #
    dd = {"id": dd_id, "durka1": request.json['durka1'], "durka2": request.json["durka2"]}

    return jsonify({'durkadurka': dd}), 201


#
# Route and Function to delete the DurkaDurka given a DurkaDurka id.
# TODO: session.flush() shouldn't be needed that many times.  Something in the DB is blocking the response, I'd guess...
#
@app.route('/ddapi/v1.0/durkadurka/<int:dd_id>', methods=['DELETE'])
def delete_dd(dd_id):
    d = session.query(DurkaDurka).filter(DurkaDurka.id == dd_id).one_or_none()
    session.flush()

    if d is None:
        session.flush()
        return jsonify({'result': False})
    else:
        try:
            session.delete(d)
            session.commit()
            session.flush()
            session.flush()  # Trying a second one to get a quick response back.
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
