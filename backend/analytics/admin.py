from django.contrib import admin

from analytics.models import Session, Event


@admin.register(Session)
class SessionAdmin(admin.ModelAdmin):
    list_display = admin.ModelAdmin.list_display + (
        "session_start",
        "session_end",
    )
    ordering = ("-session_end", "anonymous_user_id")
    search_fields = ("anonymous_user_id",)


@admin.register(Event)
class EventAdmin(admin.ModelAdmin):
    list_display = ("event_name", "anonymous_user_id", "timestamp")
    ordering = ("-timestamp",)
    search_fields = ("anonymous_user_id", "event_name")
