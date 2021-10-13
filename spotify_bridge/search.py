from spotify_bridge.token_manager import TokenManager
import requests,re

class SearchQuery():
    def __init__(self, query=""):
        self.query = query
        self.token = TokenManager().get_token()
        self.headers = headers = {
            'Accept': 'application/json',
            'Content-Type': 'application/json',
            'Authorization': f'Bearer {self.token}',
        }
        self.results = []
    
    def make_search_request(self,query=""):
        
        params = (
            ('limit', '50'),
            ('q', query),
            ('type', 'playlist'),
        )

        response = requests.get('https://api.spotify.com/v1/search', headers=self.headers, params=params).json()
        
        for list in response["playlists"]["items"]:
            data = {}
            data["playlist_id"] = list["id"]
            data["playlist_description"] = list["description"]
            data["playlist_name"] = list["name"]
            data["playlist_owner_id"] = list["owner"]["id"]
            data["playlist_reference"] = re.findall(r'[\w.+-]+@[\w-]+\.[\w.-]+|@[a-zA-Z0-9_]{0,15}', data["playlist_description"])
            data["playlist_number_of_songs"] = list["tracks"]["total"]
            if self.check_active_list(data):
                #data.update(self.get_playlist_info(data["playlist_id"]))
                self.results.append(data)
        return self.results

    def check_active_list(self,data):
        if data["playlist_description"] == "" or data["playlist_name"] == "" or data["playlist_number_of_songs"] == 0:
            return False
        return True

    def get_playlist_info(self,id):
        params = (
            ('fields','followers,tracks.items(track(id))'),
        )
        response = requests.get(f'https://api.spotify.com/v1/playlists/{id}', headers=self.headers,params=params).json()
        
        data = []
        for track in response["tracks"]["items"]:
            t = {}
            t["id"] = track["track"]["id"]
            data.append(t)

        json = {"playlist_followers":response["followers"]["total"]}#,"playlist_tracks":data}
        return json
