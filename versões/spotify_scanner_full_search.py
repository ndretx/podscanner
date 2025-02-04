import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
import pandas as pd
from datetime import datetime

# Função para autenticar no Spotify usando as credenciais do cliente
def authenticate_spotify(client_id, client_secret):
    auth_manager = SpotifyClientCredentials(client_id=client_id, client_secret=client_secret)
    sp = spotipy.Spotify(auth_manager=auth_manager)
    return sp

# Função para buscar podcasts no Spotify com base em uma consulta
def search_podcasts(sp, query, limit=50, offset=0):
    results = sp.search(q=query, type='episode', limit=limit, offset=offset)
    episodes = results['episodes']['items']
    return episodes, results['episodes']['total']

# Função principal que executa o script
def main():
    client_id = '6dccca61c86849b992ad2d764f58b766'  # ID do cliente Spotify
    client_secret = '931cd5ab3d53427ca156607cb7142bec'  # Segredo do cliente Spotify
    
    # Autentica no Spotify
    sp = authenticate_spotify(client_id, client_secret)
    
    # Solicita ao usuário que insira o termo de pesquisa
    query = input("Insira o termo de pesquisa: ")
    
    data = []  # Lista para armazenar os dados dos episódios
    offset = 0  # Deslocamento inicial para a busca
    limit = 50  # Limite de resultados por busca
    total = 1  # Inicializa o total para entrar no loop
    
    # Loop para buscar episódios até que todos sejam encontrados
    while offset < total:
        episodes, total = search_podcasts(sp, query, limit, offset)
        for episode in episodes:
            if query.lower() in episode['name'].lower():
                data.append({
                    'Title': episode['name'],
                    'Description': episode['description'],
                    'Release Date': episode['release_date'],
                    'Link': episode['external_urls']['spotify']
                })
        offset += limit  # Incrementa o deslocamento para a próxima busca
    
    # Cria um DataFrame com os dados dos episódios
    df = pd.DataFrame(data)
    
    # Gera um timestamp para o nome do arquivo
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    filename = f'podcast_episodes_{timestamp}.xlsx'
    
    # Salva os dados em um arquivo Excel
    df.to_excel(filename, index=False)
    print(f"Results have been saved to {filename}")

# Executa a função principal se o script for executado diretamente
if __name__ == "__main__":
    main()
