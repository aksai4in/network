
from django.urls import path

from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("posts/<str:page>", views.posts, name="posts"),
    path("posts", views.postic, name="postic"),
    path("following/<str:username>", views.following, name="following"),
    path("profile/<str:username>", views.profile, name="profile"),
    path("login", views.login_view, name="login"),
    path("logout", views.logout_view, name="logout"),
    path("register", views.register, name="register"),
    #api for retreving posts
    path("profilePosts/<str:username>/<str:page>", views.profile_posts, name="profile_posts"),
    path("liked", views.liked, name="liked")
]
