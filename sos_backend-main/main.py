from flask import Flask, request, jsonify
from twilio.rest import Client
import geocoder
from flask_cors import CORS
from os import environ
import os  # Add this import for accessing environment variables
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)
CORS(app)  # Enable CORS for the Flask app

# Twilio settings
account_sid = str(environ.get("ACCOUNT_ID"))  # Your Twilio Account SID
auth_token = str(environ.get("AUTH_ID"))      # Your Twilio Auth Token
twilio_phone_number = str(environ.get("TWILIO_NUM"))
destination_number = str(environ.get("SEND_NUM"))  # Twilio phone number

@app.route('/')
def hello():
    return 'Hello, World!'

# Function to send SMS via Twilio
def send_sms(location, message):
    client = Client(account_sid, auth_token)
    try:
        client.messages.create(
            body=f"Emergency Alert!\nLocation: {location}\nMessage: {message}",
            from_=twilio_phone_number,
            to=destination_number
        )
        return True
    except Exception as e:
        print(f"Failed to send SMS: {e}")
        return False

@app.route('/send_sos', methods=['POST'])
def send_sos():
    data = request.json
    message = data.get('message', 'Emergency SOS')  # Default message if not provided

    # Get the location (use GPS data from Flutter, fallback to IP geolocation for testing)
    location = data.get('location', None)
    if not location:  # If location isn't sent, fallback to approximate IP geolocation
        g = geocoder.ip('me')  # Replace this with actual GPS location from the frontend
        location = g.latlng if g else 'Unknown Location'

    # Send the SMS message
    if send_sms(location, message):
        return jsonify({'status': 'success', 'message': 'SOS sent successfully!'}), 200
    else:
        return jsonify({'status': 'error', 'message': 'Failed to send SOS'}), 500

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8080))  # Default to 8080 if PORT not set
    app.run(host="0.0.0.0", port=port)
