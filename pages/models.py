from django.db import models
from django.contrib.auth.models import AbstractUser

class User(AbstractUser):
    user_id = models.CharField(max_length=100)
    user_img = models.CharField(max_length=200)
    user_token = models.CharField(max_length=1000)


class Track(models.Model):
    name = models.CharField(max_length=100)
    artist = models.CharField(max_length=100)
    album = models.CharField(max_length=100)
    artist_id = models.CharField(max_length=100)
    album_id = models.CharField(max_length=100)
    genre = models.CharField(max_length=100)

class Artist(models.Model):
    name = models.CharField(max_length=100)
    genre = models.CharField(max_length=100)
    artist_id = models.CharField(max_length=100)

# class UserTracksJunction(models.Model):
#     user_id = models.ForeignKey(User)
#     track_id = models.ForeignKey(Track)
    

