"""
Prerequisites

    pip3 install spotipy Flask Flask-Session

    // from your [app settings](https://developer.spotify.com/dashboard/applications)
    export SPOTIPY_CLIENT_ID=client_id_here
    export SPOTIPY_CLIENT_SECRET=client_secret_here
    export SPOTIPY_REDIRECT_URI='http://127.0.0.1:8080' // must contain a port
    // SPOTIPY_REDIRECT_URI must be added to your [app settings](https://developer.spotify.com/dashboard/applications)
    OPTIONAL
    // in development environment for debug output
    export FLASK_ENV=development
    // so that you can invoke the app outside of the file's directory include
    export FLASK_APP=/path/to/spotipy/examples/app.py
 
    // on Windows, use `SET` instead of `export`

Run app.py

    python3 app.py OR python3 -m flask run
    NOTE: If receiving "port already in use" error, try other ports: 5000, 8090, 8888, etc...
        (will need to be updated in your Spotify app and SPOTIPY_REDIRECT_URI variable)
"""

import os
from time import time
from flask import Flask, session, request, redirect, render_template, url_for, flash
from flask_session import Session
from datetime import timedelta
from dotenv import load_dotenv
import spotipy
import uuid
import spotify_features as festify

load_dotenv()

app = Flask(__name__)
app.config['SECRET_KEY'] = os.urandom(64)
app.config['SESSION_TYPE'] = 'filesystem'
app.config['SESSION_FILE_DIR'] = './.flask_session/'
app.permanent_session_lifetime = timedelta(minutes=15)
Session(app)

caches_folder = './.spotify_caches/'
if not os.path.exists(caches_folder):
    os.makedirs(caches_folder)


def session_cache_path():
    return caches_folder + session.get('uuid')


@app.route('/')
def index():
    if not session.get('uuid'):
        # Step 1. Visitor is unknown, give random ID
        session['uuid'] = str(uuid.uuid4())

    cache_handler = spotipy.cache_handler.CacheFileHandler(cache_path=session_cache_path())
    auth_manager = spotipy.oauth2.SpotifyOAuth(scope='user-top-read playlist-modify-public',
                                                cache_handler=cache_handler, 
                                                show_dialog=True)

    if request.args.get("code"):
        # Step 3. Being redirected from Spotify auth page
        auth_manager.get_access_token(request.args.get("code"))
        return redirect('/')

    if not auth_manager.validate_token(cache_handler.get_cached_token()):
        # Step 2. Display sign in link when no token
        auth_url = auth_manager.get_authorize_url()
        # return render_template("index1.html")
        return render_template("index1.html", auth_url=auth_url)

    # Step 4. Signed in, display data
    spotify = spotipy.Spotify(auth_manager=auth_manager)
    return render_template("index2.html", spotify=spotify)


@app.route('/sign_out')
def sign_out():
    try:
        # Remove the CACHE file (.cache-test) so that a new user can authorize.
        os.remove(session_cache_path())
        session.clear()
    except OSError as e:
        print ("Error: %s - %s." % (e.filename, e.strerror))
    return redirect('/')


@app.route("/recommendations", methods=["POST", "GET"])
def recommendations():
    if request.method == "POST":
        term = request.form["term"]
        return redirect(url_for("display", trm=term))
    else:
        return render_template("recommendations.html")


@app.route("/recommendations/<trm>", methods=["POST", "GET"])
def display(trm):
    if request.method == "POST":
        playlistName = request.form["nm"]
        description = request.form["dp"]
        festify.createRecommendedPlaylist(session["spotify"], session["recc"], pName=playlistName, pDesc=description)
        flash(f"Your playlist, {playlistName}, has been made!", "info")
        return render_template("display.html", art=session["art"])
    else:
        cache_handler = spotipy.cache_handler.CacheFileHandler(cache_path=session_cache_path())
        auth_manager = spotipy.oauth2.SpotifyOAuth(cache_handler=cache_handler)
        if not auth_manager.validate_token(cache_handler.get_cached_token()):
            return redirect('/')
            
        spotify = spotipy.Spotify(auth_manager=auth_manager)
        session["spotify"] = spotify

        top_artists, related_artists = festify.getTopAndRelatedArtists(spotify, trm)
        coachella_artists = festify.readCSVFile()
        recommended_artists = festify.generateRecommendedArtists(top_artists, related_artists, coachella_artists)
        session["recc"] = recommended_artists
        art = [(x.image, x.name, y) for (x,y) in recommended_artists.items()]
        session["art"] = art

        return render_template("display.html", art=art)



'''
Following lines allow application to be run more conveniently with
`python app.py` (Make sure you're using python3)
(Also includes directive to leverage pythons threading capacity.)
'''
if __name__ == '__main__':
    app.run(threaded=True, port=int(os.environ.get("PORT",
                                                   os.environ.get("SPOTIPY_REDIRECT_URI", 8080).split(":")[-1])))