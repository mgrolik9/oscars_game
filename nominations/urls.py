from django.contrib import admin
from django.urls import path


from nominations.views import HomeView, LoginView, RegisterView, LogoutView, AddMovie,\
    AddPerson, ShowMoviesView, ShowPeopleView, ProfileMoviesView, ProfilePeopleView,\
    DeleteMovies, DeletePeople, ShowMovie, Results, Rank, ProfileView, ProfileImageView


urlpatterns = [
    path('', HomeView.as_view(), name="home"),
    path('login/', LoginView.as_view(), name="login"),
    path('sign_up/', RegisterView.as_view(), name="register"),
    path('log_out/', LogoutView.as_view(), name="logout"),
    path('show_movies/<int:category>', ShowMoviesView.as_view(), name="show-movies"),
    path('show_people/<int:category>', ShowPeopleView.as_view(), name="show-people"),
    path('add_movie/<int:movie_id>', AddMovie.as_view(), name="add-movie"),
    path('add_person/<int:person_id>', AddPerson.as_view(), name="add-person"),
    path('profile/', ProfileView.as_view(), name="profile"),
    path('profile_picture/', ProfileImageView.as_view(), name="profile-picture"),
    path('profile_movies/', ProfileMoviesView.as_view(), name="profile-movies"),
    path('profile_people/', ProfilePeopleView.as_view(), name="profile-people"),
    path('delete_movie/<int:movie_id>', DeleteMovies.as_view(), name="delete-movies"),
    path('delete_people/<int:person_id>', DeletePeople.as_view(), name="delete-people"),
    path('show_one_movie/<int:movie_id>', ShowMovie.as_view(), name="show-one-movie"),
    path('results/', Results.as_view(), name="results"),
    path('rank/', Rank.as_view(), name="rank")
]