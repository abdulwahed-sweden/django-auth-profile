from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.models import User

from .models import Profile

# --- Site branding ---
admin.site.site_header = "AuthProfile Admin"
admin.site.site_title = "AuthProfile"
admin.site.index_title = "Administration"


# --- Profile inline on User ---
class ProfileInline(admin.StackedInline):
    model = Profile
    can_delete = False
    verbose_name_plural = "Profile"
    fields = ["bio", "location", "phone", "avatar_url"]


# --- Extended User admin ---
class UserAdmin(BaseUserAdmin):
    inlines = [ProfileInline]
    list_display = ["username", "email", "first_name", "last_name", "is_active", "is_staff", "date_joined"]
    list_filter = ["is_active", "is_staff", "is_superuser", "date_joined"]
    search_fields = ["username", "email", "first_name", "last_name"]
    ordering = ["-date_joined"]


admin.site.unregister(User)
admin.site.register(User, UserAdmin)


# --- Profile admin ---
@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display = ["user", "location", "phone", "bio_short", "created_at", "updated_at"]
    list_filter = ["location", "created_at"]
    search_fields = ["user__username", "user__email", "location", "bio"]
    readonly_fields = ["created_at", "updated_at"]
    ordering = ["-created_at"]

    @admin.display(description="Bio")
    def bio_short(self, obj):
        if obj.bio and len(obj.bio) > 50:
            return obj.bio[:50] + "..."
        return obj.bio or "—"
