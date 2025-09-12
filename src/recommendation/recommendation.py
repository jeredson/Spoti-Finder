from textblob import TextBlob
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
import re

class TextEmotionDetector:
    def __init__(self):
        """Initialize text emotion detector"""
        self.analyzer = SentimentIntensityAnalyzer()
        
        # Emotion keywords mapping
        self.emotion_keywords = {
            'happy': ['happy', 'joy', 'excited', 'cheerful', 'delighted', 'glad', 'pleased', 'upbeat'],
            'sad': ['sad', 'depressed', 'down', 'melancholy', 'gloomy', 'sorrowful', 'blue', 'dejected'],
            'angry': ['angry', 'mad', 'furious', 'irritated', 'annoyed', 'rage', 'hostile', 'bitter'],
            'fear': ['afraid', 'scared', 'fearful', 'anxious', 'worried', 'nervous', 'terrified', 'panic'],
            'surprise': ['surprised', 'shocked', 'amazed', 'astonished', 'stunned', 'bewildered'],
            'disgust': ['disgusted', 'revolted', 'repulsed', 'sickened', 'nauseated'],
            'love': ['love', 'romantic', 'affection', 'adore', 'cherish', 'devoted'],
            'calm': ['calm', 'peaceful', 'relaxed', 'serene', 'tranquil', 'zen']
        }
        
        # Music feature mapping for emotions
        self.emotion_mapping = {
            'happy': {'valence': 0.8, 'energy': 0.7, 'danceability': 0.8, 'tempo': 120},
            'sad': {'valence': 0.2, 'energy': 0.3, 'danceability': 0.3, 'tempo': 80},
            'angry': {'valence': 0.1, 'energy': 0.9, 'danceability': 0.6, 'tempo': 140},
            'fear': {'valence': 0.2, 'energy': 0.4, 'danceability': 0.2, 'tempo': 90},
            'surprise': {'valence': 0.6, 'energy': 0.6, 'danceability': 0.7, 'tempo': 110},
            'disgust': {'valence': 0.3, 'energy': 0.4, 'danceability': 0.3, 'tempo': 95},
            'love': {'valence': 0.7, 'energy': 0.5, 'danceability': 0.6, 'tempo': 100},
            'calm': {'valence': 0.5, 'energy': 0.3, 'danceability': 0.4, 'tempo': 85},
            'neutral': {'valence': 0.5, 'energy': 0.5, 'danceability': 0.5, 'tempo': 110}
        }
    
    def preprocess_text(self, text):
        """Clean and preprocess text"""
        # Convert to lowercase
        text = text.lower()
        
        # Remove special characters but keep basic punctuation
        text = re.sub(r'[^\w\s.,!?]', '', text)
        
        return text.strip()
    
    def detect_emotion_from_text(self, text):
        """Detect emotion from text using multiple approaches"""
        try:
            if not text or not text.strip():
                return None, "Empty text provided"
            
            text = self.preprocess_text(text)
            
            # Method 1: VADER sentiment analysis
            sentiment_scores = self.analyzer.polarity_scores(text)
            
            # Method 2: TextBlob sentiment
            blob = TextBlob(text)
            textblob_polarity = blob.sentiment.polarity
            textblob_subjectivity = blob.sentiment.subjectivity
            
            # Method 3: Keyword-based emotion detection
            keyword_emotions = self._detect_emotions_by_keywords(text)
            
            # Combine methods to determine primary emotion
            primary_emotion = self._determine_primary_emotion(
                sentiment_scores, textblob_polarity, keyword_emotions
            )
            
            # Calculate confidence score
            confidence = self._calculate_confidence(sentiment_scores, keyword_emotions)
            
            return {
                'emotion': primary_emotion,
                'confidence': confidence,
                'sentiment_scores': sentiment_scores,
                'textblob_polarity': textblob_polarity,
                'textblob_subjectivity': textblob_subjectivity,
                'keyword_emotions': keyword_emotions,
                'music_features': self.emotion_mapping.get(primary_emotion, self.emotion_mapping['neutral'])
            }, None
            
        except Exception as e:
            return None, f"Error analyzing text emotion: {str(e)}"
    
    def _detect_emotions_by_keywords(self, text):
        """Detect emotions based on keyword presence"""
        emotion_scores = {}
        
        for emotion, keywords in self.emotion_keywords.items():
            score = 0
            for keyword in keywords:
                # Count occurrences of keyword in text
                count = text.count(keyword)
                score += count
            
            emotion_scores[emotion] = score
        
        return emotion_scores
    
    def _determine_primary_emotion(self, sentiment_scores, textblob_polarity, keyword_emotions):
        """Determine primary emotion from different analysis methods"""
        
        # Check if keywords strongly indicate an emotion
        max_keyword_emotion = max(keyword_emotions, key=keyword_emotions.get)
        max_keyword_score = keyword_emotions[max_keyword_emotion]
        
        if max_keyword_score > 0:
            return max_keyword_emotion
        
        # Fall back to sentiment analysis
        compound = sentiment_scores['compound']
        pos = sentiment_scores['pos']
        neg = sentiment_scores['neg']
        neu = sentiment_scores['neu']
        
        # Determine emotion based on sentiment scores
        if compound >= 0.5:
            return 'happy'
        elif compound <= -0.5:
            if neg > 0.5:
                return 'angry' if sentiment_scores['compound'] <= -0.7 else 'sad'
            else:
                return 'sad'
        elif compound > 0.1:
            return 'happy' if pos > neu else 'neutral'
        elif compound < -0.1:
            return 'sad'
        else:
            return 'neutral'
    
    def _calculate_confidence(self, sentiment_scores, keyword_emotions):
        """Calculate confidence score for emotion detection"""
        # Base confidence on VADER compound score
        base_confidence = abs(sentiment_scores['compound'])
        
        # Boost confidence if keywords are present
        max_keyword_score = max(keyword_emotions.values()) if keyword_emotions else 0
        keyword_boost = min(max_keyword_score * 0.1, 0.3)  # Max 30% boost
        
        confidence = min(base_confidence + keyword_boost, 1.0)
        
        return round(confidence, 3)
    
    def analyze_mood_from_playlist_name(self, playlist_name):
        """Analyze mood from playlist name or description"""
        return self.detect_emotion_from_text(playlist_name)
    
    def get_music_features_for_emotion(self, emotion):
        """Get music features for a specific emotion"""
        return self.emotion_mapping.get(emotion.lower(), self.emotion_mapping['neutral'])