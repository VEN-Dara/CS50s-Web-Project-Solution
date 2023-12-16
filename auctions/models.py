from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils import timezone


class User(AbstractUser):
    pass

class Category(models.Model):
    name = models.CharField(max_length=64)
    description = models.CharField(max_length=1000, blank=True)

    def __str__(self):
        return f"{self.id} \t {self.name}"

class Auction(models.Model):
    name = models.CharField(max_length=64)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    image_url = models.CharField(max_length=2000)
    listed_by = models.ForeignKey(User, blank=True, on_delete=models.CASCADE, related_name="autions_listed")
    description = models.CharField(max_length=1000, blank=True)
    category = models.ForeignKey(Category, blank=True, on_delete=models.CASCADE, related_name="auctions")
    created_date = models.DateTimeField(default=timezone.now)
    status = models.CharField(max_length=32, default="active")

    def __str__(self):
        return f"{self.id} \t {self.name} \t {self.price} \t {self.listed_by}"
    
class Bid(models.Model):
    bidder = models.ForeignKey(User, on_delete=models.CASCADE, related_name = "bid_user")
    auction = models.ForeignKey(Auction, on_delete=models.CASCADE, related_name = "bid_auction")
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    result = models.CharField(max_length=20, default="waiting")

class Watchlist(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="user")
    auctions = models.ManyToManyField(Auction, blank=True, related_name="watchlist")

class Comment(models.Model):
    username = models.ForeignKey(User, on_delete=models.CASCADE, related_name="comment")
    auction = models.ForeignKey(Auction, on_delete=models.CASCADE, related_name="comment")
    content = models.CharField(max_length=2000)
    parent_comment = models.ForeignKey('self', null=True, blank=True, on_delete=models.CASCADE)
    sibling_comment = models.ForeignKey(User, null=True, blank=True, on_delete=models.CASCADE, related_name="replyer")
    date = models.DateTimeField(default=timezone.now)

