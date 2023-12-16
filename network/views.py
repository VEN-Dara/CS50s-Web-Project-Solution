import json
import math
from django.contrib.auth import authenticate, login, logout
from django.db import IntegrityError
from django.http import HttpResponse, HttpResponseRedirect, JsonResponse
from django.shortcuts import render
from django.urls import reverse
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt
from django.core.paginator import Paginator

from .models import User, Post


def index(request):
    return render(request, "network/index.html")

@csrf_exempt
@login_required
def post(request):
    if request.method == "POST":
        post = json.loads(request.body)
        user = request.user
        body = post.get("body", "")
        post = Post(user=user, body=body)
        post.save()
        return JsonResponse({"message": "Post successfully."}, status=201)
    elif request.method == "PUT":
        data = json.loads(request.body)
        user = request.user
        id = data.get("id")
        post = Post.objects.get(pk=id)
        body = data.get("body", "")
        reaction = data.get("reaction", "")
        print(reaction)

        if body:
            post.body = body
        if reaction:
            if reaction == "love":
                post.reactions.add(user)
            elif reaction == "unlove":
                post.reactions.remove(user)
            print(post)
            return JsonResponse({ "post": post.serialize() }, safe=False)

        post.save()
        return JsonResponse({"message": "Edit post successfully."}, status=201)


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
def load_post(request, post_type):

    page_num = 1
    if request.method == "POST":
        page_num = json.loads(request.body).get("page_num", 1)

    if post_type == "new_feed":
        posts = Post.objects.order_by("-date").all()
        posts_length = Post.objects.order_by("-date").all().count()
    
    elif  post_type == "following":
        if request.user.is_authenticated:
            followings = User.objects.filter(followers=request.user)
            posts = Post.objects.order_by("-date").filter(user__in=followings)
            posts_length = Post.objects.order_by("-date").filter(user__in=followings).count()
        else:
            return render(request, "network/login.html")
    else:
        user = User.objects.filter(username=post_type).first()
        if user:
            posts = Post.objects.order_by("-date").filter(user=user)
            posts_length = Post.objects.order_by("-date").filter(user=user).count()
        else:
             return JsonResponse({"error": "Invalid user."}, status=400)
        
    page = Paginator(posts, 3)
    posts_paginator = page.page(page_num).object_list
    posts_length = math.ceil(posts_length/3)
            
    return JsonResponse({
        "posts" : [post.serialize() for post in posts_paginator],
        "posts_length": posts_length
        }, safe=False )

@csrf_exempt
def profile_info(request, username):
    try:
        user = User.objects.get(username=username)
    except User.DoesNotExist:
        return JsonResponse({"Error": "Invalid user."}, status=404)
    
    if request.method == "GET":
        followers = user.followers.all()
        followings = User.objects.filter(followers=user)

        return JsonResponse({
            "followers": [follower.serialize() for follower in followers],
            "followings": [following.serialize() for following in followings]
            }, safe=False)
    
    elif request.method == "PUT":
        data = json.loads(request.body)

        if data.get("isFollowing") is not None:
            isFollowing = data.get("isFollowing")

            if isFollowing:
                user.followers.add(request.user)
                user.save()

            else:
                user.followers.remove(request.user)
                user.save()
            return HttpResponse(status=204)
        
    else:
        return JsonResponse({
            "error": "GET or PUT request required."
        }, status=400)