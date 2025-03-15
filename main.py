from flask import Flask, request, jsonify
from flask_cors import CORS
import os

app = Flask(__name__)
CORS(app)  # Allow cross-origin requests

@app.route('/scrape', methods=['POST'])
def scrape():
    data = request.get_json()
    if not data:
        return jsonify({'error': 'No JSON data received'}), 400

    username = data.get('username')
    password = data.get('password')
    target_percentage = data.get('targetPercentage')

    if not username or not password or target_percentage is None:
        return jsonify({'error': 'Missing required fields'}), 400

    # Simulated data for now
    scraped_data = [
        ["Course 1", "80%"],
        ["Course 2", "75%"],
        ["Course 3", "90%"]
    ]
    
    return jsonify({'data': scraped_data})

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))  # Use Render's assigned port
    app.run(host='0.0.0.0', port=port)
