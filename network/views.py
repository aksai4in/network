from django.contrib.auth import authenticate, login, logout
from django.core.paginator import Paginator
from django.db import IntegrityError
from django.http import HttpResponse, HttpResponseRedirect, JsonResponse
from django.shortcuts import render
from django.urls import reverse
from django import forms
from .models import User, Post
import json
from django.views.decorators.csrf import csrf_exempt


def index(request):
    posts = Post.objects.all() 
    posts = posts.order_by("-timestamp").all()
    paginator = Paginator(posts, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    return render(request, "network/index.html", {
        "page_obj": page_obj,
        "last_current": page_obj.paginator.num_pages - page_obj.number,
        "preprevious":page_obj.number - 2
    })


def login_view(request):
    if request.method == "POST":

        # Attempt to sign user in
        username = request.POST["username"]
        password = request.POST["password"]
        user = authenticate(request, username=username, password=password)

        # Check if authentication successful
        if user is not None:
            login(request, user)
            return HttpResponseRedirect(reverse("index"))
        else:
            return render(request, "network/login.html", {
                "message": "Invalid username and/or password."
            })
    else:
        return render(request, "network/login.html")


def logout_view(request):
    logout(request)
    return HttpResponseRedirect(reverse("index"))


def register(request):
    if request.method == "POST":
        username = request.POST["username"]
        email = request.POST["email"]

        # Ensure password matches confirmation
        password = request.POST["password"]
        confirmation = request.POST["confirmation"]
        if password != confirmation:
            return render(request, "network/register.html", {
                "message": "Passwords must match."
            })

        # Attempt to create new user
        try:
            user = User.objects.create_user(username, email, password)
            user.save()
        except IntegrityError:
            return render(request, "network/register.html", {
                "message": "Username already taken."
            })
        login(request, user)
        return HttpResponseRedirect(reverse("index"))
    else:
        return render(request, "network/register.html")

@csrf_exempt
def posts(request, page):
    if request.method != "POST":
        posts = Post.objects.all()
        posts = posts.order_by("-timestamp").all()
        paginator = Paginator(posts, 10)
        page = paginator.get_page(page)
        likedPosts = User.objects.get(username = request.user).liked.all()
        return JsonResponse([[post.serialize() for post in page.object_list], [post.id for post in likedPosts]],safe=False)
@csrf_exempt
def postic(request):
        data = json.loads(request.body)
        user = User.objects.get(username = data.get("user"))
        if(data.get("like")):
            post = Post.objects.get(id = data.get("post_id"))
            if(user in post.likes.all()):
                post.likes.remove(user)
                post.save()
                return JsonResponse({"message": "unliked!", "likes": post.likes.all().count()}, status=201)
            else:
                post.likes.add(user)
                post.save()
                return JsonResponse({"message": "liked!", "likes": post.likes.all().count() }, status=201)

        else:
            content = data.get("content")
            if(data.get("post_id") != None):
                post = Post.objects.get(id = data.get("post_id"))
                post.content = content
                post.save()
                return JsonResponse({"message": "edited!"}, status=201)
            else:
                post = Post(user = user, content = content)
                post.save()
                return JsonResponse({"message": "posted!", "post": post.serialize()}, status=201)
        
        
@csrf_exempt
def profile_posts(request, username, page):
    user = User.objects.get(username = username)
    if request.method == "POST":
        return JsonResponse({"following":user.following.all().count(), "followers":user.followers.all().count()}, status=201)
    else:
        posts = user.posts.all()
        posts = posts.order_by("-timestamp").all()
        paginator = Paginator(posts, 10)
        page_obj = paginator.get_page(page)
        likedPosts = user.liked.all()
        return JsonResponse([[post.serialize() for post in page_obj.object_list], [post.id for post in likedPosts]], safe=False)
@csrf_exempt
def profile(request, username):
    if request.method == "POST":
        data = json.loads(request.body)
        user = User.objects.get(username = data.get("user"))
        account = User.objects.get(username = username)
        if(data.get("follow") == True):
            user.following.add(account)
            return JsonResponse({"message": "followed!"}, status=201)
        else:
            if(account in user.following.all()):
                user.following.remove(account)
                return JsonResponse({"message": "unfollowed!"}, status=201)
        return JsonResponse({"message": "did not"}, status=201)
    else:
        user = User.objects.get(username = username)
        posts = user.posts.all() 
        posts = posts.order_by("-timestamp").all()
        paginator = Paginator(posts, 10)
        page_number = request.GET.get('page')
        page_obj = paginator.get_page(page_number)
        return render(request, "network/profile.html", {
            "name": username,
            "page_obj": page_obj,
            "last_current": page_obj.paginator.num_pages - page_obj.number,
            "preprevious":page_obj.number - 2
        })
@csrf_exempt
def following(request, username):
    user = User.objects.get(username = username)
    following = user.following.all()
    posts = Post.objects.filter(user__in=following)
    posts = posts.order_by("-timestamp").all()
    paginator = Paginator(posts, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    if(request.method == "POST"):
        likedPosts = user.liked.all()
        return JsonResponse([[post.serialize() for post in page_obj.object_list], [post.id for post in likedPosts]], safe=False)
    else:
        return render(request, "network/following.html", {
            "page_obj": page_obj,
            "last_current": page_obj.paginator.num_pages - page_obj.number,
            "preprevious":page_obj.number - 2
        })

@csrf_exempt  
def liked(request):
    data = json.loads(request.body)
    user = User.objects.get(username = data.get("user"))
    post = Post.objects.get(id = data.get("post_id"))
    if user in post.likes.all():
        return JsonResponse({"liked": "True"})
    else:
        return JsonResponse({"liked": "False"})

