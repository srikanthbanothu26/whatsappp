from django.shortcuts import render
from .models import Contacts


def hello(request):
    contacts = Contacts.objects.all()
    return render(request, 'home.html', {'contacts': contacts})
