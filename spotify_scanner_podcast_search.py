import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
import pandas as pd
from datetime import datetime
from dotenv import load_dotenv
import os

# Carrega as variáveis de ambiente do arquivo .env
load_dotenv()

def authenticate_spotify(client_id, client_secret):
    auth_manager = SpotifyClientCredentials(client_id=client_id, client_secret=client_secret)
    sp = spotipy.Spotify(auth_manager=auth_manager)
    return sp

def search_podcasts(sp, query, limit=50, offset=0):
    results = sp.search(q=query, type='show', limit=limit, offset=offset)
    shows = results['shows']['items']
    return shows, results['shows']['total']

def search_episodes(sp, show_id, limit=50, offset=0):
    results = sp.show_episodes(show_id, limit=limit, offset=offset)
    episodes = results['items']
    return episodes, results['total']

def main():
    client_id = os.getenv('SPOTIFY_CLIENT_ID')
    client_secret = os.getenv('SPOTIFY_CLIENT_SECRET')
    
    sp = authenticate_spotify(client_id, client_secret)
    query = input("Insira o termo de pesquisa: ")
    
    data = []
    offset = 0
    limit = 50
    total = 1  # Initialize total to enter the loop
    
    while offset < total:
        shows, total = search_podcasts(sp, query, limit, offset)
        for show in shows:
            show_id = show['id']
            episode_offset = 0
            episode_total = 1  # Initialize total to enter the loop
            while episode_offset < episode_total:
                episodes, episode_total = search_episodes(sp, show_id, limit=limit, offset=episode_offset)
                for episode in episodes:
                    if episode and isinstance(episode, dict) and episode.get('name') and query.lower() in episode['name'].lower():
                        data.append({
                            'Title': episode['name'],
                            'Description': episode['description'],
                            'Release Date': episode['release_date'],
                            'Link': episode['external_urls']['spotify']
                        })
                episode_offset += limit
        offset += limit
    
    if data:
        df = pd.DataFrame(data)
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f'podcast_episodes_{timestamp}.xlsx'
        df.to_excel(filename, index=False)
        print(f"Results have been saved to {filename}")
    else:
        print("No episodes found matching the search criteria.")

if __name__ == "__main__":
    main()