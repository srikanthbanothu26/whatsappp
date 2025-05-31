from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone


class Contacts(models.Model):
    name = models.CharField(max_length=100)
    user = models.ForeignKey(User, related_name='contacts', on_delete=models.CASCADE, null=True)
    contact = models.ForeignKey(User, related_name='contact_users', on_delete=models.CASCADE,
                                null=True)
    added_at = models.DateTimeField(default=timezone.now, null=True)


class Messages(models.Model):
    sender = models.ForeignKey(User, related_name='sent_messages', on_delete=models.CASCADE)
    receiver = models.ForeignKey(User, related_name='received_messages', on_delete=models.CASCADE)
    message = models.TextField()
    date_time = models.DateTimeField(default=timezone.now, null=True)

    def __str__(self):
        return f"{self.sender.username} to {self.receiver.username}: {self.message[:20]}"
