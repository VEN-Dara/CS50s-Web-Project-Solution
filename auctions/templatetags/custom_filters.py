from django import template
from auctions.models import Auction, Comment

register = template.Library()

@register.filter
def get_num_watchlist(request):
    num_watchlists = Auction.objects.filter(watchlist__user=request.user).count()
    return num_watchlists

@register.filter
def get_dict_value(dictionary, key):
    return dictionary.get(key, "")

@register.filter(name="get_child_comments")
def get_child_comments(comment_id):
    parent_comment = Comment.objects.get(pk=comment_id)
    child_comments = Comment.objects.filter(parent_comment=parent_comment)
    return child_comments