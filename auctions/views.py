from django.contrib.auth import authenticate, login, logout
from django.db import IntegrityError
from django.http import HttpResponseRedirect, Http404
from django.shortcuts import render
from django.urls import reverse
from django.db.models import Q, Max

from .models import User,Auction, Category, Bid, Watchlist, Comment


def index(request):
    auctions = Auction.objects.exclude(status='closed').order_by('-created_date')
    update_prices = {}
    for auction in auctions:
        update_prices[auction.id] = auction.price
        bid = auction.bid_auction.all()
        if bid:
            update_prices[auction.id] = bid.last().amount
    return render(request, "auctions/index.html", {
        "auctions" : auctions,
        "update_prices" : update_prices
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
    
def new(request):
    if request.method == "POST":
        name = request.POST['name']
        price = request.POST['price']
        image_url = request.POST['image_url']
        listed_by = request.user
        description = request.POST['description']
        category = Category.objects.get( pk=int(request.POST['category']) )
        auction = Auction(name=name, price=price, image_url=image_url, listed_by=listed_by, description=description, category=category)
        auction.save()
        return HttpResponseRedirect(reverse("index"))
    return render(request, "auctions/new.html", {
        "categories" : Category.objects.all()
    })

def listing(request, auction_id, message=""):
    if request.method == "POST":
        if request.user.is_authenticated:
            bidder = request.user
            auction = Auction.objects.get(pk=auction_id)
            amount = request.POST['amount']
            bid = Bid(bidder=bidder, auction=auction, amount=amount)
            bid.save()
            message = "Your bid is the current bid."
        else:
            return render(request, "auctions/login.html")

    auction = Auction.objects.get(pk=auction_id)

    if request.user.is_authenticated:
        try:
            Watchlist.objects.get(Q(user=request.user) & Q(auctions=auction))
            in_watchlist = 1
        except Watchlist.DoesNotExist:
            in_watchlist = 0
    else:
        in_watchlist = 0

    try:
        bid = Bid.objects.filter(auction=auction)
        bid_count = bid.count()
        if bid:
            last_bid_amount = bid.last().amount
        else:
            last_bid_amount = auction.price
    except Bid.DoesNotExist:
        last_bid_amount = auction.price
    
    comments = Comment.objects.filter(Q(auction=auction) & Q(parent_comment=None)).order_by('-date')

    return render(request, "auctions/listing.html", {
        "auction" : auction,
        "last_bid_amount" : last_bid_amount,
        "min_bid_amount" : last_bid_amount + 1,
        "bid_message" : message,
        "bid_count" : bid_count,
        "watchlist" : in_watchlist,
        "comments" : comments
    })

def watchlist(request, auction_id=0):
    if request.method == "POST":
        if request.user.is_authenticated:
            auction = Auction.objects.get(pk=auction_id)
            user = request.user
            try:
                watchlist = Watchlist.objects.get(user=user)
            except Watchlist.DoesNotExist:
                watchlist = Watchlist(user=user)
                watchlist.save()
            if "add_to_watchlist" in request.POST:
                watchlist.auctions.add(auction)
            elif "remove_from_watchlist" in request.POST:
                watchlist.auctions.remove(auction)
        return HttpResponseRedirect(reverse('listing',args=(auction_id,)))
    else:
        auction_in_watchlist = Auction.objects.filter(watchlist__user=request.user)
        return render(request, "auctions/watchlist.html", {
            "auction_in_watchlist" : auction_in_watchlist
        })

def close_bid(request, auction_id):
    auction = Auction.objects.get(pk=auction_id)
    if auction.listed_by == request.user:
        auction.status = "closed"
        auction.save()
        bid = Bid.objects.filter(auction=auction).aggregate(max_amount=Max('amount'))
        if bid:
            hightest_amount = bid['max_amount']
            bid_win = Bid.objects.filter(Q(auction=auction) & Q(amount=hightest_amount)).first()
            bid_win.result = "win"
            bid_win.save()
            Bid.objects.exclude(Q(auction=auction) & Q(amount=hightest_amount)).update(result="lose")
        return HttpResponseRedirect(reverse('index'))
    raise Http404("Page not found")
    
def bidded_listing(request):
    bids = Bid.objects.filter(bidder=request.user)
    auctions = Auction.objects.filter(bid_auction__bidder=request.user)
    return render(request, "auctions/bidded_listing.html", {
        "bids" : bids,
        "auctions" : auctions
    })

def comment(request, auction_id):
    if request.method == "POST":
        if request.user.is_authenticated:
            user = request.user
            auction = Auction.objects.get(pk=auction_id)
            content = request.POST['content']
            parent_comment_id = int(request.POST.get('parent_comment', 0))
            sibling_comment_id = int(request.POST.get('sibling_comment', 0))
            if parent_comment_id != 0 and sibling_comment_id != 0:
                    parent_comment = Comment.objects.get(pk=parent_comment_id)
                    sibling_comment = User.objects.get(pk=sibling_comment_id)
                    comment = Comment(username=user, auction=auction,content=content, parent_comment=parent_comment, sibling_comment=sibling_comment)
            else:
                comment = Comment(username=user, auction=auction,content=content)
            comment.save()
            return HttpResponseRedirect(reverse("listing", args=(auction_id,)))
        else:
            return render(request, "auctions/login.html")
            
def category(request, category_id=None):
    auctions = Auction.objects.exclude(status='closed').order_by('-created_date')
    if category_id:
        category = Category.objects.get(pk=category_id)
        auctions = Auction.objects.exclude(status='closed').order_by('-created_date').filter(category=category)
    
    update_prices = {}
    for auction in auctions:
        update_prices[auction.id] = auction.price
        bid = auction.bid_auction.all()
        if bid:
            update_prices[auction.id] = bid.last().amount
            print(update_prices[auction.id])
    categories = Category.objects.filter(auctions__isnull=False).distinct()
    return render(request, "auctions/category.html", {
        "auctions" : auctions,
        "update_prices" : update_prices,
        "categories" : categories
    })
                