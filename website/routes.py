from website import app
from flask import render_template,redirect,url_for,request,session
from website import mysql_utility as mysql
from website.email_engine import EmailEngine 
from spotify_bridge.search import SearchQuery,ArtistQuery,SingleArtistQuery,SinglePlaylistsQuery

@app.before_request
def before_request():
   app.logger.info("before_request")
   session["my_artist"] = None
   if request.endpoint != None and request.endpoint not in ('checklogin','login', 'static','assets') and "loggedin" in session:

        query = """SELECT spotify_artist_id FROM users WHERE id = %s"""
        tuple1 = (session["id"])
        spotify_artist_id = mysql.select(query,tuple1,1)["spotify_artist_id"]
        
        if spotify_artist_id != None and spotify_artist_id != "" and len(spotify_artist_id) > 5:
            session["my_artist"] = SingleArtistQuery().make_job(spotify_artist_id)

        tuple1 = (session["id"],"pending")
        query = """SELECT COUNT(*) FROM r_user_requests INNER JOIN requests ON r_user_requests.id_request=requests.id WHERE r_user_requests.id_user=%s AND requests.status LIKE %s"""
        session["counter_pending_requests"] = mysql.select(query,tuple1,1)["COUNT(*)"]

        tuple1 = (session["id"],"active")
        query = """SELECT COUNT(*) FROM r_user_requests INNER JOIN requests ON r_user_requests.id_request=requests.id WHERE r_user_requests.id_user=%s AND requests.status LIKE %s"""
        session["counter_active_requests"] = mysql.select(query,tuple1,1)["COUNT(*)"]





@app.route('/')
def index():
    return render_template('search.html',title="PlaylistGOATS",session=session)

@app.route('/requests/')
def requests():
    data = get_requests()["data"]
    for x in data:
        x["chat"] = get_chat(x["id_request"])["data"]
    print(data)
    return render_template('requests2.html',title="PlaylistGOATS",session=session,requests=data)

@app.route('/api/artist_link_search', methods=['GET'])
def artist_link_search():
    query = request.args.get('search_keyword')
    if query == "":
        return {"status":"error"}
    data = ArtistQuery().make_job(query)
    return {"status":"ok","data":data}


@app.route('/api/change_artist', methods=['GET'])
def change_artist():
    query = request.args.get('id')
    if query == "":
        return {"status":"error"}
    tuple1 = (query, session['id'])
    query = """UPDATE users SET spotify_artist_id = %s WHERE id = %s"""
    if mysql.update(query,tuple1) != 0:
        return {"status":"ok","data":"ok"}

@app.route('/api/playlists', methods=['POST'])
def get_playlists():
    form = request.form
    query = form["query"]
    if query == "":
        return {"status":"error"}
    data = get_random_playlists_promo()["data"]
    data.extend(SearchQuery().make_job(query))
    for p in data:
        tuple1 = (session["id"],p["playlist_id"])
        query = """SELECT * FROM r_user_requests INNER JOIN requests ON r_user_requests.id_request=requests.id WHERE r_user_requests.id_user=%s AND requests.id_playlist LIKE %s """
        result = mysql.select(query,tuple1,1)
        if not result:
            p["status"] = "not_requested"
        else:
            p["status"] = "pending"
    return {"status":"ok","data":data}

@app.route('/api/get_random_playlists_promo', methods=['GET'])
def get_random_playlists_promo():
    tuple1 = ()
    query = """SELECT id_playlist FROM playlists_promotion"""
    result = mysql.select(query,tuple1,3)
    print(result)
    data = []
    for p in result:
        d = SinglePlaylistsQuery().make_job(p["id_playlist"])
        d["promo"] = True
        data.append(d)

    for p in data:
        tuple1 = (session["id"],p["playlist_id"])
        query = """SELECT * FROM r_user_requests INNER JOIN requests ON r_user_requests.id_request=requests.id WHERE r_user_requests.id_user=%s AND requests.id_playlist LIKE %s """
        result = mysql.select(query,tuple1,1)
        if not result:
            p["status"] = "not_requested"
        else:
            p["status"] = "pending"
    return {"status":"ok","data":data}

@app.route('/api/add_request', methods=['GET'])
def add_request():
    query = request.args.get('id')

    if query == "":
        return {"status":"error"}
    p = SinglePlaylistsQuery().make_job(query)
    print(p)
    contact = p["playlist_reference"][0]

    name = p["playlist_name"]
    #1. Insert New Request
    tuple1 = (query,contact)
    query = """INSERT INTO requests (id_playlist,contact) VALUES (%s,%s)"""
    id = mysql.insert(query,tuple1,1)
    #2. Insert user-rqueste
    tuple1 = (id,session['id'])
    query = """INSERT INTO r_user_requests (id_request,id_user) VALUES (%s,%s)"""
    mysql.insert(query,tuple1,1)
    #3. Insert chat-request
    text = f"""
What’s going on, hope you’re having a good day!
Was listening to some curated playlists on Spotify & I can definitely say I’m fan of the songs you picked!
I was stoked since the songs you chose — is similar to my sound!
Here’s my Spotify page: https://open.spotify.com/artist/{session["my_artist"]["artist_id"]}
What are the steps needed to get placement on your playlists?
Let me know the info, looking forward to hearing from you!

Thanks!
    """
    send_message(text,id,name)
    return {"status":"ok"}

@app.route('/api/requests', methods=['GET'])
def get_requests():
    tuple1 = (session["id"])
    query = """SELECT id_playlist,id_request,requests.id  FROM r_user_requests INNER JOIN requests ON r_user_requests.id_request=requests.id WHERE r_user_requests.id_user=%s"""
    result = mysql.select(query,tuple1,-1)
    print(result)
    data = []
    for p in result:
        d = SinglePlaylistsQuery().make_job(p["id_playlist"])
        d["id_request"] = p["id_request"]
        data.append(d)
    print(data)
    return {"status":"ok","data":data}


@app.route('/api/login', methods=['POST'])
def login():
    msg = 'error_data'
    print("LOGGIn")
    if request.method == 'POST' and 'username' in request.form and 'password' in request.form:
        username = request.form['username']
        password = request.form['password']
        query = """SELECT * FROM users WHERE username = %s AND password = %s"""
        tuple1 = (username,password)
        account = mysql.select(query,tuple1,1)
        if account and account["password"] == password:
            session.clear()
            print("LOGGIn CORRECT")
            session['loggedin'] = True
            session['id'] = account["id"]
            msg = 'logged'
            return {"status":"ok","data":msg}
        else:
            print("LOGGIn INCORRECT")
            msg = 'incorrect'
            return {"status":"ok","data":msg}
    return {"status":"error","data":msg}



@app.route('/api/checklogin', methods=['GET'])
def checklogin():
    if "loggedin" in session:
        return {"status":"ok","data":"logged"}
    else:
        return {"status":"ok","data":"notlogged"}



@app.route('/api/update_chats', methods=['GET'])
def update_chats():
    tuple1 = ()
    query = """SELECT * FROM requests INNER JOIN r_user_requests ON r_user_requests.id_request=requests.id"""
    result = mysql.select(query,tuple1,-1)
    
    for row in result:
        new_message = EmailEngine().searchEmail(row["contact"],row["id_request"],row["id_playlist"])
        for msg in new_message:
            tuple1 = (msg["message"],row["id"],0)
            query = """INSERT INTO r_requests_chat (data,id_request,lato) VALUES (%s,%s,%s)"""
            mysql.insert(query,tuple1,1)
    return {"status":"ok"}

def get_chat(id_request):
    tuple1 = (session["id"],id_request)
    query = """SELECT data,r_requests_chat.created_at,r_requests_chat.lato FROM r_user_requests INNER JOIN r_requests_chat ON r_user_requests.id_request=r_requests_chat.id_request WHERE r_user_requests.id_user=%s AND r_user_requests.id_request=%s"""
    result = mysql.select(query,tuple1,-1)
    return {"status":"ok","data":result}

@app.route('/api/send_message', methods=['POST'])
def send_message(text="",id_request="",playlist_name="",lato=1):
    try:
        form = request.form
        text = form["text"]
        id_request = form["id_request"]
    except:
        pass
    if text == "":
        return {"status":"error"}

    tuple1 = (session["id"],id_request)
    query = """SELECT id_playlist,contact FROM r_user_requests INNER JOIN requests ON r_user_requests.id_request=requests.id WHERE r_user_requests.id_user=%s AND r_user_requests.id_request=%s"""
    result = mysql.select(query,tuple1,-1)
    id_playlist = result[0]["id_playlist"]
    mail_to = result[0]["contact"]
    subject = f"Enquiry For {playlist_name} Playlist #{id_request} #{id_playlist}"
    if EmailEngine().sendEmail(mail_to,text,subject):
        tuple1 = (text,id_request,lato)
        query = """INSERT INTO r_requests_chat (data,id_request,lato) VALUES (%s,%s,%s)"""
        mysql.insert(query,tuple1,1)
        return {"status":"ok"}
    return {"status":"error"}