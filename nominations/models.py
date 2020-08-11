from django.contrib.auth.models import User
from django.db import models

# Create your models here.


MOVIES_CATEGORIES = (
    (1, 'Best Picture'),
    (2, 'Cinematography'),
    (3, 'Costume design'),
    (4, 'Film editing'),
    (5, 'International feature film'),
    (6, 'Makeup and hairstyling'),
    (7, 'Music'),
    (8, 'Visual effect'),
    (9, 'Adapted screenplay'),
    (10, 'Original screenplay'),
    (11, 'No movie category')
)


PERSON_CATEGORIES = (
    (1, 'Actor in a leading role'),
    (2, 'Actress in a leading role'),
    (3, 'Actor in a supporting role'),
    (4, 'Actress in a supporting role'),
    (5, 'Directing')
)


class Movie(models.Model):
    title = models.CharField(max_length=100, verbose_name='Tytuł filmu')
    nomination_category = models.IntegerField(choices=MOVIES_CATEGORIES, verbose_name='Kategorie filmu')
    winner = models.BooleanField(default=False)

    def __str__(self):
        return self.title


class Person(models.Model):
    name = models.CharField(max_length=100, verbose_name='Nominowana osoba')
    nomination_category = models.IntegerField(choices=PERSON_CATEGORIES, verbose_name='Kategoria osoby')
    movie = models.ForeignKey(Movie, on_delete=models.CASCADE)
    winner = models.BooleanField(default=False)

    def __str__(self):
        return self.name


class Profile(models.Model):
    user = models.OneToOneField(User, null=True, on_delete=models.CASCADE)
    image = models.ImageField(default='default_picture/default_avatar.JPG')

    def __str__(self):
        return self.user.username

    def delete(self, *args, **kwargs):
        self.image.delete()
        super().delete(*args, **kwargs)


class ProfileMovies(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    movies = models.ManyToManyField(Movie, related_name='movies_set')

    def __str__(self):
        return self.user.username


class ProfilePeople(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    people = models.ManyToManyField(Person, related_name='people_set')

    def __str__(self):
        return self.user.username
