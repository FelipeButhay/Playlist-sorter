ALLOWED_EXTENSIONS = {"json"}

CLIENT_ID = "-"
CLIENT_SECRET = "-"
REDIRECT_URI = "http://127.0.0.1:5000/callback"
SP_SCOPES = "user-read-playback-state user-modify-playback-state playlist-read-private playlist-read-collaborative playlist-modify-private playlist-modify-public"

import time
from requests.auth import HTTPBasicAuth
from flask import session
import requests

def allowed_file(filename):
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS

def refresh_access_token(client_id, client_secret, refresh_token):
    url = "https://accounts.spotify.com/api/token"
    data = {
        "grant_type": "refresh_token",
        "refresh_token": refresh_token
    }
    auth = HTTPBasicAuth(client_id, client_secret)
    response = requests.post(url, data=data, auth=auth)
    return response.json()

def get_access_token() -> str|None:
    now = time.time()
    
    if "token_time" not in session or now - session["token_time"] > 3500:
        new_token = refresh_access_token(
            CLIENT_ID, 
            CLIENT_SECRET,
            session["refresh_token"]
        )

        session["access_token"] = new_token
        session["token_time"] = now
        
        return session["access_token"]
    
    else:
        return None

