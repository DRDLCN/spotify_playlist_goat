class Playlist():
    def __init__(self, data):
        self.playlist_id = data["playlist_id"]
        self.playlist_description = data["playlist_description"]
        self.playlist_name = data["playlist_name"]
        self.playlist_owner_id = data["playlist_owner_id"]
        self.playlist_reference = data["playlist_reference"]
        self.playlist_number_of_songs = data["playlist_number_of_songs"]
        
