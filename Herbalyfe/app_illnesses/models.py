from django.db import models
import os

# Function to determine the upload path for illness images
def illness_image_upload_to(instance, filename):
    return os.path.join('illness_images', filename)

# Create your models here.
class Illness(models.Model): # Model to represent an illness with its details
    id = models.AutoField(primary_key=True) # Unique identifier for each illness
    name = models.CharField(max_length=100)
    description = models.TextField()
    symptoms = models.TextField()
    # recommended_herbs = models.TextField()
    # Many-to-many relationship to link recommended herbs for the illness
    recommended_herbs = models.ManyToManyField('app_herbs.Herb', related_name='related_illnesses', blank=True) 
    image = models.ImageField(upload_to=illness_image_upload_to, default='default.jpg', blank=True)
    slug = models.SlugField(unique=True) # URL-friendly identifier for the illness

    def __str__(self):
        return self.name
