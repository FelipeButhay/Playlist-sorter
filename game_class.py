import spotipy
from spotipy.oauth2 import SpotifyOAuth

from functools import wraps
import base64
import requests
from random import shuffle
import time

import config

def s_to_time(s: int) -> str:
    minutes = s // 60
        
    sec_str = ""
    if s < 10:
        sec_str = f"0{s}"
    else:
        sec_str = str(s%60)
    
    return f"{minutes}:{sec_str}"

def get_opp(side):
    return "A" if side == "B" else "B"

def ensure_token(func):
    @wraps(func)
    def wrapper(self, *args, **kwargs):
        token = config.get_access_token()
        if token != None:
            self.set_token(token)
            
        return func(self, *args, **kwargs)
    return wrapper

class Game:
    def __init__(self):
        
        self.initial_arr = []
        self.sorted_songs_names = []
        self.sorted_songs = []
        
        self.sides = {"A": {"id" : None}, "B": {"id" : None}}
        
        self.n_comp = 0
        
        self.left = None
        self.right = None
        self.mid = None
        
        self.sp = None
        self.file_loaded = False
        
    def set_token(self, access_token):
        self.sp = spotipy.Spotify(auth=access_token)
        
    def get_next_song_id(self):
        song = self.initial_arr[self.iter]
        self.iter += 1
        
        return song
        
    def get_song_data(self, id) -> dict:
        track = self.sp.track(id)
        
        return {
            "id":       id,
            "artist":   "; ".join([artist["name"] for artist in track["artists"]]),
            "song":     track["name"],
            "album":    track["album"]["name"],
            "release":  "/".join(track["album"]["release_date"].split("-")[::-1]),
            "duration": int(track["duration_ms"] / 1000 + 0.5),
            "img_url":  track["album"]["images"][0]["url"],
        }
    
    @ensure_token
    def get_initials(self) -> dict[dict]:
        if self.file_loaded:
            self.sides["A"] = self.get_song_data(self.sides["A"]["id"])
            self.sides["B"] = self.get_song_data(self.sides["B"]["id"])
            return self.sides if self.n_comp % 2 == 0 else self.swap_sides()
        
        self.iter = 0
        
        self.sides["A"] = self.get_song_data(self.get_next_song_id())
        self.sides["B"] = self.get_song_data(self.get_next_song_id())
        
        self.sorted_songs = [self.sides["B"]["id"]]
        self.sorted_songs_names = [self.sides["B"]["song"]]
        
        self.mid = 0
        self.left = 0
        self.right = len(self.sorted_songs) - 1
        
        self.n_comp = 0
        
        return self.sides
        
    @ensure_token
    def user_chose(self, side: str):
        fixed_side = side if self.n_comp%2 == 0 else get_opp(side)

        if fixed_side == "A":
            self.left = self.mid + 1
        
        else:
            self.right = self.mid - 1 
            
        self.mid = (self.left + self.right) // 2
        
        if self.left > self.right:
            self.n_comp += 1
            
            self.sorted_songs.insert(self.left, self.sides["A"]["id"])
            self.sorted_songs_names.insert(self.left, self.sides["A"]["song"])
            #print([self.sp.track(i)["name"] for i in self.sorted_songs])
            
            if self.iter < len(self.initial_arr):
                self.sides["B"] = self.sides["A"]
                
                new_key_song = self.get_song_data(self.get_next_song_id())
                self.sides["A"] = new_key_song

                self.mid = self.left
                self.left = 0
                self.right = len(self.sorted_songs) - 1

            else:
                return True, None
        else:
            new_passive_song = self.get_song_data(self.sorted_songs[self.mid])
            self.sides["B"] = new_passive_song
        
        return False, self.sides if self.n_comp % 2 == 0 else self.swap_sides()
    
    def swap_sides(self) -> dict:
        return {"A": self.sides["B"], "B": self.sides["A"]}
        
    @ensure_token
    def play_side(self, side, volume: str):
        self.sp.volume(volume)
        fixed_side = side if self.n_comp%2 == 0 else get_opp(side)
        track_id = self.sides[fixed_side]["id"]
        self.sp.start_playback(uris=[f"spotify:track:{track_id}"], position_ms=self.sides[fixed_side]["duration"]*333)
        
    @ensure_token
    def pause(self):
        self.sp.pause_playback()
    
    @ensure_token
    def get_backup_json(self):
        playlist_name = self.sp.playlist(self.playlist_id)["name"]
        progress = f"{len(self.sorted_songs)} out of {len(self.initial_arr)}"
        
        gmt = time.gmtime()
        date = f"{gmt.tm_mday}-{gmt.tm_mon}-{gmt.tm_year}_{gmt.tm_hour};{gmt.tm_min};{gmt.tm_sec}"
        
        file_name = f"backup_{playlist_name}_({progress})_{date}.json"
        
        return file_name, dict({
            "iter": self.iter,
            "n_comp": self.n_comp,
            
            "mid": self.mid,
            "left": self.left,
            "right": self.right,
            
            "init_arr": self.initial_arr,
            "partial_arr": self.sorted_songs,
            "partial_names": self.sorted_songs_names,
            
            "playlist_id": self.playlist_id,
            
            "sides_id": {
                "A": self.sides["A"]["id"], 
                "B": self.sides["B"]["id"]
            }  
        })
        
    def load_backup_json(self, backup: dict) -> int:
        try:
            self.iter = backup["iter"]
            self.n_comp = backup["n_comp"]
            
            self.mid = backup["mid"]
            self.left = backup["left"]
            self.right = backup["right"]
            
            self.initial_arr = backup["init_arr"]
            self.sorted_songs = backup["partial_arr"]
            self.sorted_songs_names = backup["partial_names"]
            
            self.playlist_id = backup["playlist_id"]
            
            self.sides["A"]["id"] = backup["sides_id"]["A"]
            self.sides["B"]["id"] = backup["sides_id"]["B"]
            
            self.file_loaded = True
            return 200
        except Exception as e:
            self.file_loaded = False
            return 400
        
    def get_sorted_list_names(self):
        return self.sorted_songs_names[::-1]
        
    @ensure_token
    def get_sorted_as_txt(self) -> list:
        playlist_name = self.sp.playlist(self.playlist_id)["name"]
        
        gmt = time.gmtime()
        date = f"{gmt.tm_mday}-{gmt.tm_mon}-{gmt.tm_year}_{gmt.tm_hour};{gmt.tm_min};{gmt.tm_sec}"
        
        file_name = f"{playlist_name}(sorted)_{date}.txt"
        
        return file_name, "\n".join(self.get_sorted_list_names())
        
    @ensure_token
    def turn_sorted_to_playlist(self) -> int:
        try:
            user_id = self.sp.me()["id"]
            playlist_name = self.sp.playlist(self.playlist_id)["name"]
            
            playlist = self.sp.user_playlist_create(
                user=user_id,
                name=f"{playlist_name} (sorted)",
                public=False,
                description=f"This is the full {playlist_name} playlist ranked from best to worst"
            )
    
            limit = 100
            offset = 0
            n = len(self.sorted_songs)
            
            reversed_sorted_songs = self.sorted_songs[::-1]

            while offset < n:
                max_n = min(offset+limit, n)
            
                self.sp.playlist_add_items(
                    playlist_id=playlist["id"],
                    items=[f"spotify:track:{t_id}" for t_id in reversed_sorted_songs[offset:max_n]] 
                )
                
                offset += limit
            
            return 200
        except:
            return 500

    @ensure_token
    def turn_playlist_to_id_file(self, playlist_id: str) -> bool:
        self.playlist_id = playlist_id
        
        self.initial_arr = []

        limit = 100
        offset = 0

        while True:
            print("test1")
            
            try:
                results = self.sp.playlist_items(
                    playlist_id,
                    offset=offset,
                    limit=limit,
                    fields="items.track.id,total,next"
                )
            except Exception as e:
                print("ERROR:", e)
                return False

            for item in results['items']:
                track = item['track']
                if track:
                    self.initial_arr.append(track["id"])

            offset += limit
            if results['next'] is None:
                break
            
        if len(self.initial_arr) <= 2:
            return False
            
        shuffle(self.initial_arr)
            
        return True

