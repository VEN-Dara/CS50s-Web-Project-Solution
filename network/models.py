from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    followers = models.ManyToManyField("self", blank=True, related_name="followings")
    
    def serialize(self):
        return {
            "id": self.id,
            "username" : self.username,
            "email": self.email
        }

class Post(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="post")
    body = models.CharField(max_length=2000)
    date = models.DateTimeField(auto_now_add=True)
    reactions = models.ManyToManyField(User, blank=True, related_name="post_reacted")

    def serialize_reactions(self):
        return [user.serialize() for user in self.reactions.all()]

    def serialize(self):
        return {
            "id": self.id,
            "user": self.user.username,
            "body": self.body,
            "date": self.date.strftime("%b %d %Y, %I:%M %p"),
            "reactions": self.serialize_reactions()
        }
