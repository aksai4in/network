from django.contrib.auth.models import AbstractUser
from django.db import models

class User(AbstractUser):
    following = models.ManyToManyField("User", blank=True, related_name = "followers")
    

class Post(models.Model):
    user = models.ForeignKey(User, on_delete = models.CASCADE, related_name = "posts")
    content = models.TextField(max_length = 2000)
    timestamp = models.DateTimeField(auto_now_add=True)
    likes = models.ManyToManyField(User, blank=True, related_name = 'liked')
    def serialize(self):
        return {
            "id":self.id,
            "username": self.user.username,
            "content": self.content,
            "timestamp": self.timestamp.strftime("%b %d %Y, %I:%M %p"),
            "likes": self.likes.all().count(),
        }
