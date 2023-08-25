from flask import Flask, jsonify, request
import os
from flask_sqlalchemy import SQLAlchemy
from flask_marshmallow import Marshmallow

app = Flask(__name__)

# Using os.path.abspath and os.path.join to construct the database URI
basedir = os.path.abspath(os.path.dirname(__file__))
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(basedir, 'db.sqlite')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)
ma = Marshmallow(app)

class Value(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    bbox = db.Column(db.String(100))
    slope = db.Column(db.Float)
    distance = db.Column(db.Float)

# Defining a schema for serialization using Marshmallow
class ValueSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = Value

value_schema = ValueSchema()
values_schema = ValueSchema(many=True)

@app.route('/', methods=['GET'])
def home():
    try:
        bbox = list(map(float, request.json['bbox']))
        slope = float(request.json['slope'])
        distance = float(request.json['distance'])
        
        annotation_lengths, size_cm2 = calculate_annotation_and_size(bbox, slope, distance)
        
        new_value = Value(bbox=str(bbox), slope=slope, distance=distance)
        db.session.add(new_value)
        db.session.commit()
        
        return jsonify({
            'bbox': bbox,
            'slope': slope,
            'distance': distance,
            'annotation_lengths': annotation_lengths,
            'size_cm2': size_cm2
        })
    except Exception as e:
        return jsonify({'error': str(e)})

def calculate_annotation_and_size(bbox, slope, distance):
    gsd = slope * distance
    annotation_lengths = [side * gsd for side in bbox]
    bbox_area = (bbox[2] - bbox[0]) * (bbox[3] - bbox[1]) * gsd
    return annotation_lengths, bbox_area

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)
