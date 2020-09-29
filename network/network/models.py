from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    pass

class Post(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="users_posts")
    date = models.DateTimeField(auto_now_add=True, blank=True)
    content = models.TextField(default="", max_length=500)
    likes = models.IntegerField(default=0) #  perhaps one to many foreign key...

    def __str__(self):
        return f"{self.user}, {self.date}: {self.content}"

class Likes(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="user_likes")
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name="post_likes")

    def __str__(self):
        return f"{self.user} likes {self.post}"

class Follow(models.Model):
    follower = models.ForeignKey(User, on_delete=models.CASCADE, related_name="user_follows")
    influencer = models.ForeignKey(User, on_delete=models.CASCADE, related_name="influencers")

    def __str__(self):
        return f"{self.follower.username} follows {self.influencer.username}"
