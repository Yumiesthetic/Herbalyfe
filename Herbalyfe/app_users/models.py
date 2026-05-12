from django.db import models
from django.contrib.auth.models import User
import os

def avatar_upload_path(instance, filename):
    ext = os.path.splitext(filename)[1].lower()  # Extract file extension
    username = instance.user.username.replace(" ", "_").lower()  # sanitize username
    filename = f"user_{username}_avatar{ext}"  # e.g., user_1_john_avatar.jpg
    return os.path.join("avatars", filename)

class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    avatar = models.ImageField(
        upload_to=avatar_upload_path,
        null=True,
        blank=True,
        default='default-avatar.png'
    )

    def save(self, *args, **kwargs):
        # Handle username-based avatar renaming
        try:
            old_user = User.objects.get(pk=self.user.pk)
            old_username = old_user.username
            new_username = self.user.username

            if old_username != new_username and self.avatar:
                old_path = self.avatar.path
                _, ext = os.path.splitext(old_path)
                new_filename = f"user_{new_username}_avatar{ext}"
                new_path = os.path.join(os.path.dirname(old_path), new_filename)

                if os.path.exists(old_path):
                    os.rename(old_path, new_path)
                    self.avatar.name = f"avatars/{new_filename}"
        except User.DoesNotExist:
            pass

        # Handle old avatar deletion on update
        try:
            old_avatar = Profile.objects.get(pk=self.pk).avatar
            new_avatar = self.avatar
            if old_avatar and old_avatar != new_avatar:
                if os.path.isfile(old_avatar.path) and "default-avatar.png" not in old_avatar.path:
                    os.remove(old_avatar.path)
        except (Profile.DoesNotExist, ValueError):
            pass

        super().save(*args, **kwargs)

    def __str__(self):
        return self.user.username
