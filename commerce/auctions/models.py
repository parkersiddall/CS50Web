from django.contrib.auth.models import AbstractUser
from django.db import models
from datetime import date

# for users
class User(AbstractUser):
    pass

# for listings
class Listing(models.Model):
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
    status_options = [
        ("open", "Open"),
        ("closed", "Closed")
    ]
    title = models.CharField(max_length=50, default="Listing")
    description = models.TextField(default="")
    starting_bid = models.DecimalField(default=0.0, decimal_places=2, max_digits=20)
    category = models.CharField(max_length=50, choices=categories, default="test", null=True, blank=True)
    url = models.URLField(null=True, blank=True, default="")
    created = models.DateField(auto_now_add=True)
    creator = models.CharField(max_length=50, default="user", null=True, blank=True)
    status = models.CharField(max_length=50, choices=status_options, default="open", null=True, blank=True)
    bid = models.DecimalField(default=0.0, decimal_places=2, max_digits=20)
    winner = models.CharField(max_length=50, default="user", null=True, blank=True)

    def __str__(self):
        return f"{self.title}"

# class for comments left by users
class Comment(models.Model):
    comment = models.TextField(default="", max_length=500)
    user = models.CharField(max_length=50, default="user", null=True, blank=True)
    listing = models.ForeignKey(Listing, on_delete=models.CASCADE, related_name="comments")
    posted = models.DateField(auto_now_add=True)

    def __str__(self):
        return f"{self.comment}"

# class for the watchlist
class Watchlist(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="users")
    listing = models.ForeignKey(Listing, on_delete=models.CASCADE, related_name="listings")
    added = models.DateField(auto_now_add=True)

    def __str__(self):
        return f"{self.user} added {self.listing} to watchlist on {self.added}"

# class for bids
class Bid(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="user_bids")
    listing = models.ForeignKey(Listing, on_delete=models.CASCADE, related_name="listing_bids")
    bid = models.DecimalField(default=0.0, decimal_places=2, max_digits=20)
    date = models.DateField(auto_now_add=True)

    def __str__(self):
        return f"{self.user} placed a bid of ${self.bid} on {self.listing}"
