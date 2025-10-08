from django.contrib import admin

from .models import (
    InventoryItem,
    MenuItem,
    MenuItemMedia,
    Restaurant,
    Review,
    StockItem,
)


class RestaurantAdmin(admin.ModelAdmin):
    list_display = ("name", "owner", "id")
    search_fields = ("name", "owner__email")
    list_filter = ("owner",)


class MenuItemMediaInline(admin.TabularInline):
    model = MenuItemMedia
    extra = 1
    fields = ("file", "media_type")


class MenuItemAdmin(admin.ModelAdmin):
    list_display = ("name", "restaurant", "price", "is_available")
    list_filter = ("restaurant", "is_available")
    search_fields = ("name", "restaurant__name")
    inlines = [MenuItemMediaInline]
    fieldsets = (
        (None, {"fields": ("restaurant", "name", "description", "price")}),
        ("Availability", {"fields": ("is_available",)}),
        ("Details", {"fields": ("ingredients", "allergens")}),
        ("Media", {"fields": ("cover",)}),
    )


class ReviewAdmin(admin.ModelAdmin):
    list_display = ("author", "rating", "restaurant", "menu_item", "created_at")
    list_filter = ("rating", "restaurant", "author")
    search_fields = ("comment", "author__email", "restaurant__name", "menu_item__name")


class InventoryItemAdmin(admin.ModelAdmin):
    list_display = ("menu_item", "quantity", "last_updated")
    search_fields = ("menu_item__name",)


class StockItemAdmin(admin.ModelAdmin):
    list_display = ("name", "restaurant", "quantity", "last_updated")
    list_filter = ("restaurant",)
    search_fields = ("name", "restaurant__name")


admin.site.register(Restaurant, RestaurantAdmin)
admin.site.register(MenuItem, MenuItemAdmin)
admin.site.register(Review, ReviewAdmin)
admin.site.register(InventoryItem, InventoryItemAdmin)
admin.site.register(StockItem, StockItemAdmin)
admin.site.register(MenuItemMedia)