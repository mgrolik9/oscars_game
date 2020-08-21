from django.contrib.auth import logout, login, authenticate
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.models import User
from django.core.exceptions import ObjectDoesNotExist
from django.shortcuts import render, redirect
from django.urls import reverse_lazy

from django.views import View
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage

from nominations.models import Movie, ProfileMovies, Person, ProfilePeople, MOVIES_CATEGORIES, PERSON_CATEGORIES, \
    Profile
from nominations.forms import ProfileForm
from nominations.functions import get_movie_poster, get_people_movie_poster
from oscars.local_settings import apikey

import requests


class HomeView(View):
    # Home view shows categories names as links

    def get(self, request):
        movies = dict(MOVIES_CATEGORIES)
        people = dict(PERSON_CATEGORIES)
        return render(request, 'home.html', {'movies': movies.items(),
                                             'people': people.items()})


class LoginView(View):
    # Log in for users

    def get(self, request):
        return render(request, 'login.html')

    def post(self, request):

        user = authenticate(username=request.POST.get('login'),
                            password=request.POST.get('password'))

        if user is not None:
            login(request, user)
            return redirect(reverse_lazy('home'))

        else:
            response = "Account doesn't exist."
            return render(request, 'login.html', {'response': response})


class RegisterView(View):
    # Sign in

    def get(self, request):
        return render(request, 'register.html')

    def post(self, request):

        username = request.POST.get('name')
        email = request.POST.get('email')
        password = request.POST.get('password')
        second_password = request.POST.get('second_password')
        user_check = User.objects.filter(username=username)
        user_check_2 = User.objects.filter(email=email)

        if user_check:
            response = 'This username already exists.'
        elif user_check_2:
            response = 'This e-mail already exists.'
        elif password != second_password:
            response = 'Password incorrect.'
        else:
            new_user = User.objects.create_user(username=username,
                                                password=password,
                                                email=email)
            new_user.save()
            Profile.objects.create(user=new_user)
            return redirect(reverse_lazy('login'))

        return render(request, 'register.html', {'response': response})


class LogoutView(View):
    # Log out for users

    def get(self, request):
        logout(request)
        return redirect(reverse_lazy('home'))


class ShowMoviesView(View):
    # View that shows movies from current category for all
    # For users it checks if they added any movie from current category to their profile

    def get(self, request, category):
        movies = Movie.objects.filter(nomination_category=category).order_by('title')
        category_list = dict(MOVIES_CATEGORIES)
        category_name = category_list[category]
        movies_set = {}

        get_movie_poster(movies, movies_set)

        try:
            check_user = ProfileMovies.objects.get(user=request.user)

        except (ObjectDoesNotExist, TypeError):
            return render(request, 'show_movies.html', {'movies_set': movies_set.items(),
                                                        'category_name': category_name})

        movies_list = Movie.objects.filter(movies_set=check_user.id)
        categories_set = []
        for item in movies_list:
            categories_set.append(item.nomination_category)

        if category in categories_set:
            response = 'You have successfully added movie from this category to your profile.'
            response2 = 'You can change it by clicking add to your profile button one more time.'

            return render(request, 'show_movies.html', {'movies_set': movies_set.items(),
                                                        'category_name': category_name,
                                                        'response': response,
                                                        'response2': response2,
                                                        'movies_list': movies_list})

        return render(request, 'show_movies.html', {'movies_set': movies_set.items(),
                                                    'category_name': category_name})


class AddMovie(LoginRequiredMixin, View):
    # Users can add one movie from each category to their profile

    login_url = '/login/'

    def get(self, request, movie_id):
        movie = Movie.objects.get(pk=movie_id)
        profile_movies, created = ProfileMovies.objects.get_or_create(user=request.user)
        movie_list = Movie.objects.filter(movies_set=profile_movies.id)

        for item in movie_list:
            if item.nomination_category == movie.nomination_category:
                profile_movies.movies.remove(item)
                profile_movies.movies.add(movie)
        profile_movies.movies.add(movie)
        return redirect(reverse_lazy('show-movies', args=[movie.nomination_category]))


class ShowPeopleView(View):
    # View that shows best in movies from current category for all
    # For users it checks if they added any best in from current category to their profile

    def get(self, request, category):
        people = Person.objects.filter(nomination_category=category).order_by('name')
        category_list = dict(PERSON_CATEGORIES)
        category_name = category_list[category]
        people_set = {}

        get_people_movie_poster(people, people_set)

        try:
            check_user = ProfilePeople.objects.get(user=request.user)

        except (ObjectDoesNotExist, TypeError):
            return render(request, 'show_people.html', {'people_set': people_set.items(),
                                                        'category_name': category_name})

        people_list = Person.objects.filter(people_set=check_user.id)
        categories_set = []
        for item in people_list:
            categories_set.append(item.nomination_category)

        if category in categories_set:
            response = 'You have successfully added movie from this category to your profile.'
            response2 = 'You can change it by clicking add to your profile button one more time.'

            return render(request, 'show_people.html', {'people_set': people_set.items(),
                                                        'category_name': category_name,
                                                        'response': response,
                                                        'response2': response2,
                                                        'people_list': people_list})

        return render(request, 'show_people.html', {'people_set': people_set.items(),
                                                    'category_name': category_name})


class AddPerson(LoginRequiredMixin, View):
    # Users can add one best in from each category to their profile

    login_url = '/login/'

    def get(self, request, person_id):
        person = Person.objects.get(pk=person_id)
        profile_people, created = ProfilePeople.objects.get_or_create(user=request.user)
        people_list = Person.objects.filter(people_set=profile_people.id)

        for item in people_list:
            if item.nomination_category == person.nomination_category:
                profile_people.people.remove(item)
                profile_people.people.add(person)
        profile_people.people.add(person)
        return redirect(reverse_lazy('show-people', args=[person.nomination_category]))


class ProfileMoviesView(LoginRequiredMixin, View):
    # Users can look for movies predictions that they added and delete each of them

    login_url = '/login/'

    def get(self, request):
        try:
            users_type = ProfileMovies.objects.get(user=request.user)
        except ObjectDoesNotExist:
            response = 'You have to add your nominations'
            return render(request, 'profile_movies.html', {'response': response})

        movies_list = Movie.objects.filter(movies_set=users_type.id).order_by('nomination_category')

        page = request.GET.get('page', 1)

        paginator = Paginator(movies_list, 5)
        try:
            movies = paginator.page(page)
        except PageNotAnInteger:
            movies = paginator.page(1)
        except EmptyPage:
            movies = paginator.page(paginator.num_pages)

        return render(request, 'profile_movies.html', {'movies': movies})


class ProfilePeopleView(LoginRequiredMixin, View):
    # Users can look for best in predictions that they added and delete each of them

    login_url = '/login/'

    def get(self, request):
        try:
            users_type = ProfilePeople.objects.get(user=request.user)
        except ObjectDoesNotExist:
            response = 'You have to add your nominations'
            return render(request, 'profile_people.html', {'response': response})

        people_list = Person.objects.filter(people_set=users_type.id).order_by('nomination_category')
        return render(request, 'profile_people.html', {'people_list': people_list})


class DeleteMovies(LoginRequiredMixin, View):
    # Deleting movies button

    def get(self, request, movie_id):
        movie = Movie.objects.get(pk=movie_id)
        profile_movies = ProfileMovies.objects.get(user=request.user)
        profile_movies.movies.remove(movie)
        return redirect(reverse_lazy('profile-movies'))


class DeletePeople(LoginRequiredMixin, View):
    # Deleting best in button

    def get(self, request, person_id):
        person = Person.objects.get(pk=person_id)
        profile_people = ProfilePeople.objects.get(user=request.user)
        profile_people.people.remove(person)
        return redirect(reverse_lazy('profile-people'))


class ShowMovie(View):
    # Show one movie details and related nomination categories for movie and best in

    def get(self, request, movie_id):
        movie = Movie.objects.get(pk=movie_id)
        movies_list = Movie.objects.filter(title=movie.title).order_by('nomination_category')
        people_list = Person.objects.all().order_by('nomination_category')
        people_nominations_set = []

        payload = {'t': movie.title, 'y': 2019, 'apikey': apikey}
        response = requests.get("http://www.omdbapi.com/", params=payload)
        json_response = response.json()
        poster = json_response.get("Poster")
        plot = json_response.get("Plot")

        for person in people_list:
            if person.movie.title == movie.title:
                people_nominations_set.append(person)

        if len(people_nominations_set) > 0:
            return render(request, 'show_one_movie.html', {'movie': movie,
                                                           'poster': poster,
                                                           'plot': plot,
                                                           'movies_list': movies_list,
                                                           'people_nominations_set': people_nominations_set})
        else:
            return render(request, 'show_one_movie.html', {'movie': movie,
                                                           'poster': poster,
                                                           'plot': plot,
                                                           'movies_list': movies_list})


class Results(View):
    # Show official winners of oscars completed by admin

    def get(self, request):

        winners_set = {}
        winners_people_set = {}

        try:
            movies_list = Movie.objects.filter(winner=True).order_by('nomination_category')
            people_list = Person.objects.filter(winner=True).order_by('nomination_category')
        except ObjectDoesNotExist:
            try:
                movies_list = Movie.objects.filter(winner=True).order_by('nomination_category')
            except ObjectDoesNotExist:
                try:
                    people_list = Person.objects.filter(winner=True).order_by('nomination_category')
                except ObjectDoesNotExist:
                    return render(request, 'results.html')

                get_people_movie_poster(people_list, winners_people_set)
                return render(request, 'results.html', {'winners_people_set': winners_people_set.items()})

            get_movie_poster(movies_list, winners_set)
            return render(request, 'results.html', {'winners_set': winners_set.items()})

        get_movie_poster(movies_list, winners_set)
        get_people_movie_poster(people_list, winners_people_set)
        return render(request, 'results.html', {'winners_set': winners_set.items(),
                                                'winners_people_set': winners_people_set.items()})


class Rank(LoginRequiredMixin, View):
    # Calculate scores for logged user and let them find other users scores

    login_url = '/login/'

    def get(self, request):

        try:
            user_movies = ProfileMovies.objects.get(user=request.user)
            user_people = ProfilePeople.objects.get(user=request.user)
        except ObjectDoesNotExist:
            response = 'You have to add oscars predictions first'
            return render(request, 'rank.html', {'response': response})

        count_movies = Movie.objects.filter(movies_set=user_movies.id).count()
        count_people = Person.objects.filter(people_set=user_people.id).count()
        count_all = count_movies + count_people
        number_of_categories = (len(dict(MOVIES_CATEGORIES)) + len(dict(PERSON_CATEGORIES))) - 1
        if count_all != number_of_categories:
            response = 'You have to add predictions from all categories to your profile'
            return render(request, 'rank.html', {'response': response})

        user_movies_set = Movie.objects.filter(movies_set=user_movies.id, winner=True).count()
        user_people_set = Person.objects.filter(people_set=user_people.id, winner=True).count()
        user_result = user_movies_set + user_people_set
        return render(request, 'rank.html', {'number_of_categories': number_of_categories,
                                             'user_result': user_result})

    def post(self, request):
        checked_username = request.POST.get('search_user')
        number_of_categories = (len(dict(MOVIES_CATEGORIES)) + len(dict(PERSON_CATEGORIES))) - 1

        try:
            user_movies = ProfileMovies.objects.get(user=request.user)
            user_people = ProfilePeople.objects.get(user=request.user)
        except ObjectDoesNotExist:
            response = 'You have to add oscars predictions first'
            try:
                checked_user = User.objects.get(username=checked_username)
            except ObjectDoesNotExist:
                response2 = 'User not found'
                return render(request, 'rank.html', {'response': response,
                                                     'response2': response2})

            try:
                checked_user_movies = ProfileMovies.objects.get(user=checked_user)
                checked_user_people = ProfilePeople.objects.get(user=checked_user)
            except ObjectDoesNotExist:
                response2 = 'This user did not add oscars predictions'
                return render(request, 'rank.html', {'response': response,
                                                     'response2': response2})

            count_user_movies = Movie.objects.filter(movies_set=checked_user_movies.id).count()
            count_user_people = Person.objects.filter(people_set=checked_user_people.id).count()
            count_user_all = count_user_movies + count_user_people
            if count_user_all != number_of_categories:
                response2 = 'User did not choose his predictions for all categories yet'
                return render(request, 'rank.html', {'response': response,
                                                     'response2': response2})

            checked_user_movies_set = Movie.objects.filter(movies_set=checked_user_movies.id, winner=True).count()
            checked_user_people_set = Person.objects.filter(people_set=checked_user_people.id, winner=True).count()
            checked_result = checked_user_movies_set + checked_user_people_set
            return render(request, 'rank.html', {'response': response,
                                                 'number_of_categories': number_of_categories,
                                                 'checked_username': checked_username,
                                                 'checked_result': checked_result})

        count_movies = Movie.objects.filter(movies_set=user_movies.id).count()
        count_people = Person.objects.filter(people_set=user_people.id).count()
        count_all = count_movies + count_people
        if count_all != number_of_categories:
            response = 'You have to add predictions from all categories to your profile'

            try:
                checked_user = User.objects.get(username=checked_username)
            except ObjectDoesNotExist:
                response2 = 'User not found'
                return render(request, 'rank.html', {'response': response,
                                                     'response2': response2})

            try:
                checked_user_movies = ProfileMovies.objects.get(user=checked_user)
                checked_user_people = ProfilePeople.objects.get(user=checked_user)
            except ObjectDoesNotExist:
                response2 = 'This user did not add oscars predictions'
                return render(request, 'rank.html', {'response': response,
                                                     'response2': response2})

            count_user_movies = Movie.objects.filter(movies_set=checked_user_movies.id).count()
            count_user_people = Person.objects.filter(people_set=checked_user_people.id).count()
            count_user_all = count_user_movies + count_user_people
            if count_user_all != number_of_categories:
                response2 = 'User did not choose his predictions for all categories yet'
                return render(request, 'rank.html', {'response': response,
                                                     'response2': response2})

            checked_user_movies_set = Movie.objects.filter(movies_set=checked_user_movies.id, winner=True).count()
            checked_user_people_set = Person.objects.filter(people_set=checked_user_people.id, winner=True).count()
            checked_result = checked_user_movies_set + checked_user_people_set
            return render(request, 'rank.html', {'response': response,
                                                 'number_of_categories': number_of_categories,
                                                 'checked_username': checked_username,
                                                 'checked_result': checked_result})

        user_movies_set = Movie.objects.filter(movies_set=user_movies.id, winner=True).count()
        user_people_set = Person.objects.filter(people_set=user_people.id, winner=True).count()
        user_result = user_movies_set + user_people_set

        try:
            checked_user = User.objects.get(username=checked_username)
        except ObjectDoesNotExist:
            response2 = 'User not found'
            return render(request, 'rank.html', {'number_of_categories': number_of_categories,
                                                 'user_result': user_result,
                                                 'response2': response2})

        try:
            checked_user_movies = ProfileMovies.objects.get(user=checked_user)
            checked_user_people = ProfilePeople.objects.get(user=checked_user)
        except ObjectDoesNotExist:
            response2 = 'This user did not add oscars predictions'
            return render(request, 'rank.html', {'number_of_categories': number_of_categories,
                                                 'user_result': user_result,
                                                 'response2': response2})

        count_user_movies = Movie.objects.filter(movies_set=checked_user_movies.id).count()
        count_user_people = Person.objects.filter(people_set=checked_user_people.id).count()
        count_user_all = count_user_movies + count_user_people
        if count_user_all != number_of_categories:
            response2 = 'User did not choose his predictions for all categories yet'
            return render(request, 'rank.html', {'number_of_categories': number_of_categories,
                                                 'user_result': user_result,
                                                 'response2': response2})

        checked_user_movies_set = Movie.objects.filter(movies_set=checked_user_movies.id, winner=True).count()
        checked_user_people_set = Person.objects.filter(people_set=checked_user_people.id, winner=True).count()
        checked_result = checked_user_movies_set + checked_user_people_set
        return render(request, 'rank.html', {'number_of_categories': number_of_categories,
                                             'user_result': user_result,
                                             'checked_username': checked_username,
                                             'checked_result': checked_result})


class ProfileView(LoginRequiredMixin, View):
    # Profile shows profile photo, links to change profile photo and edit oscars predictions

    login_url = '/login/'

    def get(self, request):
        profile_user = Profile.objects.get(user=request.user)
        return render(request, 'profile.html', {'profile_user': profile_user})


class ProfileImageView(LoginRequiredMixin, View):
    # View with form to change profile photo

    login_url = '/login/'

    def get(self, request):
        form = ProfileForm

        return render(request, 'profile_picture.html', {'form': form})

    def post(self, request):
        form = ProfileForm(request.POST, request.FILES)

        if form.is_valid():
            profile_image = Profile.objects.get(user=request.user)
            if profile_image.image == 'default_picture/default_avatar.JPG':
                profile_image.image = form.cleaned_data['image']
                profile_image.save()
            else:
                profile_image.image.delete()
                profile_image.image = form.cleaned_data['image']
                profile_image.save()
            return redirect(reverse_lazy('profile'))
