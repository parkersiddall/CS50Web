from django.contrib.auth import authenticate, login, logout
from django.db import IntegrityError
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse
from django.core.paginator import Paginator
from django.contrib.auth.decorators import login_required
import operator
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
import json

from .models import User, Post, Likes, Follow


def index(request):

    # define variable for pagination
    list_posts = Post.objects.all().order_by('-date')
    paginator = Paginator(list_posts, 10) # Show 10 contacts per page.
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    if request.method == "GET":
        return render(request, "network/index.html", {
            "page_obj": page_obj
        })
    elif request.method == "POST":
        if "submit_post" in request.POST:

            # declare variables
            user = request.user
            content = request.POST['new-post']

            # check to be sure post is not blank
            if content == "":
                # return index page with error message
                return render(request, "network/index.html", {
                    "error_message": "Your post is incomplete.",
                    "page_obj": page_obj
                })

            # create and save new post
            post = Post(user=user, content=content)
            post.save()

            # return index page with message
            return render(request, "network/index.html", {
                "success_message": "Posted successfully!",
                "page_obj": page_obj
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

def profile(request, username):

    # get user account info
    profile_user = User.objects.get(username=username)

    # get user follower info
    followers = Follow.objects.filter(influencer=profile_user.id)
    following = Follow.objects.filter(follower=profile_user.id)

    # get user's posts
    posts = Post.objects.filter(user=profile_user.id).order_by('-date')

    paginator = Paginator(posts, 10) # Show 10 contacts per page.
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    if request.method == "GET":
        return render(request, "network/profile.html", {
        "followers": followers,
        "following": following,
        "profile_user": profile_user,
        "posts": posts,
        "page_obj": page_obj
        })

    elif request.method == "POST":
        # if request to unfollow by clicking the button that says "following"
        if "following" in request.POST:
            follow = Follow.objects.get(follower=request.user, influencer=profile_user)  # query DB to find this follow
            follow.delete()  # delete follow
            return render(request, "network/profile.html", {
            "followers": followers,
            "following": following,
            "profile_user": profile_user,
            "posts": posts,
            "page_obj": page_obj
            })
        # if request to follow
        if "follow" in request.POST:
            # query DB to see if a follow already exists
            exists = Follow.objects.filter(follower=request.user, influencer=profile_user)
            if len(exists) != 0:
                return render(request, "network/profile.html", {
                "followers": followers,
                "following": following,
                "profile_user": profile_user,
                "posts": posts,
                "page_obj": page_obj,
                "error_message": "An error occurred. You are already following this user."
                })
            else:
                # create and save follow
                follow = Follow(follower=request.user, influencer=profile_user)
                follow.save()
                return render(request, "network/profile.html", {
                    "followers": followers,
                    "following": following,
                    "profile_user": profile_user,
                    "posts": posts,
                    "page_obj": page_obj
                    })

@login_required(redirect_field_name='login')
def following(request):
    # collect queryset of people logged in user follows
    influencers = Follow.objects.filter(follower=request.user)

    # create a list to store posts from influencers
    influencer_posts = []

    # loop through influencers, get their posts, save them to the list declared above
    for item in influencers:
        posts = item.influencer.users_posts.all()
        for post in posts:
            influencer_posts.append(post)

    # reverse sort influencer_posts based on date
    influencer_posts_reverseorder = sorted(influencer_posts, key=operator.attrgetter('date'), reverse=True)

    # set up paginator
    paginator = Paginator(influencer_posts_reverseorder, 10) # Show 10 contacts per page.
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)



    if request.method == "GET":
        return render(request, "network/following.html", {
            "influencer_posts": influencer_posts,
            "influencer_posts_reverseorder": influencer_posts_reverseorder,
            "page_obj": page_obj
        })

@csrf_exempt
@login_required(redirect_field_name='login')
def edit(request):
    # editing must be via POST
    if request.method != "POST":
        return JsonResponse({"error": "POST request required."}, status=400)

    # get data from post
    data = json.loads(request.body)

    # extract data info into variables
    edited_content = data.get("edited_content", "")
    post_id = data.get("post_id", "")

    # get post from database, update, save
    i = Post.objects.get(id=post_id)
    i.content = edited_content
    i.save()

    return JsonResponse({"message": "Post updated"}, status=201)


@csrf_exempt
@login_required(redirect_field_name='login')
def unlike(request):
    # editing must be via POST
    if request.method != "POST":
        return JsonResponse({"error": "POST request required."}, status=400)

    # get data from post, extract id
    data = json.loads(request.body)
    post_id = data.get("post_id", "")

    # get like from database and delete it
    like = Likes.objects.get(user=request.user, post=post_id)
    like.delete()

    # get post, update its like count
    post = Post.objects.get(id=post_id)
    post.likes = post.likes - 1
    post.save()

    return JsonResponse({"message": "Post unliked."}, status=201)


@csrf_exempt
@login_required(redirect_field_name='login')
def like(request):
    # editing must be via POST
    if request.method != "POST":
        return JsonResponse({"error": "POST request required."}, status=400)

    # get data from post, extract id
    data = json.loads(request.body)
    post_id = data.get("post_id", "")

    # get post, update its like count
    post = Post.objects.get(id=post_id)
    post.likes = post.likes + 1
    post.save()

    # create like
    like = Likes(user=request.user, post=post)
    like.save()



    return JsonResponse({"message": "Post liked."}, status=201)
