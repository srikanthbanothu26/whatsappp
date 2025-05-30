from django.contrib import admin
from .models import Contacts


class ContactAdmin(admin.ModelAdmin):
    list_display = ('name',)


admin.site.register(Contacts, ContactAdmin)
