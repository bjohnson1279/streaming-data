import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
from ytmusicapi import YTMusic
import os
import json

class StreamingDataFetcher:
    def __init__(self, spotify_client_id, spotify_client_secret, ytmusic_auth_file=None):
        """
        Initializes the StreamingDataFetcher with API credentials.

        Args:
            spotify_client_id (str): Your Spotify API Client ID.
            spotify_client_secret (str): Your Spotify API Client Secret.
            ytmusic_auth_file (str, optional): Path to the ytmusicapi authentication file (e.g., 'oauth.json' or 'headers_auth.json').
                                               If None, ytmusicapi will try to work in an unauthenticated manner (may have limitations).
        """
        # Spotify authentication
        self.sp = spotipy.Spotify(auth_manager=SpotifyClientCredentials(
            client_id=spotify_client_id,
            client_secret=spotify_client_secret
        ))

        # YouTube Music authentication
        try:
            if ytmusic_auth_file and os.path.exists(ytmusic_auth_file):
                self.yt = YTMusic(ytmusic_auth_file)
            else:
                self.yt = YTMusic() # Attempt unauthenticated access or prompt for setup if not found
                print(f"Warning: YouTube Music authentication file '{ytmusic_auth_file}' not found or not provided. "
                      "Attempting unauthenticated access, which might be limited. "
                      "Run YTMusic.setup() to create one if needed.")
        except Exception as e:
            print(f"Error initializing YouTube Music API: {e}. "
                  "Please ensure 'ytmusicapi' is correctly installed and authenticated if required.")
            self.yt = None


    def get_spotify_data(self, artist_name, track_title):
        """
        Fetches data from Spotify for a given artist and track.

        Args:
            artist_name (str): The name of the artist.
            track_title (str): The title of the track.

        Returns:
            dict: A dictionary containing Spotify data (popularity, URL) or None if not found.
        """
        try:
            query = f"track:{track_title} artist:{artist_name}"
            results = self.sp.search(q=query, type='track', limit=1)

            if results and results['tracks']['items']:
                track = results['tracks']['items'][0]
                return {
                    "popularity": track['popularity'],
                    "external_url": track['external_urls']['spotify'],
                    "album": track['album']['name'],
                    "release_date": track['album']['release_date']
                }
            else:
                return None
        except Exception as e:
            print(f"Error fetching Spotify data for {artist_name} - {track_title}: {e}")
            return None

    def get_youtube_music_data(self, artist_name, track_title):
        """
        Fetches data from YouTube Music for a given artist and track.

        Args:
            artist_name (str): The name of the artist.
            track_title (str): The title of the track.

        Returns:
            dict: A dictionary containing YouTube Music data (views, URL) or None if not found.
        """
        if not self.yt:
            return None

        try:
            query = f"{artist_name} {track_title}"
            # Search for songs specifically, often more relevant for view counts
            results = self.yt.search(query, filter="songs")

            if results:
                # Look for an official video or a good match
                for result in results:
                    if result.get('resultType') == 'song' and result.get('artists') and result.get('artists')[0].get('name') == artist_name and result.get('title') == track_title:
                        return {
                            "views": result.get('views'),
                            "url": f"https://music.youtube.com/watch?v={result['videoId']}"
                        }
                    elif result.get('resultType') == 'video' and result.get('artists') and result.get('artists')[0].get('name') == artist_name and result.get('title') == track_title:
                        return {
                            "views": result.get('views'),
                            "url": f"https://www.youtube.com/watch?v={result['videoId']}"
                        }
                # If no perfect match, return the first song result with views
                for result in results:
                    if result.get('resultType') == 'song' and result.get('views'):
                         return {
                            "views": result.get('views'),
                            "url": f"https://music.youtube.com/watch?v={result['videoId']}"
                        }
                return None
            else:
                return None
        except Exception as e:
            print(f"Error fetching YouTube Music data for {artist_name} - {track_title}: {e}")
            return None

    def get_streaming_data(self, artist_name, track_title):
        """
        Aggregates streaming data from all available services.

        Args:
            artist_name (str): The name of the artist.
            track_title (str): The title of the track.

        Returns:
            dict: A dictionary containing aggregated streaming data.
        """
        data = {
            "artist": artist_name,
            "title": track_title,
            "spotify": {},
            "youtube_music": {}
        }

        print(f"Fetching data for: {artist_name} - {track_title}")

        # Fetch Spotify data
        spotify_data = self.get_spotify_data(artist_name, track_title)
        if spotify_data:
            data["spotify"] = spotify_data
            print(f"  Spotify Popularity: {spotify_data.get('popularity', 'N/A')}")
        else:
            print("  Spotify data not found or error occurred.")

        # Fetch YouTube Music data
        youtube_music_data = self.get_youtube_music_data(artist_name, track_title)
        if youtube_music_data:
            data["youtube_music"] = youtube_music_data
            print(f"  YouTube Music Views: {youtube_music_data.get('views', 'N/A')}")
        else:
            print("  YouTube Music data not found or error occurred.")

        return data

# --- Example Usage ---
if __name__ == '__main__':
    # Replace with your actual Spotify Client ID and Client Secret
    SPOTIPY_CLIENT_ID = ""
    SPOTIPY_CLIENT_SECRET = ""
    YT_MUSIC_AUTH_FILE = "headers_auth.json" # Or 'oauth.json' if that's what YTMusic.setup() generated

    # Verify that you've replaced the placeholders
    if SPOTIPY_CLIENT_ID == "YOUR_SPOTIPY_CLIENT_ID" or SPOTIPY_CLIENT_SECRET == "YOUR_SPOTIPY_CLIENT_SECRET":
        print("Please replace 'YOUR_SPOTIPY_CLIENT_ID' and 'YOUR_SPOTIPY_CLIENT_SECRET' with your actual Spotify API credentials.")
        print("Refer to Step 1 for instructions on how to get them.")
    else:
        fetcher = StreamingDataFetcher(SPOTIPY_CLIENT_ID, SPOTIPY_CLIENT_SECRET, YT_MUSIC_AUTH_FILE)

        songs = [
            "Amber",
            "Down",
            "Beautiful Disaster",
            "All Mixed Up",
            "Come Original",
            "Creatures (For a While)",
            "Love Song",
            "Sunset in July",
            "Don't Tread on Me",
            "Don't Stay Home",
            "You're Gonna Get It",
            "Full Bloom",
            "Good Feeling",
            "Sand Dollars",
            "Count Me In"
        ]

        artist = "311"
        for song in songs:
            streaming_info = fetcher.get_streaming_data(artist, song)
            print(f"\n--- Aggregated Data (311 - {song}) ---")
            print(json.dumps(streaming_info, indent=2))
            print("-" * 30)

        # {"data":{"seoRecommendedTrack":{"items":[{"data":{"__typename":"Track","albumOfTrack":{"coverArt":{"sources":[{"height":300,"url":"https://i.scdn.co/image/ab67616d00001e020b6c94e9ed0f9b470b70af86","width":300},{"height":64,"url":"https://i.scdn.co/image/ab67616d000048510b6c94e9ed0f9b470b70af86","width":64},{"height":640,"url":"https://i.scdn.co/image/ab67616d0000b2730b6c94e9ed0f9b470b70af86","width":640}]},"id":"6ken2un2BQtGxUMT8c7aVH","uri":"spotify:album:6ken2un2BQtGxUMT8c7aVH"},"artists":{"items":[{"id":"41Q0HrwWBtuUkJc7C1Rp6K","profile":{"name":"311"},"uri":"spotify:artist:41Q0HrwWBtuUkJc7C1Rp6K"}]},"contentRating":{"label":"NONE"},"duration":{"totalMilliseconds":133186},"id":"28jz5StpMXZ9wX84uK7gl4","name":"Syntax Error","playability":{"playable":true},"playcount":"911715","uri":"spotify:track:28jz5StpMXZ9wX84uK7gl4"}},{"data":{"__typename":"Track","albumOfTrack":{"coverArt":{"sources":[{"height":300,"url":"https://i.scdn.co/image/ab67616d00001e020b6c94e9ed0f9b470b70af86","width":300},{"height":64,"url":"https://i.scdn.co/image/ab67616d000048510b6c94e9ed0f9b470b70af86","width":64},{"height":640,"url":"https://i.scdn.co/image/ab67616d0000b2730b6c94e9ed0f9b470b70af86","width":640}]},"id":"6ken2un2BQtGxUMT8c7aVH","uri":"spotify:album:6ken2un2BQtGxUMT8c7aVH"},"artists":{"items":[{"id":"41Q0HrwWBtuUkJc7C1Rp6K","profile":{"name":"311"},"uri":"spotify:artist:41Q0HrwWBtuUkJc7C1Rp6K"}]},"contentRating":{"label":"NONE"},"duration":{"totalMilliseconds":234000},"id":"0XR8I3hqnvkG8RNStXtGCs","name":"Days of '88","playability":{"playable":true},"playcount":"1015401","uri":"spotify:track:0XR8I3hqnvkG8RNStXtGCs"}},{"data":{"__typename":"Track","albumOfTrack":{"coverArt":{"sources":[{"height":300,"url":"https://i.scdn.co/image/ab67616d00001e020b6c94e9ed0f9b470b70af86","width":300},{"height":64,"url":"https://i.scdn.co/image/ab67616d000048510b6c94e9ed0f9b470b70af86","width":64},{"height":640,"url":"https://i.scdn.co/image/ab67616d0000b2730b6c94e9ed0f9b470b70af86","width":640}]},"id":"6ken2un2BQtGxUMT8c7aVH","uri":"spotify:album:6ken2un2BQtGxUMT8c7aVH"},"artists":{"items":[{"id":"41Q0HrwWBtuUkJc7C1Rp6K","profile":{"name":"311"},"uri":"spotify:artist:41Q0HrwWBtuUkJc7C1Rp6K"}]},"contentRating":{"label":"NONE"},"duration":{"totalMilliseconds":207253},"id":"2VeAYuDHfOH0dwESM09vqX","name":"One and the Same","playability":{"playable":true},"playcount":"1032652","uri":"spotify:track:2VeAYuDHfOH0dwESM09vqX"}},{"data":{"__typename":"Track","albumOfTrack":{"coverArt":{"sources":[{"height":300,"url":"https://i.scdn.co/image/ab67616d00001e020b6c94e9ed0f9b470b70af86","width":300},{"height":64,"url":"https://i.scdn.co/image/ab67616d000048510b6c94e9ed0f9b470b70af86","width":64},{"height":640,"url":"https://i.scdn.co/image/ab67616d0000b2730b6c94e9ed0f9b470b70af86","width":640}]},"id":"6ken2un2BQtGxUMT8c7aVH","uri":"spotify:album:6ken2un2BQtGxUMT8c7aVH"},"artists":{"items":[{"id":"41Q0HrwWBtuUkJc7C1Rp6K","profile":{"name":"311"},"uri":"spotify:artist:41Q0HrwWBtuUkJc7C1Rp6K"}]},"contentRating":{"label":"NONE"},"duration":{"totalMilliseconds":213133},"id":"6UGtSZvWI6AfRUwizIuCH3","name":"Hey Yo","playability":{"playable":true},"playcount":"1961281","uri":"spotify:track:6UGtSZvWI6AfRUwizIuCH3"}},{"data":{"__typename":"Track","albumOfTrack":{"coverArt":{"sources":[{"height":300,"url":"https://i.scdn.co/image/ab67616d00001e020b6c94e9ed0f9b470b70af86","width":300},{"height":64,"url":"https://i.scdn.co/image/ab67616d000048510b6c94e9ed0f9b470b70af86","width":64},{"height":640,"url":"https://i.scdn.co/image/ab67616d0000b2730b6c94e9ed0f9b470b70af86","width":640}]},"id":"6ken2un2BQtGxUMT8c7aVH","uri":"spotify:album:6ken2un2BQtGxUMT8c7aVH"},"artists":{"items":[{"id":"41Q0HrwWBtuUkJc7C1Rp6K","profile":{"name":"311"},"uri":"spotify:artist:41Q0HrwWBtuUkJc7C1Rp6K"}]},"contentRating":{"label":"NONE"},"duration":{"totalMilliseconds":328080},"id":"15QSgOl5CHTcSF44GYSg8u","name":"Wildfire","playability":{"playable":true},"playcount":"2697424","uri":"spotify:track:15QSgOl5CHTcSF44GYSg8u"}}]}},"extensions":{}}

        # Example 1: A popular song
        # artist = "The Weeknd"
        # song = "Blinding Lights"
        # streaming_info = fetcher.get_streaming_data(artist, song)
        # print("\n--- Aggregated Data (Example 1) ---")
        # print(json.dumps(streaming_info, indent=2))

        # print("-" * 30)

        # Example 2: Another song
        # artist = "Queen"
        # song = "Bohemian Rhapsody"
        # streaming_info_2 = fetcher.get_streaming_data(artist, song)
        # print("\n--- Aggregated Data (Example 2) ---")
        # print(json.dumps(streaming_info_2, indent=2))

        # print("-" * 30)

        # Example 3: A less common song or one that might not have direct matches
        # artist = "Imagine Dragons"
        # song = "Radioactive"
        # streaming_info_3 = fetcher.get_streaming_data(artist, song)
        # print("\n--- Aggregated Data (Example 3) ---")
        # print(json.dumps(streaming_info_3, indent=2))
