from django.shortcuts import render, HttpResponseRedirect
import spotipy
import spotipy.util as util
from spotipy import oauth2
import json
from pages.models import Track, Artist
import ast
scope = 'user-library-read'
SPOTIPY_CLIENT_ID = 'b7bcf47cb6f246deae87280dc75f530d'
SPOTIPY_CLIENT_SECRET = '7286c24d1a6e4d0d8e74f6846532318d'
SPOTIPY_REDIRECT_URI = 'http://localhost:8000/after-sign-in/'
username = ''
# Create your views here.


def next_offset(n):
    try:
        return int(n['next'].split('?')[1].split('&')[0].split('=')[1])
    except ValueError:
        return None
    except AttributeError:
        return None
    except TypeError:
        return None


def home(request):
    return render(request, 'pages/home.html', {})


def sign_in(request):

    # token = util.prompt_for_user_token(username, scope)
    # print(token)
    sp_oauth = oauth2.SpotifyOAuth(SPOTIPY_CLIENT_ID, SPOTIPY_CLIENT_SECRET, SPOTIPY_REDIRECT_URI,
                                   scope=scope, cache_path=".cache-" + username)
    token_info = sp_oauth.get_cached_token()
    if not token_info:
        auth_url = sp_oauth.get_authorize_url()
        return HttpResponseRedirect(auth_url)
    sp = spotipy.Spotify(auth=token_info['access_token'])
    total = []
    results = sp.current_user_saved_tracks(limit=50)
    next = next_offset(results)

    total.append(results)
    while next and next < int(results['total']):
        next_50 = sp.current_user_saved_tracks(limit=50, offset=next)
        next = next_offset(next_50)
        total.append(next_50)
        print(next)
    tracks = []
    for r in total:
        for track in r['items']:
            tracks.append(track)
    
    for i in total:
        for tracks in i['items']:
            if Track.objects.filter(album_id=tracks['track']['id']).count() == 1:
                print('track data found, skipping') 
            else:
                print('track data not found, adding "{}"'.format(tracks['track']['name']))
                Track.objects.create(
                    name=tracks['track']['name'],
                    artist=tracks['track']['album']['artists'][0]['name'],
                    album=tracks['track']['album']['name'],
                    artist_id=tracks['track']['album']['artists'][0]['id'],
                    album_id=tracks['track']['id'],
                    genre=''
                )

            if Track.objects.filter(artist_id=tracks['track']['album']['artists'][0]['id']).count() >= 1 and Track.objects.filter(artist_id=tracks['track']['album']['artists'][0]['id']).values('genre')[0]['genre'] != '': 
                print('genre found, skipping')
                print('*******')
                Track.objects.filter(artist_id=tracks['track']['album']['artists'][0]['id']).update(genre=Track.objects.filter(artist_id=tracks['track']['album']['artists'][0]['id']).values('genre')[0]['genre'])
            else:
                a_results = sp.artist(tracks['track']['album']['artists'][0]['id'])
                print('Requesting genre from spotify')
                print('*******')
                Track.objects.filter(album_id=tracks['track']['id']).update(genre=a_results['genres'])
                
    
    genres = []           
    genre_data = Track.objects.values('genre')
    for entry in genre_data:
        genres.append(ast.literal_eval(entry['genre']))
        
    g_list = [] 
    for songs in genres:
        for g in songs:
            g_list.append(g)
    
    print(g_list.count('hip hop'))
    print(g_list.count('rap'))
    print(g_list.count('alternative rock'))
    print(g_list.count('rock'))
    print(g_list.count('pop'))
    print(g_list.count('indie rock'))
    print(g_list.count('pop rap'))

    return render(request, 'pages/sign-in.html',{'results': results['items']})


def after_sign_in(request):
    results = {}
    token = 'http://localhost:8000/after-sign-in/?{}'.format(request.GET.urlencode())
    sp_oauth = oauth2.SpotifyOAuth(SPOTIPY_CLIENT_ID, SPOTIPY_CLIENT_SECRET, SPOTIPY_REDIRECT_URI,
                                   scope=scope, cache_path=".cache-" + username)
    code = sp_oauth.parse_response_code(token)
    token_info = sp_oauth.get_access_token(code)
    
    if token_info:
        sp = spotipy.Spotify(auth=token_info['access_token'])
        results = sp.current_user_saved_tracks()
    total = []
    results = sp.current_user_saved_tracks(limit=50)
    next = next_offset(results)

    total.append(results)
    while next and next < int(results['total']):
        next_50 = sp.current_user_saved_tracks(limit=50, offset=next)
        next = next_offset(next_50)
        total.append(next_50)
        print(next)
    tracks = []
    for r in total:
        for track in r['items']:
            tracks.append(track)
    
    for i in total:
        for tracks in i['items']:
            if Track.objects.filter(album_id=tracks['track']['id']).count() == 1:
                print('track data found, skipping') 
            else:
                print('track data not found, adding "{}"'.format(tracks['track']['name']))
                Track.objects.create(
                    name=tracks['track']['name'],
                    artist=tracks['track']['album']['artists'][0]['name'],
                    album=tracks['track']['album']['name'],
                    artist_id=tracks['track']['album']['artists'][0]['id'],
                    album_id=tracks['track']['id'],
                    genre=''
                )

            if Track.objects.filter(artist_id=tracks['track']['album']['artists'][0]['id']).count() >= 1 and Track.objects.filter(artist_id=tracks['track']['album']['artists'][0]['id']).values('genre')[0]['genre'] != '': 
                print('genre found, skipping')
                print('*******')
                Track.objects.filter(artist_id=tracks['track']['album']['artists'][0]['id']).update(genre=Track.objects.filter(artist_id=tracks['track']['album']['artists'][0]['id']).values('genre')[0]['genre'])
            else:
                a_results = sp.artist(tracks['track']['album']['artists'][0]['id'])
                print('Requesting genre from spotify')
                print('*******')
                Track.objects.filter(album_id=tracks['track']['id']).update(genre=a_results['genres'])
    return render(request, 'pages/sign-in.html',{'results': results['items']})
# 
