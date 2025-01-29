import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
import pandas as pd
from datetime import datetime
import os
from dotenv import load_dotenv
import time
import json

# Autenticação no Spotify
def authenticate_spotify():
    load_dotenv()
    client_id = os.getenv('SPOTIFY_CLIENT_ID')
    client_secret = os.getenv('SPOTIFY_CLIENT_SECRET')
    if not client_id or not client_secret:
        raise ValueError("Credenciais do Spotify não encontradas. Verifique o arquivo .env.")
    auth_manager = SpotifyClientCredentials(client_id=client_id, client_secret=client_secret)
    sp = spotipy.Spotify(auth_manager=auth_manager)
    return sp

# Buscar shows (programas de podcast) relacionados ao termo de busca
def search_podcast_shows(sp, query, limit=50):
    shows = []
    offset = 0
    
    while True:
        try:
            results = sp.search(q=query, type='show', limit=limit, offset=offset)
            if results.get('shows') and results['shows'].get('items'):
                shows.extend(results['shows']['items'])
            
            # Verifica se há mais páginas
            if not results.get('shows') or not results['shows'].get('next'):
                break
            
            offset += limit
            time.sleep(1)  # Delay entre requisições
        
        except spotipy.exceptions.SpotifyException as e:
            print(f"Erro na requisição: {e.http_status} - {e.msg}")
            break
    
    return shows

# Listar todos os episódios de um show (programa de podcast)
def get_episodes_from_show(sp, show_id, limit=50):
    episodes = []
    offset = 0
    
    while True:
        try:
            results = sp.show_episodes(show_id, limit=limit, offset=offset)
            if results.get('items'):
                episodes.extend(results['items'])
            
            # Verifica se há mais páginas
            if not results.get('next'):
                break
            
            offset += limit
            time.sleep(1)  # Delay entre requisições
        
        except spotipy.exceptions.SpotifyException as e:
            print(f"Erro na requisição: {e.http_status} - {e.msg}")
            break
    
    return episodes

# Função principal
def main():
    try:
        sp = authenticate_spotify()
        query = 'ditadura brasil'  # Defina o termo de busca aqui
        
        # Passo 1: Buscar shows relacionados ao termo de busca
        print(f"Buscando shows relacionados ao termo '{query}'...")
        shows = search_podcast_shows(sp, query)
        print(f"Encontrados {len(shows)} shows.")
        
        # Passo 2: Listar episódios de cada show
        all_episodes = []
        for show in shows:
            show_id = show['id']
            show_name = show['name']
            print(f"Buscando episódios do show: {show_name}...")
            episodes = get_episodes_from_show(sp, show_id)
            all_episodes.extend(episodes)
            print(f"Encontrados {len(episodes)} episódios.")
            time.sleep(2)  # Delay entre buscas de shows
        
        # Passo 3: Filtrar episódios que contenham o termo de busca no título ou descrição
        data = []
        for episode in all_episodes:
            title = episode.get('name', 'Sem título')
            description = episode.get('description', 'Sem descrição')
            release_date = episode.get('release_date', 'Data desconhecida')
            link = episode.get('external_urls', {}).get('spotify', 'Link não disponível')
            
            if query.lower() in title.lower() or query.lower() in description.lower():
                data.append({
                    'Title': title,
                    'Description': description,
                    'Release Date': release_date,
                    'Link': link
                })
        
        # Salvar resultados em um arquivo Excel
        if data:
            df = pd.DataFrame(data)
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            filename = f'podcast_episodes_{timestamp}.xlsx'
            df.to_excel(filename, index=False)
            print(f"Results have been saved to {filename}")
        else:
            print("Nenhum episódio encontrado com o termo especificado.")
    
    except ValueError as e:
        print(e)
    except spotipy.exceptions.SpotifyException as e:
        print(f"Erro ao autenticar ou buscar podcasts: {e.http_status} - {e.msg}")

if __name__ == "__main__":
    main()