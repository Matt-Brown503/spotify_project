from django.db import models


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
