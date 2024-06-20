import spotipy
from spotipy.oauth2 import SpotifyOAuth
sp_oauth = SpotifyOAuth(client_id='8a93a75ab01445e8b69666bfaeafcaa9',
                        client_secret='9788349067ee4d079016bb5f2e539b22',
                        redirect_uri='http://127.0.0.1:5500/Auth/index.html',
                        scope='user-library-read user-modify-playback-state')
auth_url = sp_oauth.get_authorize_url()
print(f"Por favor, visita esta URL en tu navegador para autorizar la aplicación:\n{auth_url}")
redirect_response = input("Pega aquí la URL de redirección después de autorizar: ").strip()
token_info = sp_oauth.get_access_token(redirect_response)
if token_info:
    sp = spotipy.Spotify(auth=token_info['access_token'])
    print("Autenticación exitosa. Ahora puedes usar `sp` para interactuar con Spotify.")
else:
    print("No se pudo obtener el token de acceso.")
