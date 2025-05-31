from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
import json
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth import login, logout
from .models import Contacts, Messages


def Home(request):
    if request.user.is_authenticated:
        user = request.user
        contacts = Contacts.objects.filter(user=user)
        if contacts.exists():
            return render(request, 'home.html', {'contacts': contacts})
    return render(request, 'home.html')


def register(request):
    form = UserCreationForm()
    if request.method == "POST":
        form = UserCreationForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect("user_login")

    return render(request, "register.html", {"form": form})


def login_view(request):
    # if the user is already logged in then redirect to the store page
    if request.user.is_authenticated:
        return redirect("home")

    if request.method == "POST":
        form = AuthenticationForm(data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            return redirect("home")

    form = AuthenticationForm()
    return render(request, "login.html", {"form": form})


def logout_view(request):
    logout(request)
    return redirect("home")


@login_required
def search_contacts(request):
    query = request.GET.get('q', '')
    user = request.user
    contacts = Contacts.objects.filter(user=user, name__icontains=query)
    data = [{'name': c.name} for c in contacts]
    return JsonResponse(data, safe=False)


@login_required
def get_messages(request):
    contact_name = request.GET.get('contact')
    last_id = request.GET.get('last_id')  # <-- NEW

    try:
        contact_entry = Contacts.objects.get(user=request.user, name=contact_name)
        contact_user = contact_entry.contact

        queryset = Messages.objects.filter(
            sender__in=[request.user, contact_user],
            receiver__in=[request.user, contact_user]
        )

        if last_id:
            queryset = queryset.filter(id__gt=last_id)  # <-- ONLY FETCH NEW MESSAGES

        messages = queryset.order_by('date_time')

        result = [{
            'id': msg.id,  # <-- INCLUDE ID TO TRACK
            'sender': msg.sender.username,
            'receiver': msg.receiver.username,
            'message': msg.message,
            'date_time': msg.date_time.strftime('%Y-%m-%d %H:%M'),
            'is_current_user': msg.sender == request.user
        } for msg in messages]

        return JsonResponse(result, safe=False)
    except Contacts.DoesNotExist:
        return JsonResponse([], safe=False)


@login_required
def send_message(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        contact_name = data.get('contact')
        message = data.get('message')

        try:
            contact_entry = Contacts.objects.get(user=request.user, name=contact_name)
            receiver = contact_entry.contact
            sender = request.user

            msg_obj = Messages.objects.create(sender=sender, receiver=receiver, message=message)
            return JsonResponse({'success': True, 'message_id': msg_obj.id})
        except Contacts.DoesNotExist:
            return JsonResponse({'success': False, 'error': 'Contact not found'})
    return JsonResponse({'success': False, 'error': 'Invalid request method'})
