from django.db import models


class Contacts(models.Model):
    name = models.CharField(max_length=100)


class Messages(models.Model):
    message = models.TextField()
    date_time = models.DateTimeField()
