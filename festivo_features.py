import spotipy
import sys
import json
import pandas as pd
import festivo_classes as sc

from festivo_classes import Artist
from collections import defaultdict
from spotipy.oauth2 import SpotifyClientCredentials
from spotipy.oauth2 import SpotifyOAuth
from dotenv import load_dotenv


def userAuthentication():
    """Authenticates user

    Returns
    -------
    sp : class Spotify
    Spotify API Client obj
    """
    load_dotenv()
    scope = "user-top-read playlist-modify-public"
    sp = spotipy.Spotify(auth_manager=SpotifyOAuth(scope=scope))

    return sp


def userTermInput():
    """obtain user specified range

    Returns
    -------
    rangeIn : int
        user choice for term
    """
    print(
        """
        (1) short term: (approximately last 4 weeks of listerning history)
        (2) medium term: (approxiamtely last 6 months of listening history)
        (3) long term: (approximately last few years of listening history)
        (4) all data available: (combination of all three terms)
        """
    )
    rangeIn = input("Enter the value for the range you'd like to use: ")
    while True:
        if rangeIn.isdigit() and int(rangeIn) in [1,2,3,4]:
            break
        print("Invalid input, Please choose between (1), (2), (3), or (4) ")
        rangeIn = input("Enter the value for the range you'd like to use: ")

    return int(rangeIn)


def getTopAndRelatedArtists(sp):
    """Call to access users top and related artists based on user specififed range

    Parameters
    ----------
    sp : class Spotify
        Spotify API Client obj
    
    Returns
    -------
    top_artists : set
        set of users top artists
    related_artists : dic
        dic of related artists based on users top artists
    """
    # rangeIn = userTermInput()
    # ranges = {1:'short_term', 2:'medium_term', 3:'long_term'}
    top_artists_lst = []
    related_artists_lst = []

    for timeRange in ['short_term', 'medium_term', 'long_term']:
        top_artists_json = sp.current_user_top_artists(time_range=timeRange, limit=50)
        top_artists, related_artists = accessTopandRelatedArtists(sp, top_artists_json)
        top_artists_lst.append(top_artists)
        related_artists_lst.append(related_artists)



    # if term in ['short_term', 'medium_term', 'long_term']:
    # # if rangeIn in [1,2,3]:
    #     top_artists_json = sp.current_user_top_artists(time_range=term, limit=50)
    #     top_artists, related_artists = accessTopandRelatedArtists(sp, top_artists_json)
    # else: # rangeIn == 4
    #     top_artists = []
    #     related_artists = {}
    #     for values in ['short_term', 'medium_term', 'long_term']:
    #         top_artists_json = sp.current_user_top_artists(time_range=values, limit=50)
    #         top, related = accessTopandRelatedArtists(sp, top_artists_json)
    #         top_artists += top
    #         related_artists.update(related)
    #     top_artists = set(top_artists)

    # for i in range(len(related_artists_lst)):
    #     related_artists_lst[i] = {k : v for k, v in sorted(related_artists_lst[i].items(), key=lambda item: item[1], reverse=True)}

    return top_artists_lst, related_artists_lst


def accessTopandRelatedArtists(sp, top_artists_json):
    """gets users top artists and related artist from Spotify API

    Parameters
    ----------
    sp : class Spotify
        Spotify API Client obj
    top_artists_json : dic
        json variable containing users top artists information from Spotify API 

    Returns
    -------
    top_artists : list
        list of users top artists
    rel_artists : dic
        dic of related artists based on users top artists
    """
    top_artists = []
    rel_artists = {}

    for i, item in enumerate(top_artists_json['items']):
        top_artist = Artist(name=item['name'], _id=item['id'], genres=item['genres'], image=item['images'][0]['url'], uri=item['uri'])
        top_artists.append(top_artist)
        related_artists = sp.artist_related_artists(top_artist._id)['artists']
        for j,rel_item in enumerate(related_artists):
            rel_artist = Artist(name=rel_item['name'], _id=rel_item['id'], genres=rel_item['genres'], image=rel_item['images'][0]['url'], uri=rel_item['uri'])
            if rel_artist in rel_artists:
                rel_artists[rel_artist] += 1
            else:
                rel_artists[rel_artist] = 1

            if i >= 40 and j >= 3:
                break
            elif i >= 30 and j >= 7:
                break
            elif i >= 20 and j >= 11:
                break
            elif i >= 10 and j >= 15:
                break
            else:
                continue

    return top_artists, rel_artists


def readCSVFile():
    """reads in csv file of artists

    Returns
    -------
    coachella_artists : list
        list of coachella artists
    """
    df = pd.read_csv('static/Coachella_2022_Artists - Sheet1.csv')
    coachella_artists = df.Artists.to_list()

    return coachella_artists


def generateRecommendedArtists(top_artists_lst, related_artists_lst, coachella_artists):
    """Generates recommended artists based on user's top artists and the festival artists

    Parameters
    ----------
    top_artists : set(type(Class Artist))
        set containing users top artists
    related_artists : dic(type(Class Artist): int)
        dic containing artists related to users top artists, along with their match index

    Returns
    -------
    recommended_artists : dic
        a dic of Class Artists and their match index
    """
    recommended_artists_lst = []
    for i in range(len(top_artists_lst)):
        recommended_artists = {}
        related_artists_and_index = getArtistAndMatchIndex(related_artists_lst[i])
        top_artists_dic = getPopularArtists(top_artists_lst[i])
        top_match_index = 100
        for artist in coachella_artists:
            if artist in getArtistNames(top_artists_lst[i]):
                recommended_artists[top_artists_dic[artist]] = top_match_index
            elif artist in getArtistNames(related_artists_lst[i]):
                recommended_artists[related_artists_and_index[artist][0]] = related_artists_and_index[artist][1]
            
        recommended_artists_lst.append(recommended_artists)
    
    # for i in range(len(recommended_artists_lst)):
    #     recommended_artists_lst[i] = {k : v for k, v in sorted(recommended_artists_lst[i].items(), key=lambda item: item[1], reverse=True)}

    return recommended_artists_lst


def getPopularArtists(artists):
    artist_dic = {}
    for artist in artists:
        artist_dic[artist.name] = artist

    return artist_dic

def getArtistAndMatchIndex(artists):
    artist_dic = {}
    for artist, index in artists.items():
        artist_dic[artist.name] = [artist, index]

    return artist_dic


def getArtistNames(artists):
    artist_names = []
    for artist in artists:
        artist_names.append(artist.name)

    return artist_names


def promptFinished(task):
    print(f"Finished with {task}.\n")
    

def userPlaylistInput():
    """Ask if user would like to create a playlist

    Returns
    -------
    playlist_bool : bool
        whether user wants to create a playlist
    """

    print(
        """
        Would you like to create a playlist based on your recommended artists
        top tracks?

        (1) Yeah! :)
        (2) No. >:(
        """
    )
    playIn = input("Enter the value for your decision: ")
    while True:
        if playIn.isdigit() and int(playIn) in [1,2]:
            break
        print("Invalid input, Please choose between (1), or (2)")
        playIn = input("Enter the value for your decision: ")

    if int(playIn) == 1:
        return True
    else:
        return False


def userPlaylistNameInput():
    """Get the name of the playlist from user

    Returns
    -------
    playlist_name : str
        name of playlist
    """
    playNameIn = input("Enter the name of your playlist: ")

    return playNameIn


def getRecommendedTopTracks(sp, recommended_artists):
    top_tracks = []
    for artist in recommended_artists.keys():
        top_tracks_json = sp.artist_top_tracks(artist._id)
        tracks = top_tracks_json['tracks']
        for i in range(len(tracks) - 5):
            track = sc.Track(name=tracks[i]['name'], _id=tracks[i]['id'])
            top_tracks.append(track)
    
    # for i, track in enumerate(top_tracks):
    #     print(f"{i}) {track._id} {track.name}")

    return top_tracks


def createPlaylist(sp, pName, pDesc):
    user_id = sp.me()['id'] #User class?
    # playlist_name = userPlaylistNameInput()
    new_playlist = sp.user_playlist_create(user=user_id, name=pName, description=pDesc)
    playlist = sc.Playlist(name=new_playlist['name'], _id=new_playlist['id'])

    return playlist
    # if checkIfPlaylistExist(sp):
    #     pass


def chunks(tracks, n):
    n = max(1, n)

    return (tracks[i:i+n] for i in range(0, len(tracks), n))


def getTrackIds(recc_top_tracks):
    track_ids = []
    for track in recc_top_tracks:
        track_ids.append(track._id)

    track_ids_chunks = chunks(track_ids, 10)

    return track_ids_chunks


def addTracksToPlaylist(sp, playlist, recc_top_tracks):
    track_ids_chunks = getTrackIds(recc_top_tracks)
    for tracks in track_ids_chunks:
        sp.playlist_add_items(playlist._id, tracks)
        

# def checkIfPlaylistExist(sp):
#     pass


def createRecommendedPlaylist(sp, recommended_artists, term):
    recc_top_tracks = getRecommendedTopTracks(sp, recommended_artists) # list/set/dic of object Track
    # promptFinished("getting top recommended tracks")
    timeRange = {
        "shortTerm": "Last Month",
        "medTerm": "Last 6 Months",
        "longTerm": "All Time"
    }
    pName = f"Festify - Coachella 2022 Reccommended Artists - {timeRange[term]}"
    pDesc = "Your recommended artists for Coachella 2022 generated by Festify!\n\nThis isn't all-inclusive but its a good place to start. :)"
    playlist = createPlaylist(sp, pName, pDesc) # object Playlist
    # promptFinished("creating playlist")
    addTracksToPlaylist(sp, playlist, recc_top_tracks)
    # promptFinished("adding tracks to new playlist")
    

# def displayArtists(artists, name):
#     print(name)
#     for i,artist in enumerate(artists):
#         print(f"{i}) {artist}")
#     print()


# def 


def main():
    sp = userAuthentication()
    top_artists, related_artists = getTopAndRelatedArtists(sp)
    coachella_artists = readCSVFile()
    recommended_artists = generateRecommendedArtists(top_artists, related_artists, coachella_artists)
    promptFinished("obtaining your recommended artists")
    if userPlaylistInput():
        createRecommendedPlaylist(sp, recommended_artists)
    promptFinished("creating your recommended artists playlist")


if __name__ == "__main__":
    main()




