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
import festivo_features as festivo

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


@app.route("/display", methods=["POST", "GET"])
def display():
    cache_handler = spotipy.cache_handler.CacheFileHandler(cache_path=session_cache_path())
    auth_manager = spotipy.oauth2.SpotifyOAuth(cache_handler=cache_handler)
    if not auth_manager.validate_token(cache_handler.get_cached_token()):
        return redirect('/')
    spotify = spotipy.Spotify(auth_manager=auth_manager)
    session["spotify"] = spotify

    top_artists_lst, related_artists_lst = festivo.getTopAndRelatedArtists(spotify)
    coachella_artists = festivo.readCSVFile()
    recommended_artists_lst = festivo.generateRecommendedArtists(top_artists_lst, related_artists_lst, coachella_artists)
    session["recc"] = recommended_artists_lst
    session["shortTerm"] = [(x.image, x.name, y, x.uri) for (x,y) in recommended_artists_lst[0].items()]
    session["medTerm"] = [(x.image, x.name, y, x.uri) for (x,y) in recommended_artists_lst[1].items()]
    session["longTerm"] = [(x.image, x.name, y, x.uri) for (x,y) in recommended_artists_lst[2].items()]

    return redirect(url_for("allTimeRanges", timeRange="shortTerm"))



@app.route("/display/<timeRange>", methods=["POST", "GET"])
def allTimeRanges(timeRange):
    if request.method == "POST":
        indicator = int(request.form["indicator"])
        if indicator == 1:
            timeRange = request.form["timeRange"]
            return redirect(url_for("allTimeRanges", timeRange=timeRange))
        else:
            if timeRange == "shortTerm":
                festivo.createRecommendedPlaylist(session["spotify"], session["recc"][0], timeRange)
            elif timeRange == "medTerm":
                festivo.createRecommendedPlaylist(session["spotify"], session["recc"][1], timeRange)
            else:
                festivo.createRecommendedPlaylist(session["spotify"], session["recc"][2], timeRange)
            flash("Your playlist has successfully been created!")
            return redirect(url_for("allTimeRanges", timeRange=timeRange))
    else:
        return render_template("display.html", term=session[timeRange], termName=timeRange)


'''
Following lines allow application to be run more conveniently with
`python app.py` (Make sure you're using python3)
(Also includes directive to leverage pythons threading capacity.)
'''
if __name__ == '__main__':
    app.run(threaded=True, port=int(os.environ.get("PORT",
                                                   os.environ.get("SPOTIPY_REDIRECT_URI", 8080).split(":")[-1])))