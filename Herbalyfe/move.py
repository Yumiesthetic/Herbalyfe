# This script has already been activated and is now useless, but kept for reference

import os
import django
from shutil import move


# Set up Django environment
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "Herbalyfe.settings")  # <-- replace with your project settings module
django.setup()

from django.conf import settings
from app_herbs.models import Herb
from app_illnesses.models import Illness


# Move images function
DEFAULT_NAMES = ("default.jpg", "default.jpeg", "default.png")

def move_images_for_model(model, subfolder_name):
    print("\nProcessing {} images...".format(model.__name__))
    moved, skipped = 0, 0

    target_dir = os.path.join(settings.MEDIA_ROOT, subfolder_name)
    os.makedirs(target_dir, exist_ok=True)

    for obj in model.objects.all():
        if not obj.image:
            skipped += 1
            continue

        image_name = os.path.basename(obj.image.name)
        if not image_name or image_name.lower() in DEFAULT_NAMES:
            skipped += 1
            continue

        old_path = os.path.join(settings.MEDIA_ROOT, obj.image.name)
        new_path = os.path.join(target_dir, image_name)

        if os.path.exists(old_path):
            try:
                move(old_path, new_path)
                obj.image.name = "{}/{}".format(subfolder_name, image_name)
                obj.save()
                moved += 1
                print("Moved: {}".format(image_name))
            except Exception as e:
                print("Error moving {}: {}".format(image_name, e))
                skipped += 1
        else:
            print("Not found: {}".format(old_path))
            skipped += 1

    print("Done for {}: {} moved, {} skipped.\n".format(model.__name__, moved, skipped))


if __name__ == "__main__":
    move_images_for_model(Herb, "herb_images")
    move_images_for_model(Illness, "illness_images")
    print("All done!")
