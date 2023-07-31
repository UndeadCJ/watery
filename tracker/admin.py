from django.contrib import admin

from tracker.models import User, Intake, History

admin.site.register(User)
admin.site.register(History)
admin.site.register(Intake)
