from flask import Flask, render_template, request, jsonify, send_from_directory
import os
import sys
import json
import base64
from werkzeug.utils import secure_filename

# Add parent directories to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from emotion_detection.face_emotion import FaceEmotionDetector
from emotion_detection.text_emotion import TextEmotionDetector
from music_analysis.spotify_client import SpotifyClient
from recommendation.recommender import EmotionBasedRecommender

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your-secret-key-here'
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size

# Ensure upload directory exists
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

# Initialize components
try:
    spotify_client = SpotifyClient()
    face_detector = FaceEmotionDetector()
    text_detector = TextEmotionDetector()
    recommender = EmotionBasedRecommender(spotify_client)
    
    # Build/load track database
    recommender.build_track_database()
    recommender.load_model()
    
    print("All components initialized successfully!")
except Exception as e:
    print(f"Error initializing components: {e}")
    spotify_client = None
    face_detector = None
    text_detector = None
    recommender = None

@app.route('/')
def index():
    """Main page"""
    return render_template('index.html')

@app.route('/face-detection')
def face_detection():
    """Face emotion detection page"""
    return render_template('face_detection.html')

@app.route('/text-analysis')
def text_analysis():
    """Text emotion analysis page"""
    return render_template('text_analysis.html')

@app.route('/api/analyze-text', methods=['POST'])
def analyze_text_emotion():
    """API endpoint for text emotion analysis"""
    try:
        data = request.get_json()
        text = data.get('text', '')
        
        if not text.strip():
            return jsonify({'error': 'No text provided'}), 400
        
        # Analyze emotion
        emotion_result, error = text_detector.detect_emotion_from_text(text)
        
        if error:
            return jsonify({'error': error}), 400
        
        # Get recommendations
        recommendations = recommender.recommend_by_text_emotion(emotion_result, 15)
        
        response = {
            'emotion_analysis': emotion_result,
            'recommendations': recommendations
        }
        
        return jsonify(response)
        
    except Exception as e:
        return jsonify({'error': f'Server error: {str(e)}'}), 500

@app.route('/api/analyze-image', methods=['POST'])
def analyze_image_emotion():
    """API endpoint for image emotion analysis"""
    try:
        # Handle file upload
        if 'image' in request.files:
            file = request.files['image']
            if file.filename == '':
                return jsonify({'error': 'No file selected'}), 400
            
            # Save uploaded file
            filename = secure_filename(file.filename)
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(filepath)
            
            # Analyze emotion
            emotion_result, error = face_detector.detect_emotion_from_image(filepath)
            
            # Clean up uploaded file
            try:
                os.remove(filepath)
            except:
                pass
        
        # Handle base64 image data
        elif request.json and 'image_data' in request.json:
            image_data = request.json['image_data']
            emotion_result, error = face_detector.detect_emotion_from_base64(image_data)
        
        else:
            return jsonify({'error': 'No image data provided'}), 400
        
        if error:
            return jsonify({'error': error}), 400
        
        # Get recommendations
        recommendations = recommender.recommend_by_face_emotion(emotion_result, 15)
        
        response = {
            'emotion_analysis': emotion_result,
            'recommendations': recommendations
        }
        
        return jsonify(response)
        
    except Exception as e:
        return jsonify({'error': f'Server error: {str(e)}'}), 500

@app.route('/api/search-tracks')
def search_tracks():
    """API endpoint for searching tracks"""
    try:
        query = request.args.get('q', '')
        limit = int(request.args.get('limit', 10))
        
        if not query:
            return jsonify({'error': 'No search query provided'}), 400
        
        tracks = spotify_client.search_tracks(query, limit=limit)
        
        # Format track data
        formatted_tracks = []
        for track in tracks:
            formatted_tracks.append({
                'id': track['id'],
                'name': track['name'],
                'artist': track['artists'][0]['name'] if track['artists'] else 'Unknown',
                'album': track['album']['name'],
                'preview_url': track['preview_url'],
                'external_url': track['external_urls']['spotify'],
                'image': track['album']['images'][0]['url'] if track['album']['images'] else None
            })
        
        return jsonify({'tracks': formatted_tracks})
        
    except Exception as e:
        return jsonify({'error': f'Server error: {str(e)}'}), 500

@app.route('/api/similar-tracks/<track_id>')
def get_similar_tracks(track_id):
    """API endpoint for getting similar tracks"""
    try:
        num_recommendations = int(request.args.get('limit', 10))
        similar_tracks = recommender.get_similar_tracks(track_id, num_recommendations)
        
        return jsonify({'tracks': similar_tracks})
        
    except Exception as e:
        return jsonify({'error': f'Server error: {str(e)}'}), 500

@app.route('/api/emotion-stats')
def get_emotion_stats():
    """API endpoint for emotion distribution statistics"""
    try:
        stats = recommender.analyze_emotion_distribution()
        return jsonify(stats)
        
    except Exception as e:
        return jsonify({'error': f'Server error: {str(e)}'}), 500

@app.route('/api/recommend-by-features', methods=['POST'])
def recommend_by_features():
    """API endpoint for custom feature-based recommendations"""
    try:
        data = request.get_json()
        features = data.get('features', {})
        num_recommendations = data.get('limit', 15)
        
        recommendations = recommender.recommend_by_emotion(features, num_recommendations)
        
        return jsonify({'recommendations': recommendations})
        
    except Exception as e:
        return jsonify({'error': f'Server error: {str(e)}'}), 500

@app.errorhandler(413)
def too_large(e):
    return jsonify({'error': 'File too large'}), 413

@app.errorhandler(404)
def not_found(e):
    return render_template('404.html'), 404

@app.errorhandler(500)
def server_error(e):
    return jsonify({'error': 'Internal server error'}), 500

if __name__ == '__main__':
    # Check if components are initialized
    if not all([spotify_client, face_detector, text_detector, recommender]):
        print("Warning: Some components failed to initialize. Please check your configuration.")
    
    app.run(debug=True, host='0.0.0.0', port=5000)