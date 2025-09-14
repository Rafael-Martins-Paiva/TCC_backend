from django.contrib import admin

from .models import Restaurant


class RestaurantAdmin(admin.ModelAdmin):
    list_display = ("name", "owner", "id")
    search_fields = ("name", "owner__email")
    list_filter = ("owner",)


admin.site.register(Restaurant, RestaurantAdmin)
