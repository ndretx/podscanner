import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
import pandas as pd
from datetime import datetime

def authenticate_spotify(client_id, client_secret):
    auth_manager = SpotifyClientCredentials(client_id=client_id, client_secret=client_secret)
    sp = spotipy.Spotify(auth_manager=auth_manager)
    return sp

def search_podcasts(sp, query, limit=50):
    results = sp.search(q=query, type='episode', limit=limit)
    episodes = results['episodes']['items']
    return episodes

def main():
    client_id = '6dccca61c86849b992ad2d764f58b766'
    client_secret = '931cd5ab3d53427ca156607cb7142bec'
    
    sp = authenticate_spotify(client_id, client_secret)
    query = 'ditadura'
    episodes = search_podcasts(sp, query)
    
    data = []
    for episode in episodes:
        if 'ditadura' in episode['name'].lower():
            data.append({
                'Title': episode['name'],
                'Description': episode['description'],
                'Release Date': episode['release_date'],
                'Link': episode['external_urls']['spotify']
            })
    
    df = pd.DataFrame(data)
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    filename = f'podcast_episodes_{timestamp}.xlsx'
    df.to_excel(filename, index=False)
    print(f"Results have been saved to {filename}")

if __name__ == "__main__":
    main()
