from django.db import models
from django.contrib.auth.models import User
from app_herbs.models import HerbPin


class PinReport(models.Model):

    STATUS_CHOICES = [
        ('PENDING', 'Pending'),
        ('APPROVED', 'Approved'),
        ('DENIED', 'Denied'),
    ]

    reported_pin = models.ForeignKey(
        HerbPin,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='reports'
    )

    original_pin_owner = models.CharField(
    max_length=150,
    blank=True
    )

    reported_by = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='submitted_reports'
    )

    reason = models.TextField(max_length=250)

    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='PENDING'
    )

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        if self.reported_pin:
            return f"Report #{self.id} on Pin {self.reported_pin.id}"

        return f"Report #{self.id} on Deleted Pin"