from django.contrib import admin
from auctions.models import * 

#admin structure config
class WatchlistAdmin(admin.ModelAdmin):
    list_display = ['user', 'auctions_list']

    def auctions_list(self, obj):
        return ", ".join([str(auction) for auction in obj.auctions.all()])
    
    auctions_list.short_description = 'Auctions'

class UserAdmin(admin.ModelAdmin):
    list_display = ['id', 'username']

class CategoryAdmin(admin.ModelAdmin):
    list_display = ['id', 'name', 'description']

class AuctionAdmin(admin.ModelAdmin):
    list_display = ['id', 'name', 'price', 'listed_by', 'category', 'status', 'created_date', 'description', 'image_url' ]

class BidAdmin(admin.ModelAdmin):
    list_display = ['id', 'bidder', 'auction', 'amount', 'result']

class CommentAdmin(admin.ModelAdmin):
    list_display = ['id', 'username', 'content', 'date']

# Register your models here.
admin.site.register(User, UserAdmin)
admin.site.register(Category, CategoryAdmin)
admin.site.register(Auction, AuctionAdmin)
admin.site.register(Bid, BidAdmin)
admin.site.register(Comment, CommentAdmin)
admin.site.register(Watchlist, WatchlistAdmin)