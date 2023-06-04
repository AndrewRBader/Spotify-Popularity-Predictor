import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
import pandas as pd
import os
from dotenv import load_dotenv

load_dotenv()
cid=os.getenv('cid')
secret=os.getenv('secret')

def track_data(search):

    # Start the connection with the API
    client_credentials_manager = SpotifyClientCredentials(client_id=cid, client_secret=secret)
    spotify = spotipy.Spotify(client_credentials_manager=client_credentials_manager)
    
    # Get search results
    search_result=spotify.search('{}'.format(search),type='track')
    
    # Parse search results to retrieve the track URI and artist URI
    track_uri=track_uri=search_result['tracks']['items'][0]['uri']
    artist_uri=artist_uri=search_result['tracks']['items'][0]['album']['artists'][0]['uri']
    
    # Prepare data to be gathered from track and artist info
    album_dict={'Album/Single':'type',
    'Tracks_in_album':'total_tracks'
    }
    artists_dict={'Artist':'name'}
    track_dict={'Track_number':'track_number',
    'duration_ms':'duration_ms',
    'explicit':'explicit',
    'Title':'name'
    }
    artist_dict={'Artist_followers':'followers',
    'Genre':'genres'
    }
    
    # Gather track and artist info
    song_stats=spotify.track(track_uri)
    artist_stats=spotify.artist(artist_uri)
    audio_features=spotify.audio_features(tracks=[track_uri])
    
    # Populate song_dict with all relevant data
    song_dict={}
    for k, v in album_dict.items():
        song_dict[k]=song_stats['album'][v]
    for k, v in track_dict.items():
        song_dict[k]=song_stats[v] 
    for k, v in artists_dict.items():
        song_dict[k]=song_stats['artists'][0][v] 
    for k, v in artist_dict.items():
        song_dict[k]=artist_stats[v] 
    for i in ['type','id','uri','track_href','analysis_url','duration_ms']:
        del audio_features[0][i]
    song_dict.update(audio_features[0])
    song_dict['Artist_followers']=song_dict['Artist_followers']['total']
    
    # Renaming values to match our dataframe
    song_dict['liveliness']=song_dict['liveness']
    del song_dict['liveness']
    song_dict['acoustics']=song_dict['acousticness']
    del song_dict['acousticness']

    # Turn dict into pandas Series
    song_series=pd.Series(song_dict)

    # Sort data to match our dataframe
    song_series=song_series.reindex(['Title', 'Artist', 'Artist_followers', 'Track_number',
       'Tracks_in_album', 'danceability', 'energy', 'key', 'loudness', 'mode',
       'speechiness', 'acoustics', 'instrumentalness', 'liveliness', 'valence',
       'tempo', 'duration_ms', 'time_signature', 'explicit','Album/Single','Genre'])

    # Encode explicit
    for i in ['Explicit_false', 'Explicit_true']:
        song_series[i]=0 
        if song_series['explicit'] == True:
            song_series['Explicit_true']=1
        else:
            song_series['Explicit_false']=1
    song_series=song_series.drop('explicit')

    # Encode Album/Single
    for i in ['album', 'compilation', 'single']:
        song_series[i]=0
        if song_series['Album/Single']==i:
            song_series[i]=1
    song_series=song_series.drop('Album/Single')

    # Encode Genre
    for i in ['boy band',
        'country', 'dance/electronic', 'else', 'funk', 'hip hop', 'house',
        'indie', 'k-pop', 'latin', 'metal', 'pop', 'r&b/soul',
        'rap', 'reggaeton', 'rock', 'trap']:
        song_series[i]=0
        if i in song_series['Genre']:
            song_series[i]=1
    song_series=song_series.drop('Genre')
    df = song_series.to_frame().T
    
    return df