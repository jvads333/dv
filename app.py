from flask import Flask, render_template, request, redirect, url_for, send_file, jsonify
from pymongo import MongoClient
from bson.objectid import ObjectId
import io

app = Flask(__name__)

# Connect to MongoDB
client = MongoClient('mongodb://localhost:27017/')
db = client['mydatabase']
users_collection = db['users']

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/submit', methods=['POST'])
def submit():
    name = request.form.get('name')
    email = request.form.get('email')
    profile_pic = request.files['profile_pic']
    
    # Read image data directly
    image_data = profile_pic.read()
    
    # Insert user data with image directly into MongoDB
    user_id = users_collection.insert_one({
        'name': name, 
        'email': email,
        'image': image_data
    }).inserted_id

    return redirect(url_for('index'))

@app.route('/search_ajax', methods=['GET'])
def search_ajax():
    search_name = request.args.get('search_name')
    user = users_collection.find_one({'name': search_name})

    if user:
        return jsonify({
            'found': True,
            'name': user['name'],
            'email': user['email'],
            'user_id': str(user['_id']),
            'has_image': 'image' in user and user['image'] is not None
        })
    else:
        return jsonify({
            'found': False
        })

@app.route('/image/<user_id>')
def image(user_id):
    user = users_collection.find_one({'_id': ObjectId(user_id)})
    if user and 'image' in user:
        return send_file(
            io.BytesIO(user['image']),
            mimetype='image/jpeg',
            as_attachment=False,
            download_name=f"{user_id}.jpg"
        )
    return "Image not found", 404

if __name__ == '__main__':
    app.run(debug=True)