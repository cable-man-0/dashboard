from flask import Flask, request, jsonify
from algorithms.dbscan import detect_anomalies_dbscan
from algorithms.svm import detect_anomalies_svm
from algorithms.isolation_forest import detect_anomalies_iforest
import logging
import pandas as pd
import hashlib
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime, timedelta
import uuid
import paho.mqtt.client as mqtt
import json

logging.basicConfig(level=logging.DEBUG)

def make_hashes(password):
    return hashlib.sha256(str.encode(password)).hexdigest()

def check_hashes(hashed_text, password):
    """Compare a hashed password with a plain text password."""
    return hashlib.sha256(str.encode(password)).hexdigest() == hashed_text

#db = SQLAlchemy()



app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///new_database.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

class User(db.Model):
    __tablename__ = 'User'

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    password = db.Column(db.String(100), nullable=False)

    def __repr__(self):
        return f"User('{self.username}')"

class Token(db.Model):
    __tablename__ = 'Token'

    token = db.Column(db.String, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('User.id'), nullable=False)
    expiration = db.Column(db.DateTime, nullable=False)

with app.app_context():
    db.create_all()

def generate_token(user_id):
    expiration_time = datetime.utcnow() + timedelta(minutes=30)
    token = str(uuid.uuid4())
    token_data = {
        'user_id': user_id,
        'expiration': expiration_time
    }
    db.session.add(Token(token=token, **token_data))
    db.session.commit()
    return token

def on_connect(client, userdata, flags, rc, topic):
    if rc == 0:
        logging.info(f'Connected successfully with result code {rc}')
        client.payload = client.subscribe(topic)
    else:
        logging.error(f'Connection failed with result code {rc}')

def on_message(client, userdata, msg):
    payload = str(msg.payload.decode("utf-8"))
    if payload:
        try:
            message_json = json.loads(payload)
            userdata['payload'] = message_json
            return message_json
        except json.JSONDecodeError:
            logging.warning("Failed to parse payload as JSON.")
            userdata['payload'] = None
            return None
    logging.info("Received payload: %s", payload)
    return None


@app.route('/register', methods=['POST'])
def register():
    username = request.json['username']
    password = request.json['password']

    if not username or not password:
        logging.error('Invalid user input.')
        return 'Invalid user input.', 400

    user = User.query.filter_by(username=username).first()
    if user:
        logging.error(f'Username {username} already exists.')
        return 'Username already exists.', 409

    hashed_password = make_hashes(password)
    new_user = User(username=username, password=hashed_password)
    db.session.add(new_user)
    db.session.commit()

    logging.info(f'User {username} registered successfully.')
    return 'User account created successfully.', 201

@app.route('/login', methods=['POST'])
def login():
    username = request.json['username']
    password = request.json['password']

    if not username or not password:
        logging.error('Invalid user input.')
        return 'Invalid user input.', 400

    user = User.query.filter_by(username=username).first()
    if not user:
        logging.error(f'User {username} not found.')
        return 'User not found.', 404

    if not check_hashes(user.password, password):
        logging.error(f'Invalid password for user {username}.')
        return 'Invalid password.', 401

    token = generate_token(user.id)

    logging.info(f'User {username} logged in successfully.')
    return jsonify({'token': token}), 200

@app.route('/update_user', methods=['PUT'])
def update_user():
    try:
        if request.headers['Content-Type'] != 'application/json':
            logging.error('Verify the data format is in JSON')
            return jsonify({'error': 'Invalid content type. Expected JSON data.'}), 400

        data = request.get_json()
        if not data or 'username' not in data or 'password' not in data:
            logging.error('Invalid JSON format. Expected "username" and "password" keys.')
            return jsonify({'error': 'Invalid JSON format. Expected "username" and "password" keys.'}), 400

        username = data['username']
        new_hashed_password = make_hashes(data['password'])

        user = User.query.filter_by(username=username).first()
        if not user:
            logging.error(f'User {username} not found.')
            return jsonify({'error': 'User not found.'}), 404

        user.password = new_hashed_password
        db.session.commit()

        logging.info(f'User {username} updated successfully.')
        return jsonify({'message': 'User updated successfully.'}), 200
    except Exception as e:
        logging.error(f'An error occurred: {str(e)}')
        return jsonify({'error': str(e)}), 500

@app.route('/detect_anomalies', methods=['POST'])
def detect_anomalies():
    try:
        if request.headers['Content-Type'] != 'application/json':
            logging.error('Verify the data format is in JSON')
            return jsonify({'error': 'Invalid content type. Expected JSON data.'}), 400

        data = request.json
        if 'data' not in data or 'algorithm' not in data:
            logging.error('Invalid JSON format. Expected "data" and "algorithm" keys.')
            return jsonify({'error': 'Invalid JSON format. Expected "data" and "algorithm" keys.'}), 400

        df = pd.DataFrame(data['data'])
        algorithm = data['algorithm']
        parameters = data.get('parameters', {})

        if algorithm == 'isolation_forest':
            anomaly_indices = detect_anomalies_iforest(df, **parameters)
        elif algorithm == 'SVM':
            anomaly_indices = detect_anomalies_svm(df, **parameters)
        elif algorithm == 'DBSCAN':
            anomaly_indices = detect_anomalies_dbscan(df, **parameters)
        else:
            logging.error('Invalid algorithm specified')
            return jsonify({'error': 'Invalid algorithm specified.'}), 400

        if anomaly_indices is None:
            logging.error('An error occurred while detecting anomalies.')
            return jsonify({'error': 'An error occurred while detecting anomalies.'}), 500

        logging.info('Success')
        return jsonify(anomaly_indices), 200
    except Exception as e:
        logging.error(f'An error occurred: {str(e)}')
        return jsonify({'error': str(e)}), 500



@app.route('/subscribe_mqtt_topic', methods=['POST'])
def subscribe_mqtt_topic():
    try:
        if request.headers['Content-Type'] != 'application/json':
            logging.error('Verify the data format is in JSON')
            return jsonify({'error': 'Invalid content type. Expected JSON data.'}), 400

        data = request.json
        broker = data["broker"]
        topic = data["topic"]
        port = data["port"]

        userdata = {'payload': None}  # Initialize a userdata dictionary
        
        client = mqtt.Client()  # Initialize client
        client.user_data_set(userdata)  # Set the userdata dictionary
        
        client.on_connect = lambda client, userdata, flags, rc, topic=topic: on_connect(client, userdata, flags, rc, topic)
        client.on_message = on_message
        
        try:
            client.connect(broker, port)
            client.loop_start()  # Start loop in non-blocking mode
          
            payload = userdata.get('payload')
            client.disconnect()  # Disconnect MQTT client
            
            return jsonify({'message': 'Successfully subscribed to the MQTT topic.', 'payload': payload}), 200
        except Exception as e:
            logging.error(f'An error occurred while connecting to MQTT broker: {str(e)}')
            return jsonify({'error': f'An error occurred while connecting to MQTT broker: {str(e)}'}), 500
    except Exception as e:
        logging.error(f'An error occurred: {str(e)}')
        return jsonify({'error': str(e)}), 500




if __name__ == '__main__':
    app.run(debug=True)
    