#!/usr/bin/env python3
"""
Spotify Music Recommender Based on Human Emotion
Main entry point for the application
"""

import os
import sys
import argparse

# Add src directory to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

def setup_environment():
    """Setup environment and check dependencies"""
    try:
        # Check if .env file exists
        env_file = os.path.join(os.path.dirname(__file__), '.env')
        if not os.path.exists(env_file):
            print("❌ .env file not found. Please create one with your Spotify credentials.")
            return False
        
        # Import required modules
        from emotion_detection.face_emotion import FaceEmotionDetector
        from emotion_detection.text_emotion import TextEmotionDetector
        from music_analysis.spotify_client import SpotifyClient
        from recommendation.recommender import EmotionBasedRecommender
        
        print("✅ All modules imported successfully")
        return True
        
    except ImportError as e:
        print(f"❌ Import error: {e}")
        print("Please install required dependencies: pip install -r requirements.txt")
        return False
    except Exception as e:
        print(f"❌ Setup error: {e}")
        return False

def test_text_emotion(text):
    """Test text emotion analysis"""
    print(f"\n📝 Analyzing text: '{text}'")
    
    try:
        from emotion_detection.text_emotion import TextEmotionDetector
        
        detector = TextEmotionDetector()
        result, error = detector.detect_emotion_from_text(text)
        
        if error:
            print(f"❌ Error: {error}")
            return None
        
        print(f"✅ Detected emotion: {result['emotion']} (confidence: {result['confidence']:.1%})")
        print(f"🎵 Music features for this emotion:")
        for feature, value in result['music_features'].items():
            print(f"   {feature}: {value}")
        
        return result
        
    except Exception as e:
        print(f"❌ Error in text emotion analysis: {e}")
        return None

def test_face_emotion(image_path):
    """Test face emotion analysis"""
    print(f"\n📷 Analyzing image: {image_path}")
    
    try:
        from emotion_detection.face_emotion import FaceEmotionDetector
        
        detector = FaceEmotionDetector()
        result, error = detector.detect_emotion_from_image(image_path)
        
        if error:
            print(f"❌ Error: {error}")
            return None
        
        print(f"✅ Detected emotion: {result['emotion']} (confidence: {result['confidence']:.1%})")
        print(f"🎵 Music features for this emotion:")
        for feature, value in result['music_features'].items():
            print(f"   {feature}: {value}")
        
        return result
        
    except Exception as e:
        print(f"❌ Error in face emotion analysis: {e}")
        return None

def test_music_recommendations(emotion_result, num_recommendations=10):
    """Test music recommendations based on emotion analysis"""
    print(f"\n🎵 Getting music recommendations...")
    
    try:
        from music_analysis.spotify_client import SpotifyClient
        from recommendation.recommender import EmotionBasedRecommender
        
        spotify_client = SpotifyClient()
        recommender = EmotionBasedRecommender(spotify_client)
        
        print("📚 Building track database...")
        recommender.build_track_database(use_cached=True)
        
        print("🤖 Loading recommendation model...")
        recommender.load_model()
        
        # Get recommendations
        music_features = emotion_result['music_features']
        recommendations = recommender.recommend_by_emotion(music_features, num_recommendations)
        
        if not recommendations:
            print("❌ No recommendations found")
            return
        
        print(f"✅ Found {len(recommendations)} recommendations:")
        print("=" * 60)
        
        for i, track in enumerate(recommendations[:10], 1):
            print(f"{i:2d}. {track['name']}")
            print(f"    🎤 Artist: {track['artist']}")
            if track.get('album'):
                print(f"    💿 Album: {track['album']}")
            if track.get('popularity'):
                print(f"    📈 Popularity: {track['popularity']}%")
            if track.get('similarity_score'):
                print(f"    💖 Match: {track['similarity_score']:.1%}")
            if track.get('external_url'):
                print(f"    🔗 Spotify: {track['external_url']}")
            print()
        
    except Exception as e:
        print(f"❌ Error getting recommendations: {e}")

def run_web_app():
    """Run the Flask web application"""
    print("\n🌐 Starting web application...")
    
    try:
        from web_app.app import app
        print("✅ Web app starting at http://localhost:5000")
        app.run(debug=True, host='0.0.0.0', port=5000)
    except Exception as e:
        print(f"❌ Error starting web app: {e}")

def main():
    """Main function"""
    parser = argparse.ArgumentParser(description='Spotify Music Recommender Based on Human Emotion')
    parser.add_argument('--text', type=str, help='Analyze emotion from text')
    parser.add_argument('--image', type=str, help='Analyze emotion from image file')
    parser.add_argument('--web', action='store_true', help='Run web application')
    parser.add_argument('--setup', action='store_true', help='Setup and test environment')
    
    args = parser.parse_args()
    
    print("=" * 60)
    print("🎵 SPOTIFY MUSIC RECOMMENDER BASED ON HUMAN EMOTION 🎵")
    print("=" * 60)
    
    if not setup_environment():
        return
    
    if args.setup:
        print("🎉 Environment setup complete!")
        return
    
    if args.web:
        run_web_app()
        return
    
    if args.text:
        result = test_text_emotion(args.text)
        if result:
            test_music_recommendations(result)
        return
    
    if args.image:
        if not os.path.exists(args.image):
            print(f"❌ Image file not found: {args.image}")
            return
        
        result = test_face_emotion(args.image)
        if result:
            test_music_recommendations(result)
        return
    
    # Default: run web app
    run_web_app()

if __name__ == "__main__":
    main()