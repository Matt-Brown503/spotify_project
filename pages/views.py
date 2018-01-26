from django.shortcuts import render, HttpResponseRedirect
import spotipy
import spotipy.util as util
from pages import oauth2
import json
from pages.models import Track, Artist
import ast
from django.http import JsonResponse
from rest_framework.views import APIView
from rest_framework.response import Response
from collections import Counter
from colour import Color
scope = 'user-library-read user-read-birthdate user-read-email'
SPOTIPY_CLIENT_ID = 'b7bcf47cb6f246deae87280dc75f530d'
SPOTIPY_CLIENT_SECRET = '7286c24d1a6e4d0d8e74f6846532318d'
SPOTIPY_REDIRECT_URI = 'http://localhost:8000/after-sign-in/'
username = ''
# Create your views here.

g_data = []
g_labels = []
g_values = []
g_colors = []
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
    user_data = sp.me()
    print(user_data)
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
    
    for songs in genres:
        for g in songs:
            g_data.append(g)
    
    x = Counter(g_data)
    pop_genre = ['folk-pop', 'latin-pop', 'synthpop', 'teen pop', 'korean pop', 'german pop', 'j-pop', 'dance pop']
    rap_genre = ['trap music', 'southern hip hop', 'pop rap', 'west coast rap', 'hardcore hip hop', 'deep undeground hip hop', 'alternative hip hop', 'french hip hop']
    rock_genre = ['modern rock', 'classic rock', 'pop rock', 'alternative rock', 'soft rock', 'indie rock', 'folk rock', 'blues-rock', 'southern rock', 'christian alternative rock', 'country rock', 'glam rock']
    classical = ['modern classical', 'baroque', 'classical guitar']
    jazz = ['bebop', 'swing', 'acid jazz', 'big band']
    edm = ['chillwave', 'chiptune', 'house', 'electronic', 'downtempo', 'trip hop', 'trance', 'electro swing']
    metal = ['black metal', 'alternative metal', 'glam metal',]
    punk = ['garage punk', 'pop punk', 'skate punk', 'indie punk']
    
    

    valid_genres = ['r&b', 'folk', 'reggae', 'salsa', 'latin', 'ambient', 'country', 'soul', 'funk',  'blues', 'emo', 'soundtrack', 'bossa nova', 'world']
    
    del g_labels [:]
    del g_values [:]
    del g_colors [:] 

    def colorPicker(fcolor, lcolor, count):
        start = Color(fcolor)
        c = list(start.range_to(Color(lcolor), count))
        for i in c:
            print(i.hex)
            g_colors.append(i.hex)
    
    def dataBuilder(clist, fcolor, lcolor):
        count = 0
        for word in clist:
            if word in x:
                g_labels.append(word)
                g_values.append(x[word])
                count += 1
            else:
                print('genre not found in track list')
        colorPicker(fcolor, lcolor, count)
        print(count)
    

    dataBuilder(rock_genre, 'red', '#ff7c7c')
    dataBuilder(pop_genre, 'blue', '#7c81ff')
    dataBuilder(rap_genre, 'green', '#ccffd7')

    # colorPicker(rap_genre, 'purple', 'dark purple')
    # colorPicker(rock_genre, 'white', 'black')
    # colorPicker(classical, 'blue', 'yellow')
    # colorPicker(jazz_genre, 'blue', 'yellow')
    # colorPicker(edm_genre, 'blue', 'yellow')
    # colorPicker(metal_genre, 'blue', 'yellow')
    # colorPicker(punk_genre, 'blue', 'yellow')
    # colorPicker(punk_genre, 'blue', 'yellow')
    

    

    # for word in pop_genre:
    #     if word in x:
    #         g_labels.append(word)
    #         g_values.append(x[word])
    #         colorPicker(pop_genre, '#0008ff', '#000000')
    #     else:
    #         print('genre not found in track list')
    
    # print(g_values)
    # print(g_labels)
    # print(x)


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

class ChartData(APIView):
    authentication_classes = []
    permission_classes = []

    def get(self, request, format=None):
        data = {
            'labels': g_labels,
            'values': g_values,
            'colors': g_colors,
        }
        return Response(data)