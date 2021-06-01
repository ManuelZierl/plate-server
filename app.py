from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

from errors import handle_err, NotAPlate, WrongRequest
from utils import is_german_plate, levenshtein_distance

app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.register_error_handler(NotAPlate, handle_err)
app.register_error_handler(WrongRequest, handle_err)
db = SQLAlchemy(app)


class Plate(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    timestamp = db.Column(db.DateTime, default=datetime.now)
    plate_str = db.Column(db.String(9), nullable=False)


@app.route("/plate", methods=["POST", "GET"])
def _plate():
    if request.method == "POST":
        if plate_str := request.form.get("plate"):
            plate_str = plate_str.upper()
            if not is_german_plate(plate_str):
                raise NotAPlate()
            plate = Plate(plate_str=plate_str)
            db.session.add(plate)
            db.session.commit()
            return jsonify({"success": True,
                            "plate": plate_str,
                            "timestamp": plate.timestamp.strftime('%Y-%m-%dT%H:%M:%SZ'),
                            "code": 200})
        else:
            raise WrongRequest()

    elif request.method == "GET":
        all_plates = Plate.query.all()
        all_plates = [{"plate": x.plate_str, "timestamp": x.timestamp.strftime("%Y-%m-%dT%H:%M:%SZ")}
                      for x in all_plates]
        return jsonify(all_plates)

    raise WrongRequest()


@app.route("/search-plate", methods=["GET"])
def plate_search():
    key = request.args.get("key")
    levenshtein = request.args.get("levenshtein", "x")
    levenshtein = int(levenshtein) if levenshtein.isdigit() else None

    if key is not None and levenshtein is not None:
        all_plates = Plate.query.all()
        all_plates = [{"_plate": x.plate_str.replace("-", ""), "plate": x.plate_str,
                       "timestamp": x.timestamp.strftime("%Y-%m-%dT%H:%M:%SZ")}
                      for x in all_plates]

        filtered_plates = [dict(x, **{"dist": dist}) for x in all_plates if
                           (dist := levenshtein_distance(x["_plate"], key)) <= levenshtein]
        return jsonify({key: filtered_plates})
    raise WrongRequest()


if __name__ == "__main__":
    app.run(debug=True, host='0.0.0.0')
