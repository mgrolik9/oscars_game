from django.contrib import admin


from nominations.models import Movie, Person, ProfileMovies, ProfilePeople, Profile

# Register your models here.


@admin.register(Movie)
class MovieAdmin(admin.ModelAdmin):
    list_display = ('title', 'nomination_category', 'winner')


@admin.register(Person)
class PersonAdmin(admin.ModelAdmin):
    list_display = ('name', 'nomination_category', 'movie', 'winner')


@admin.register(ProfileMovies)
class ProfileMoviesAdmin(admin.ModelAdmin):
    list_display = ('user', 'movie_list')

    def movie_list(self, obj):
        return ", ".join([str(t) for t in obj.movies.all()])


@admin.register(ProfilePeople)
class ProfilePeopleAdmin(admin.ModelAdmin):
    list_display = ('user', 'people_list')

    def people_list(self, obj):
        return ", ".join([str(t) for t in obj.people.all()])


@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'image')

