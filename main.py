#!/usr/bin/env python3
"""
Spotify Music Recommender Based on Human Emotion
Main script to run the complete application

This script initializes all components and provides a command-line interface
for testing the emotion detection and music recommendation system.
"""

import os
import sys
import argparse
from pathlib import Path

# Add src directory to path
src_path = Path(__file__).parent / 'src'
sys.path.insert(0, str(src_path))

try:
    from emotion_detection.face_emotion import FaceEmotionDetector
    from emotion_detection.text_emotion import TextEmotionDetector
    from music_analysis.spotify_client import SpotifyClient
    from recommendation.recommender import EmotionBasedRecommender
except ImportError as e:
    print(f"Error importing modules: {e}")
    print("Please make sure all required packages are installed:")
    print("pip install -r requirements.txt")
    sys.exit(1)

def setup_environment():
    """Setup environment and check for required configurations"""
    # Check for .env file
    if not os.path.exists('.env'):
        print("⚠️  .env file not found!")
        print("Please create a .env file with your Spotify API credentials:")
        print("SPOTIFY_CLIENT_ID=your_client_id")
        print("SPOTIFY_CLIENT_SECRET=your_client_secret")
        return False
    
    # Check for required directories
    os.makedirs('data', exist_ok=True)
    os.makedirs('models', exist_ok=True)
    os.makedirs('uploads', exist_ok=True)
    
    return True

def test_face_emotion(image_path):
    """Test face emotion detection with an image"""
    print(f"\n🔍 Analyzing facial emotion in: {image_path}")
    
    try:
        detector = FaceEmotionDetector()
        result, error = detector.detect_emotion_from_image(image_path)
        
        if error:
            print(f"❌ Error: {error}")
            return None
        
        print(f"✅ Detected Emotion: {result['emotion'].upper()}")
        print(f"📊 Confidence: {result['confidence']:.2%}")
        print("📈 All emotions:")
        for emotion, score in result['all_emotions'].items():
            print(f"   {emotion}: {score:.2%}")
        
        print("🎵 Music features for this emotion:")
        for feature, value in result['music_features'].items():
            print(f"   {feature}: {value}")
        
        return result
        
    except Exception as e:
        print(f"❌ Error in face emotion detection: {e}")
        return None

def test_text_emotion(text):
    """Test text emotion analysis"""
    print(f"\n📝 Analyzing text emotion: '{text[:50]}...'")
    
    try:
        detector = TextEmotionDetector()
        result, error = detector.detect_emotion_from_text(text)
        
        if error:
            print(f"❌ Error: {error}")
            return None
        
        print(f"✅ Detected Emotion: {result['emotion'].upper()}")
        print(f"📊 Confidence: {result['confidence']:.2%}")
        print(f"💭 Sentiment Score: {result['sentiment_scores']['compound']:.3f}")
        
        print("🎵 Music features for this emotion:")
        for feature, value in result['music_features'].items():
            print(f"   {feature}: {value}")
        
        return result
        
    except Exception as e:
        print(f"❌ Error in text emotion analysis: {e}")
        return None

def test_music_recommendations(emotion_result, num_recommendations=10):
    """Test music recommendations based on emotion analysis"""
    print(f"\n🎵 Getting music recommendations...")
    
    try:
        # Initialize Spotify client and recommender
        spotify_client = SpotifyClient()
        recommender = EmotionBasedRecommender(spotify_client)
        
        print("📚 Building track database (this may take a while on first run)...")
        recommender.build_track_database(use_cached=True)
        
        print("🤖 Loading/training recommendation model...")
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

def interactive_mode():
    """Run interactive mode for testing"""
    print("\n🎯 Interactive Mode")
    print("Choose an option:")
    print("1. Analyze text emotion")
    print("2. Analyze face emotion (from image)")
    print("3. Get music recommendations")
    print("4. Run web application")
    print("5. Exit")
    
    while True:
        try:
            choice = input("\nEnter your choice (1-5): ").strip()
            
            if choice == '1':
                text = input("Enter text to analyze: ").strip()
                if text:
                    result = test_text_emotion(text)
                    if result:
                        get_recs = input("Get music recommendations? (y/n): ").strip().lower()
                        if get_recs == 'y':
                            test_music_recommendations(result)
                
            elif choice == '2':
                image_path = input("Enter image path: ").strip()
                if os.path.exists(image_path):
                    result = test_face_emotion(image_path)
                    if result:
                        get_recs = input("Get music recommendations? (y/n): ").strip().lower()
                        if get_recs == 'y':
                            test_music_recommendations(result)
                else:
                    print("❌ Image file not found")
                
            elif choice == '3':
                print("Select emotion for recommendations:")
                emotions = ['happy', 'sad', 'angry', 'calm', 'energetic']
                for i, emotion in enumerate(emotions, 1):
                    print(f"{i}. {emotion.title()}")
                
                try:
                    emotion_choice = int(input("Choose emotion (1-5): ")) - 1
                    if 0 <= emotion_choice < len(emotions):
                        # Create mock emotion result
                        emotion_mappings = {
                            'happy': {'valence': 0.8, 'energy': 0.7, 'danceability': 0.8},
                            'sad': {'valence': 0.2, 'energy': 0.3, 'danceability': 0.3},
                            'angry': {'valence': 0.1, 'energy': 0.9, 'danceability': 0.6},
                            'calm': {'valence': 0.5, 'energy': 0.3, 'danceability': 0.4},
                            'energetic': {'valence': 0.7, 'energy': 0.9, 'danceability': 0.9}
                        }
                        
                        selected_emotion = emotions[emotion_choice]
                        mock_result = {
                            'emotion': selected_emotion,
                            'confidence': 0.8,
                            'music_features': emotion_mappings[selected_emotion]
                        }
                        test_music_recommendations(mock_result)
                    else:
                        print("❌ Invalid choice")
                except ValueError:
                    print("❌ Please enter a number")
                
            elif choice == '4':
                run_web_app()
                break
                
            elif choice == '5':
                print("👋 Goodbye!")
                break
                
            else:
                print("❌ Invalid choice. Please enter 1-5.")
                
        except KeyboardInterrupt:
            print("\n👋 Goodbye!")
            break
        except Exception as e:
            print(f"❌ Error: {e}")

def main():
    """Main function"""
    parser = argparse.ArgumentParser(description='Spotify Music Recommender Based on Human Emotion')
    parser.add_argument('--text', type=str, help='Analyze emotion from text')
    parser.add_argument('--image', type=str, help='Analyze emotion from image file')
    parser.add_argument('--web', action='store_true', help='Run web application')
    parser.add_argument('--interactive', action='store_true', help='Run in interactive mode')
    parser.add_argument('--setup', action='store_true', help='Setup and test environment')
    parser.add_argument('--recommendations', type=int, default=10, help='Number of recommendations to show')
    
    args = parser.parse_args()
    
    # Print welcome message
    print("=" * 60)
    print("🎵 SPOTIFY MUSIC RECOMMENDER BASED ON HUMAN EMOTION 🎵")
    print("=" * 60)
    print("Final Year Project - AI Music Recommendation System")
    print()
    
    # Setup environment
    if not setup_environment():
        return
    
    # Handle different modes
    if args.setup:
        print("🔧 Testing environment setup...")
        
        # Test imports
        try:
            print("✅ All modules imported successfully")
            
            # Test Spotify connection
            spotify_client = SpotifyClient()
            print("✅ Spotify API connection successful")
            
            # Test emotion detectors
            face_detector = FaceEmotionDetector()
            text_detector = TextEmotionDetector()
            print("✅ Emotion detectors initialized successfully")
            
            print("🎉 Environment setup complete!")
            
        except Exception as e:
            print(f"❌ Setup error: {e}")
        
        return
    
    if args.web:
        run_web_app()
        return
    
    if args.text:
        result = test_text_emotion(args.text)
        if result:
            test_music_recommendations(result, args.recommendations)
        return
    
    if args.image:
        if not os.path.exists(args.image):
            print(f"❌ Image file not found: {args.image}")
            return
        
        result = test_face_emotion(args.image)
        if result:
            test_music_recommendations(result, args.recommendations)
        return
    
    if args.interactive:
        interactive_mode()
        return
    
    # Default: show help
    parser.print_help()
    print("\nExamples:")
    print("  python main.py --setup                           # Test environment setup")
    print("  python main.py --web                             # Run web application")
    print("  python main.py --interactive                     # Interactive mode")
    print("  python main.py --text 'I am feeling happy!'     # Analyze text emotion")
    print("  python main.py --image photo.jpg                # Analyze face emotion")
    print()
    print("For the full web experience, run: python main.py --web")

if __name__ == "__main__":
    main()