from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin

from .models import User


class UserAdmin(BaseUserAdmin):
    list_display = ("email", "name", "is_verified", "has_paid_plan", "is_staff", "is_superuser")
    search_fields = ("email", "name")
    list_filter = ("is_verified", "has_paid_plan", "is_superuser")
    ordering = ("email",)

    fieldsets = (
        (None, {"fields": ("email", "password")}),
        ("Personal info", {"fields": ("name", "bio")}),
        (
            "Permissions",
            {
                "fields": (
                    "is_active",
                    "is_staff",
                    "is_superuser",
                    "is_verified",
                    "has_paid_plan",
                    "groups",
                    "user_permissions",
                )
            },
        ),
        ("Important dates", {"fields": ("last_login", "date_joined")}),
    )
    add_fieldsets = (
        (
            None,
            {
                "classes": ("wide",),
                "fields": ("email", "password", "password2"),
            },  # password2 is not a model field, it's for form validation
        ),
    )


admin.site.register(User, UserAdmin)
