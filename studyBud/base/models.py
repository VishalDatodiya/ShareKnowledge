from django.db import models
# from django.contrib.auth.models import User

from django.contrib.auth.models import AbstractUser

class User(AbstractUser):
    name = models.CharField(max_length=200, null=True)
    email = models.EmailField(unique=True, null=True)
    bio = models.TextField(null=True)
    
    avatar = models.ImageField(null=True, default="avatar.svg")
    
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []


class Topic(models.Model):
    name = models.CharField(max_length=200)
    
    
    def __str__(self):
        return self.name


class Room(models.Model):
    # SET_NULL means if we delete the topic then it will still in the room by unknown
    host = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    topic = models.ForeignKey(Topic, on_delete=models.SET_NULL, null=True)
    name = models.CharField(max_length=100)
    description = models.TextField(null=True, blank=True)  # blank means we can update or add anytime
    participants = models.ManyToManyField(User, related_name='participants', blank=True)
    # I used related name bcz we already use User in host field so they have conflict so i used related name for furtur reference.
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)
    
    # auto_add_now -> whenever we update it will noly show the first creation time only
    # auto_add -> Whenever we update the data it will show last modified time
    
    # order by
    # here we are ordering whole class
    class Meta:
        ordering = ['-updated', '-created']
    
    
    def __str__(self):
        return self.name



class Messages(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    room = models.ForeignKey(Room, on_delete=models.CASCADE)
    body = models.TextField()
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-updated', '-created']
    
    def __str__(self):
        return self.body[0:50]    # showing only 50 letter of message
    
    