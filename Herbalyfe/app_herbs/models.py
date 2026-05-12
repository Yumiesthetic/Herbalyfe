from django.db import models
from django.contrib.auth.models import User
import os

# Function to determine the upload path for herb images
def herb_image_upload_to(instance, filename):
    return os.path.join('herb_images', filename)


class Herb(models.Model): # Model to represent an herb with its details
    id = models.AutoField(primary_key=True) # Unique identifier for each herb
    name = models.CharField(max_length=100)
    scientific_name = models.CharField(max_length=200, blank=True, null=True)
    description = models.TextField()
    medicinal_uses = models.TextField()
    side_effects = models.TextField(blank=True, null=True)
    image = models.ImageField(upload_to=herb_image_upload_to, default='default.jpg', blank=True)
    slug = models.SlugField(unique=True) # URL-friendly identifier for the herb

    def __str__(self):
        return self.name


class HerbPin(models.Model): # Model to represent a pinned herb location by a user
    herb = models.ForeignKey(Herb, on_delete=models.CASCADE, related_name='pins')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='herb_pins')
    latitude = models.FloatField()
    longitude = models.FloatField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.herb.name} pinned by {self.user.username}"

class Favorite(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='favorite_pins')
    pin = models.ForeignKey('HerbPin', on_delete=models.CASCADE, related_name='favorited_by')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'pin')

    def __str__(self):
        return f"{self.user.username} favorited {self.pin.herb.name}"
