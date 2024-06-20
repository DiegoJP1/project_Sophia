import webbrowser
import json
import os
from urllib.parse import urlparse, parse_qs
import speech_recognition as sr
import pyttsx3
import datetime
import pathlib
import textwrap
import google.generativeai as genai
from IPython.display import display, Markdown
import wikipedia
import wolframalpha
import spotipy
from spotipy.oauth2 import SpotifyOAuth, SpotifyOauthError

class Assistant:
    def __init__(self):
        self.name = "Sophia"
        self.recognizer = sr.Recognizer()
        self.engine = pyttsx3.init()
        self.wolfram_alpha_app_id = "PKK9L7-28E2Y9PJ6E"
        self.sp = None
        self.token_file = "spotify_token.json"
        self.sp_oauth = SpotifyOAuth(
            client_id='8a93a75ab01445e8b69666bfaeafcaa9',
            client_secret='9788349067ee4d079016bb5f2e539b22',
            redirect_uri='http://127.0.0.1:5500/Auth/index.html',
            scope='user-library-read user-modify-playback-state user-read-playback-state'
        )

    def authenticate_spotify(self):
        if os.path.exists(self.token_file):
            os.remove(self.token_file)

        auth_url = self.sp_oauth.get_authorize_url()
        print(f"Please, go to this url in your browser to authorize the application:\n{auth_url}")
        webbrowser.open_new_tab(auth_url)
        current_url = input("Paste here your URL actual of your browser after authorize: ").strip()
        parsed_url = urlparse(current_url)
        query_params = parse_qs(parsed_url.query)
        auth_code = query_params.get('code')

        if auth_code:
            try:
                token_info = self.sp_oauth.get_access_token(auth_code[0])
                if token_info:
                    self.sp = spotipy.Spotify(auth=token_info['access_token'])
                    self.save_spotify_token(token_info)
                    print("authentication succes")
                else:
                    print("the token couldn't be obtained.")
            except SpotifyOauthError as e:
                print(f"Error at the authentication with Spotify: {e}")
        else:
            print("The authorization code was not obtained. Be sure to complete the authorization flow correctly.")

    def save_spotify_token(self, token_info):
        with open(self.token_file, 'w') as file:
            json.dump(token_info, file)

    def load_spotify_token(self):
        if os.path.exists(self.token_file):
            with open(self.token_file, 'r') as file:
                token_info = json.load(file)
                if self.sp_oauth.is_token_expired(token_info):
                    try:
                        token_info = self.sp_oauth.refresh_access_token(token_info['refresh_token'])
                        self.save_spotify_token(token_info)
                    except SpotifyOauthError as e:
                        print(f"Error with refresh the token: {e}")
                        return False
                self.sp = spotipy.Spotify(auth=token_info['access_token'])
                return True
        return False

    def speak(self, text):
        print(f"{self.name}: {text}")
        self.engine.say(text)
        self.engine.runAndWait()

    def greet(self):
        current_time = datetime.datetime.now()
        if current_time.hour < 12:
            greeting = f"hi there what can i do for you ?"
        elif 12 <= current_time.hour < 18:
            greeting = f"Good afternoon, how can I help you?"
        else:
            greeting = f"Good night, what can i do for you?"
        return greeting

    def listen(self):
        with sr.Microphone() as source:
            print("listening...")
            audio = self.recognizer.listen(source)
            try:
                user_input = self.recognizer.recognize_google(audio, language="es-ES")
                print(f"you: {user_input}")
                return user_input.lower()
            except sr.UnknownValueError:
                return ""
            except sr.RequestError:
                self.speak("sorry i didn't understand")
                return ""

    def respond(self, user_input):
        if "hello" in user_input or "hey" in user_input or self.name.lower() in user_input:
            return self.greet()
        elif "hour" in user_input:
            current_time = datetime.datetime.now().strftime("%I:%M %p")
            return f"the current hour is {current_time}"
        elif "search" in user_input or "who is" in user_input:
            search_query = user_input.replace("search", "").replace("who is", "")
            try:
                result = wikipedia.summary(search_query, sentences=2, auto_suggest=False)
                return result
            except wikipedia.exceptions.PageError:
                return "sorry i didn't found information about that"
            except wikipedia.exceptions.DisambiguationError:
                return "There are multiple options, could you be more specific?"
        elif "when it was" in user_input:
            query = user_input.replace("when it was", "").strip()
            try:
                wikipedia.set_lang("en")
                wiki_page = wikipedia.page(query)
                wiki_content = wiki_page.content
                return wiki_content
            except wikipedia.exceptions.PageError:
                return f"i didn't found information about '{query}'."
            except wikipedia.exceptions.DisambiguationError:
                return "There are multiple options, could you be more specific?"
        elif "calculate" in user_input:
            query = user_input.replace("calculate", "").strip()
            try:
                client = wolframalpha.Client(self.wolfram_alpha_app_id)
                response = client.query(query)
                result = next(response.results).text
                return result
            except Exception as e:
                print(f"alculating: {e}")
                return "I could not solve the question."
        elif "play" in user_input:
            return self.handle_play_song(user_input)
        elif "show me spotify devices" in user_input:
            return self.show_spotify_devices()
        elif "bye" in user_input:
            return "See you later. Have a nice day."
        elif "What are you programmed with" in user_input or "what languages you are programmed with" in user_input:
            return "I was programmed with python including API integrations such as spotify, wikipedia, walframe etc."
        elif "what functions do you have" in user_input or "what you can do" in user_input:
            return "I was programmed to help you with your day to day life I can perform functions such as: help you with research, give you the time, play songs on your devices."
        else:
            return "Sorry, I didn't understand your instruction"

    def handle_play_song(self, user_input):
        if "from" in user_input:
            parts = user_input.split("from")
            song_name = parts[0].replace("play", "").strip()
            artist_name = parts[1].strip()
            return self.play_song(song_name, artist_name)
        else:
            song_name = user_input.replace("play", "").strip()
            return self.play_song(song_name)

    def play_song(self, song_name, artist_name=None):
        if self.sp:
            query = f"track:{song_name}"
            if artist_name:
                query += f" artist:{artist_name}"
            results = self.sp.search(q=query, limit=1)
            if results['tracks']['items']:
                track_uri = results['tracks']['items'][0]['uri']
                if self.get_active_device():
                    self.sp.start_playback(uris=[track_uri])
                    return f"playing '{song_name}'" + (f" from '{artist_name}'" if artist_name else "") + " in Spotify."
                else:
                    return "No active device was found to play music."
            else:
                return f"Song not found '{song_name}'" + (f" from '{artist_name}'" if artist_name else "") + " in Spotify."
        else:
            return "You must authenticate Spotify first."

    def get_active_device(self):
        try:
            devices = self.sp.devices()
            if devices['devices']:
                for device in devices['devices']:
                    if device['is_active']:
                        return True
                self.sp.transfer_playback(devices['devices'][0]['id'])
                return True
            return False
        except spotipy.exceptions.SpotifyException as e:
            print(f"Error when obtaining active devices: {e}")
            if e.http_status == 401:
                print("Invalid or expired access token, reauthenticating...")
                self.authenticate_spotify()
            return False

    def show_spotify_devices(self):
        try:
            devices = self.sp.devices()
            if devices['devices']:
                device_list = []
                for device in devices['devices']:
                    device_list.append(f"Devices: {device['name']}, Type: {device['type']}, Active: {'yes' if device['is_active'] else 'No'}")
                return "here are your devices: " + "; ".join(device_list)
            else:
                return "devices not found"
        except spotipy.exceptions.SpotifyException as e:
            print(f"Error obtaining devices: {e}")
            if e.http_status == 401:
                print("Invalid or expired access token, reauthenticating...")
                self.authenticate_spotify()
            return "Error getting the devices. Please try again."

def main():
    assistant = Assistant()
    if not assistant.load_spotify_token():
        assistant.authenticate_spotify()

    assistant.speak(assistant.greet())

    while True:
        user_input = assistant.listen()
        if user_input:
            response = assistant.respond(user_input)
            assistant.speak(response)

            if "bye" in user_input:
                break

if __name__ == "__main__":
    main()
