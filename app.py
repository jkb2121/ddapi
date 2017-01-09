#!flask/bin/python
from sqlalchemy import create_engine
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import scoped_session, sessionmaker

from flask import Flask, jsonify
from flask import request, abort, make_response

app = Flask(__name__)
# ----------------------------------------------------------------------------------------------------------------------
engine = create_engine('mysql+pymysql://kitflask:TPjbaX50bq3s0EJ6@localhost/kits', convert_unicode=True,
                       echo=True, encoding="ISO-8859-1")

Base = automap_base()
Base.prepare(engine, reflect=True)
DurkaDurka = Base.classes.durkadurka

session = scoped_session(sessionmaker(bind=engine))


# ----------------------------------------------------------------------------------------------------------------------
@app.errorhandler(404)
def not_found(error):
    return make_response(jsonify({'error': 'Not found'}), 404)


@app.route('/ddapi/v1.0/durkadurka', methods=['GET'])
def get_dd():
    dd = []
    for durk in session.query(DurkaDurka.id, DurkaDurka.durka1, DurkaDurka.durka2):
        dd.append({"id": durk[0], "durka1": durk[1], "durka2": durk[2]})

    if len(dd) == 0:
        abort(404)

    return jsonify({'durkadurka': dd})


@app.route('/ddapi/v1.0/durkadurka/<int:dd_id>', methods=['GET'])
def get_dd_id(dd_id):
    dd = []
    for dt in session.query(DurkaDurka.id, DurkaDurka.durka1, DurkaDurka.durka2).filter(DurkaDurka.id == int(dd_id)):
        print dt
        dd.append({"id": dt[0], "durka1": dt[1], "durka2": dt[2]})

    if len(dd) == 0:
        abort(404)
    return jsonify({'durkadurka': dd})


@app.route('/ddapi/v1.0/durkadurka', methods=['POST'])
def create_dd():
    if not request.json or not 'durka1' or not 'durka2' in request.json:
        abort(400)

    i2 = DurkaDurka(durka1=request.json['durka1'], durka2=request.json['durka2'])
    session.add(i2)
    session.commit()
    session.flush()

    #
    # I think this is where a declarative_base() may have come in handy--I could just create the .return_json()
    # function in the class instead of querying the DB and manually creating the JSON response here. :(
    #
    id = session.query(DurkaDurka.id, DurkaDurka.durka1, DurkaDurka.durka2) \
        .filter(DurkaDurka.durka1 == request.json['durka1']) \
        .filter(DurkaDurka.durka2 == request.json['durka2']) \
        .one()
    session.flush()
    dd = {"id": id.id, "durka1": id.durka1, "durka2": id.durka2}

    return jsonify({'durkadurka': dd}), 201


@app.route('/ddapi/v1.0/durkadurka/<int:dd_id>', methods=['PUT'])
def update_dd(dd_id):
    if not request.json or not 'durka1' or not 'durka2' in request.json:
        abort(400)

    q = session.query(DurkaDurka).filter(DurkaDurka.id == dd_id)
    record = q.one()
    record.durka1 = request.json['durka1']
    record.durka2 = request.json['durka2']
    session.commit()
    session.flush()
    session.flush()  # I'll have to come back to this, but postman responded quickly with this second .flush(), slow with the first.

    #
    # Again, the declarative_base() may have come in handy here--I could just create the .return_json()
    # function in the class instead of manually creating the JSON response here. :(
    #
    dd = {"id": dd_id, "durka1": request.json['durka1'], "durka2": request.json["durka2"]}

    return jsonify({'durkadurka': dd}), 201


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


@app.route('/')
def index():
    return "DurkaDurka API"


# ----------------------------------------------------------------------------------------------------------------------
if __name__ == '__main__':
    app.run(debug=True)
