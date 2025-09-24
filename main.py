from flask import Flask, render_template, request, redirect, url_for
from flask import session, jsonify, send_file
import re
import config
import requests
import time
from requests.auth import HTTPBasicAuth
import os
import io
import json

app = Flask(__name__)
app.secret_key = os.urandom(24)

from game_class import Game
sp_game = Game()

@app.route("/", methods=["GET", "POST"])
def main():
    if request.method == "POST":
        
        # RECIVE Y GUARDA EL ARCHIVO CON LA LISTA PARCIAL
        backup_file = request.files.get("backup-file")
        if backup_file:
            if not config.allowed_file(backup_file.filename):
                return "File type not allowed. Also don't mess with the fucking html, " +\
                       "I put so much effort in this, thanks <3", 400
            
            try:
                backup_file_data = backup_file.read().decode("utf-8")
                backup_dict = json.loads(backup_file_data)
            except Exception as e:
                return "Error reading the backup file, make sure it's a valid json file: " + str(e), 400
                
            if sp_game.load_backup_json(backup_dict) == 400:
                return "Backup file is corrupted or not valid", 400
            
        # RECIVE EL LINK DE LA PLAYLIST
        else:
            playlist_id = ""
            try:
                playlist_url = request.form["playlist_url"]
                playlist_id = re.search(r'playlist/([a-zA-Z0-9]+)', playlist_url).group(1)
                session["playlist_id"] = playlist_id
        
            except:
                return "Thats not a spotify playlist link bro", 400
        
        
        return redirect("https://accounts.spotify.com/authorize?" +\
                        f"client_id={config.CLIENT_ID}" +\
                        f"&response_type=code" +\
                        f"&redirect_uri={config.REDIRECT_URI}" +\
                        f"&scope={config.SP_SCOPES}"
        )
        
    return render_template("index.html")

@app.route("/callback")
def callback():
    code = request.args.get("code")
    if code is None:
        return "Error: no se recibió 'code'", 500

    # Pedimos el access token
    token_url = "https://accounts.spotify.com/api/token"
    payload = {
        "grant_type": "authorization_code",
        "code": code,
        "redirect_uri": config.REDIRECT_URI,
        "client_id": config.CLIENT_ID,
        "client_secret": config.CLIENT_SECRET,
    }
    
    response = requests.post(token_url, data=payload)
    data = response.json()

    session["access_token"] = data.get("access_token")
    session["refresh_token"] = data.get("refresh_token")
    session["token_time"] = time.time()
    
    sp_game.set_token(session["access_token"])
    if not sp_game.file_loaded:
        if not sp_game.turn_playlist_to_id_file(session["playlist_id"]):
            return "Empty ahh playlist sybau", 400
    
    return redirect(url_for("game"))

@app.route("/game")
def game():
    return render_template("game.html")

@app.route("/game/start")
def start_game():
    sides_data = sp_game.get_initials()
    
    return jsonify(sides_data)

# /game/click?side=${side}
@app.route("/game/click")
def click_side() :
    side = request.args.get("side")
    end, side_data = sp_game.user_chose(side)
    
    if end:
        return jsonify({"finished": True, "redirect": url_for("end")})
    
    # print(side_data)
    return jsonify(side_data)
    # return jsonify({"side_to_update": side_to_update, "data": side_data})

@app.route("/game/play")
def play_track():
    side = request.args.get("side")
    volume = int(request.args.get("volume"))
    
    sp_game.play_side(side, volume)
    
    return "", 200

@app.route("/game/pause")
def pause_track():
    sp_game.pause()

    return "", 200

@app.route("/game/exit")
def exit_message():
    return render_template("exit.html")

@app.route("/game/download-backup")
def download_backup():
    file_name, data = sp_game.get_backup_json()
    
    json_str = json.dumps(data, indent=4)
    buffer = io.BytesIO(json_str.encode("utf-8"))

    return send_file(
        buffer,
        as_attachment=True,
        download_name=file_name,
        mimetype="application/json"
    )
    
@app.route("/end")
def end():
    return render_template("end.html", sortedList=sp_game.get_sorted_list_names())

@app.route("/end/turn_playlist")
def turn_to_playlist():
    status = sp_game.turn_sorted_to_playlist()
    return "", status

@app.route("/end/download_as_txt")
def download_as_txt():
    file_name, data = sp_game.get_sorted_as_txt()
    
    buffer = io.BytesIO(data.encode("utf-8"))

    return send_file(
        buffer,
        as_attachment=True,
        download_name=file_name,
        mimetype="application/json"
    )

if __name__ == "__main__":
    app.run(debug=True)