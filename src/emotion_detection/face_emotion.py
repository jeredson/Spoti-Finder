import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
import pandas as pd
import os
from dotenv import load_dotenv

load_dotenv()

class SpotifyClient:
    def __init__(self):
        """Initialize Spotify client with credentials"""
        client_id = os.getenv('SPOTIFY_CLIENT_ID')
        client_secret = os.getenv('SPOTIFY_CLIENT_SECRET')
        
        if not client_id or not client_secret:
            raise ValueError("Please set SPOTIFY_CLIENT_ID and SPOTIFY_CLIENT_SECRET in .env file")
        
        client_credentials_manager = SpotifyClientCredentials(
            client_id=client_id,
            client_secret=client_secret
        )
        
        self.sp = spotipy.Spotify(client_credentials_manager=client_credentials_manager)
    
    def search_tracks(self, query, limit=50, offset=0):
        """Search for tracks on Spotify"""
        try:
            results = self.sp.search(q=query, type='track', limit=limit, offset=offset)
            return results['tracks']['items']
        except Exception as e:
            print(f"Error searching tracks: {e}")
            return []
    
    def get_track_features(self, track_ids):
        """Get audio features for multiple tracks"""
        try:
            if isinstance(track_ids, str):
                track_ids = [track_ids]
            
            features = self.sp.audio_features(track_ids)
            return [f for f in features if f is not None]
        except Exception as e:
            print(f"Error getting track features: {e}")
            return []
    
    def get_track_info(self, track_id):
        """Get basic track information"""
        try:
            track = self.sp.track(track_id)
            return {
                'id': track['id'],
                'name': track['name'],
                'artists': [artist['name'] for artist in track['artists']],
                'album': track['album']['name'],
                'popularity': track['popularity'],
                'preview_url': track['preview_url'],
                'external_url': track['external_urls']['spotify']
            }
        except Exception as e:
            print(f"Error getting track info: {e}")
            return None
    
    def get_playlist_tracks(self, playlist_id):
        """Get tracks from a specific playlist"""
        try:
            results = self.sp.playlist_tracks(playlist_id)
            tracks = []
            
            for item in results['items']:
                if item['track']:
                    tracks.append(item['track'])
            
            return tracks
        except Exception as e:
            print(f"Error getting playlist tracks: {e}")
            return []
    
    def get_recommendations(self, seed_tracks=None, seed_artists=None, seed_genres=None, 
                          target_valence=None, target_energy=None, target_danceability=None,
                          limit=20):
        """Get track recommendations based on seeds and audio features"""
        try:
            recommendations = self.sp.recommendations(
                seed_tracks=seed_tracks,
                seed_artists=seed_artists,
                seed_genres=seed_genres,
                target_valence=target_valence,
                target_energy=target_energy,
                target_danceability=target_danceability,
                limit=limit
            )
            
            return recommendations['tracks']
        except Exception as e:
            print(f"Error getting recommendations: {e}")
            return []
    
    def build_dataset(self, genres=['pop', 'rock', 'jazz', 'classical', 'electronic'], 
                     tracks_per_genre=100):
        """Build a dataset of tracks with features for training"""
        dataset = []
        
        for genre in genres:
            print(f"Collecting {genre} tracks...")
            tracks = self.search_tracks(f'genre:{genre}', limit=tracks_per_genre)
            
            for track in tracks:
                track_info = {
                    'id': track['id'],
                    'name': track['name'],
                    'artist': track['artists'][0]['name'] if track['artists'] else 'Unknown',
                    'popularity': track['popularity'],
                    'genre': genre
                }
                
                # Get audio features
                features = self.get_track_features(track['id'])
                if features:
                    track_info.update(features[0])
                    dataset.append(track_info)
        
        return pd.DataFrame(dataset)