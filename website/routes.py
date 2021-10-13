from website import app
from flask import render_template,redirect,url_for,request
from spotify_bridge.search import SearchQuery

@app.route('/')
def index():
    return render_template('index.html',title="Home")

@app.route('/api/playlists', methods=['POST'])
def get_playlists():
    form = request.form
    query = form["query"]
    print(query)
    if query == "":
        return {"status":"error"}
    data = SearchQuery().make_search_request(query)
    return {"status":"ok","data":data}
