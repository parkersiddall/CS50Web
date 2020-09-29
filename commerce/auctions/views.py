from django.contrib.auth import authenticate, login, logout
from django.db import IntegrityError
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse
from django.contrib.auth.decorators import login_required
from django import forms

from .models import User, Listing, Comment, Watchlist, Bid

categories = [
    ("Not Specified", "Not Specified"),
    ("Consumer Goods", "Consumer Goods"),
    ("Household Appliances", "Household Appliances"),
    ("Food and Beverage", "Food and Beverage"),
    ("Automobiles", "Automobiles"),
    ("Musical Instruments", "Musical Instruments"),
    ("Sporting Goods", "Sporting Goods"),
    ("Other", "Other")
]

# FORMS
# class for create listing form
class CreateForm(forms.Form):
    title = forms.CharField(label="Title", required=True, max_length=50)
    starting_bid = forms.FloatField(label="Starting bid", required=True)
    category = forms.CharField(label="Category", widget=forms.Select(choices=categories), required=False)  # find a way to make the default option null
    url = forms.URLField(label="Photo URL", required=False)
    description = forms.CharField(widget=forms.Textarea, required=True)
    creator = forms.HiddenInput()

# class for comment form
class CommentForm(forms.Form):
    comment = forms.CharField(widget=forms.Textarea, required=True)

# class for bid form
class BidForm(forms.Form):
    bid = forms.FloatField(label="Make a bid", required=True)


# VIEWS
def index(request):
    # create a list that containts all Listings
    listings = Listing.objects.all()
    # create list to populate with open listing
    active_listings = []
    # go through listings to check if it is open
    for listing in listings:
        if listing.status == "open":
            active_listings.append(listing)

    return render(request, "auctions/index.html", {
    "active_listings":active_listings
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
            return render(request, "auctions/login.html", {
                "message": "Invalid username and/or password."
            })
    else:
        return render(request, "auctions/login.html")


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
            return render(request, "auctions/register.html", {
                "message": "Passwords must match."
            })

        # Attempt to create new user
        try:
            user = User.objects.create_user(username, email, password)
            user.save()
        except IntegrityError:
            return render(request, "auctions/register.html", {
                "message": "Username already taken."
            })
        login(request, user)
        return HttpResponseRedirect(reverse("index"))
    else:
        return render(request, "auctions/register.html")


# view for create listing
@login_required
def create(request):
    if request.method == "GET":
        return render(request, "auctions/create.html", {
        "create_form":CreateForm()
        })

    # if request is POST
    else:
        # gather form data and be sure it is valid
        new_listing = CreateForm(request.POST)
        if new_listing.is_valid():

            #  pull out form data and put it into variables
            new_listing_title = new_listing.cleaned_data["title"]
            new_listing_description = new_listing.cleaned_data["description"]
            new_listing_starting_bid = new_listing.cleaned_data["starting_bid"]
            new_listing_category = new_listing.cleaned_data["category"]
            new_listing_creator = request.user.username
            # some logic to check for the photo URL
            if new_listing.cleaned_data["url"] == "":
                new_listing_url = "https://us.123rf.com/450wm/pavelstasevich/pavelstasevich1811/pavelstasevich181101032/112815935-stock-vector-no-image-available-icon-flat-vector-illustration.jpg?ver=6"
            else:
                new_listing_url = new_listing.cleaned_data["url"]

            # create a new listing for to be inserted into DB
            f = Listing(title=new_listing_title, description=new_listing_description, starting_bid=new_listing_starting_bid,
                    category=new_listing_category, url = new_listing_url, creator=new_listing_creator)

            # save to DB
            f.save()

            # gather active Listings
            # create a list that containts all Listings
            listings = Listing.objects.all()
            # create list to populate with open listing
            active_listings = []
            # go through listings to check if it is open
            for listing in listings:
                if listing.status == "open":
                    active_listings.append(listing)

            return render(request, "auctions/index.html", {
                "active_listings":active_listings
            })

        else:
            return render(request, "auctions/create.html", {
            "create_form":new_listing
        })

def listing(request, id):
    # GET
    if request.method == "GET":
        # get listing from database using the ID
        listing = Listing.objects.get(id=id)

        # get info from Watchlist
        watchlist = Watchlist.objects.filter(user=request.user.id, listing=id)

        if listing in watchlist:
            watchlist_message = "WATCHLIST"
        else:
            watchlist_message = "Add to watchlist"

        # return the listing page passing in the listing info
        return render(request, "auctions/listing.html", {
        "listing":listing,
        "comment_form":CommentForm(),  # returns comment form
        "comments": Comment.objects.filter(listing=listing),  # query results for a filtered search based on listing ID
        "watchlist_message": watchlist_message,
        "watchlist": watchlist,
        "bid_form": BidForm()
        })
    # POST
    else:
        #  COMMENT BOX (if posted from the comment section)
        if "submit_comment" in request.POST:
            # delcare variable for watchlist
            watchlist = Watchlist.objects.filter(user=request.user.id, listing=id)
            # pull listing id from DB
            listing = Listing.objects.get(id=id)
            # retrieve comment from post form
            comment = CommentForm(request.POST)
            # validate comment
            if comment.is_valid():
                # assign variables
                new_comment = comment.cleaned_data["comment"]
                new_comment_user = request.user.username
                new_comment_listing = listing

                # create a new comment to be loaded in DB
                f = Comment(comment=new_comment, user=new_comment_user, listing=new_comment_listing)
                f.save()  # save new comment to DB
                # return same page but with message
                return render(request, "auctions/listing.html", {
                    "listing":listing,
                    "comment_form":CommentForm(),  # returns comment form
                    "message": "Comment sent!",
                    "comments": Comment.objects.filter(listing=listing),
                    "watchlist": watchlist,  # query results for a filtered search based on listing ID
                    "bid_form": BidForm()
                })
        # POST from add to watchlist
        elif "add_watchlist" in request.POST:
            # delcare variable for watchlist
            watchlist = Watchlist.objects.filter(user=request.user.id, listing=id)

            # pull listing id from DB
            listing = Listing.objects.get(id=id)
            # create and save details to watchlist DB
            wl = Watchlist(user=request.user, listing=listing)
            wl.save()  # save to DB

            return render(request, "auctions/listing.html", {
                "listing":listing,
                "comment_form":CommentForm(),  # returns comment form
                "message": "Added to watchlist!",
                "comments": Comment.objects.filter(listing=listing),
                "watchlist": watchlist,  # query results for a filtered search based on listing ID
                "bid_form": BidForm()
            })
        # POST from remove from watchlist
        elif "remove_watchlist" in request.POST:
            # delcare variable for watchlist
            watchlist = Watchlist.objects.filter(user=request.user.id, listing=id)

            # pull listing id from DB
            listing = Listing.objects.get(id=id)
            # delete record for watchlist model
            Watchlist.objects.filter(user=request.user, listing=listing).delete()
            return render(request, "auctions/listing.html", {
                "listing":listing,
                "comment_form":CommentForm(),  # returns comment form
                "message": "Removed from watchlist!",
                "comments": Comment.objects.filter(listing=listing),  # query results for a filtered search based on listing ID
                "watchlist": watchlist,
                "bid_form": BidForm()
            })
        # POST end bid
        elif "end_bid" in request.POST:
            #get listing, update, and save
            listing = Listing.objects.get(id=id)
            listing.status = "closed"
            listing.save()

            # delcare variable for watchlist
            watchlist = Watchlist.objects.filter(user=request.user.id, listing=id)

            return render(request, "auctions/listing.html", {
                "listing":listing,
                "comment_form":CommentForm(),  # returns comment form
                "message": "You have ended the bid. It will no longer appear in the list of active listings. The winning bidder will be notified.",
                "comments": Comment.objects.filter(listing=listing),  # query results for a filtered search based on listing ID
                "watchlist": watchlist,
                "bid_form": BidForm()
            })

        # POST from bid
        elif "submit_bid" in request.POST:
            # delcare variable for watchlist
            watchlist = Watchlist.objects.filter(user=request.user.id, listing=id)
            # declare variable for listing
            listing = Listing.objects.get(id=id)
            # pull out data from form and validate it
            bid_form = BidForm(request.POST)
            if bid_form.is_valid():
                # declare variable for bid
                bid = bid_form.cleaned_data["bid"]
                # check to see that it is higher than starting bid
                if bid > listing.starting_bid:
                    # check to see if listing bid is at 0, meaning no new bids
                    if listing.bid == 0.0:
                        listing.bid = bid
                        # save bid value on listing
                        listing.save()
                        # save bid entry to big log
                        f = Bid(user=request.user, listing=listing, bid=listing.bid)
                        f.save()
                        # update winner in listing
                        listing.winner = request.user.username
                        listing.save()
                        return render(request, "auctions/listing.html", {
                            "listing":listing,
                            "comment_form":CommentForm(),  # returns comment form
                            "message": "You have successfully placed your bid!",
                            "comments": Comment.objects.filter(listing=listing),  # query results for a filtered search based on listing ID
                            "watchlist": watchlist,
                            "bid_form": BidForm()
                        })
                    # check to see that it be
                    elif listing.bid != 0.0:
                        if bid > listing.bid:
                            # save bid to listing
                            listing.bid = bid
                            listing.save()
                            # save bid entry to big log
                            f = Bid(user=request.user, listing=listing, bid=listing.bid)
                            f.save()
                            # update winner in listing
                            listing.winner = request.user.username
                            listing.save()

                            return render(request, "auctions/listing.html", {
                                "listing":listing,
                                "comment_form":CommentForm(),  # returns comment form
                                "message": "You have successfully placed your bid!",
                                "comments": Comment.objects.filter(listing=listing),  # query results for a filtered search based on listing ID
                                "watchlist": watchlist,
                                "bid_form": BidForm()
                            })
                        else:
                            #return error: bid not higher than highest bid
                            return render(request, "auctions/listing.html", {
                                "listing":listing,
                                "comment_form":CommentForm(),  # returns comment form
                                "message": "You have not placed a bid higher than the current highest bid.",
                                "comments": Comment.objects.filter(listing=listing),  # query results for a filtered search based on listing ID
                                "watchlist": watchlist,
                                "bid_form": BidForm()
                            })
                else:
                    # return error: bid not higher than starting bid
                    return render(request, "auctions/listing.html", {
                        "listing":listing,
                        "comment_form":CommentForm(),  # returns comment form
                        "message": "Your bid is not higher than the starting amount.",
                        "comments": Comment.objects.filter(listing=listing),  # query results for a filtered search based on listing ID
                        "watchlist": watchlist,
                        "bid_form": BidForm()
                    })


            else:
                # invalid input
                return render(request, "auctions/listing.html", {
                    "listing":listing,
                    "comment_form":CommentForm(),  # returns comment form
                    "message": "You have not placed a bid higher than the current highest bid.",
                    "comments": Comment.objects.filter(listing=listing),  # query results for a filtered search based on listing ID
                    "watchlist": watchlist,
                    "bid_form": BidForm()
                })




        else:  # I think this is the else for the comment form POST
            # declare variables
            watchlist = Watchlist.objects.filter(user=request.user.id, listing=id)
            listing = Listing.objects.get(id=id)

            return render(request, "auctions/listing.html", {
                "listing":listing,
                "comment_form":comment,  # returns comment form
                "message": "Comment load error.",
                "watchlist": watchlist,
                "listing": listing
            })

# class for the watchlist page
@login_required
def watchlist(request):
    # declare variables
    watchlist = Watchlist.objects.filter(user=request.user)  # watchlist for user
    # GET method
    if request.method == "GET":
        return render(request, "auctions/watchlist.html", {
            "watchlist": watchlist
        })

# class for the webpage with categories
def categories(request):
    categories = [
        ("Not Specified", "Not Specified"),
        ("Consumer Goods", "Consumer Goods"),
        ("Household Appliances", "Household Appliances"),
        ("Food and Beverage", "Food and Beverage"),
        ("Automobiles", "Automobiles"),
        ("Musical Instruments", "Musical Instruments"),
        ("Sporting Goods", "Sporting Goods"),
        ("Other", "Other")
    ]
    return render(request, "auctions/categories.html", {
    "categories": categories
    })

def category(request, category):
    listings = Listing.objects.filter(category=category, status="open")
    return render(request, "auctions/category.html", {
        "listings": listings,
        "category":category
    })
