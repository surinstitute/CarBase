from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.models import Permission
from unfold.admin import ModelAdmin

from .forms import AdminPasswordChangeForm, UserChangeForm, UserCreationForm
from .models import User


def grant_default_catalog_permissions(user):
    permissions = Permission.objects.filter(content_type__app_label="catalog").exclude(
        content_type__model="group"
    )
    user.user_permissions.add(*permissions)


@admin.register(User)
class UserAdmin(BaseUserAdmin, ModelAdmin):
    form = UserChangeForm
    add_form = UserCreationForm
    change_password_form = AdminPasswordChangeForm

    date_hierarchy = "date_joined"
    list_display = (
        "email",
        "first_name",
        "date_joined",
        "is_staff",
        "is_superuser",
    )
    list_filter = (
        "is_active",
        "is_staff",
        "is_superuser",
        "date_joined",
        "groups",
        "catalog_groups",
    )
    fieldsets = (
        (None, {"fields": ("email", "first_name", "password")}),
        (
            "Permissions",
            {
                "fields": (
                    "is_active",
                    "is_staff",
                    "is_superuser",
                    "catalog_groups",
                    "groups",
                    "user_permissions",
                )
            },
        ),
        ("Important dates", {"fields": ("date_joined", "last_login")}),
    )
    readonly_fields = ("date_joined", "last_login")
    search_fields = ("email", "first_name")
    ordering = ("-date_joined",)
    filter_horizontal = ("catalog_groups", "groups", "user_permissions")

    add_fieldsets = (
        (
            None,
            {
                "classes": ("wide",),
                "fields": (
                    "email",
                    "first_name",
                    "last_name",
                    "is_active",
                    "is_staff",
                    "catalog_groups",
                    "password1",
                    "password2",
                ),
            },
        ),
    )

    def save_related(self, request, form, formsets, change):
        super().save_related(request, form, formsets, change)
        user = form.instance
        if not user.is_superuser and user.catalog_groups.exists():
            grant_default_catalog_permissions(user)
