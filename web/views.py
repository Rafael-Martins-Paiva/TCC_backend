import json

from django.contrib import messages
from django.contrib.auth import authenticate, login
from django.contrib.auth.decorators import login_required
from django.http import Http404, HttpResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.template import TemplateDoesNotExist
from django.utils.decorators import method_decorator
from django.views.generic import TemplateView

from accounts.repositories import DjangoUserRepository
from domain.accounts.aggregates.value_objects.email import InvalidEmailError
from domain.accounts.exceptions.auth_exceptions import UserAlreadyExistsError
from domain.accounts.services.registration_service import RegistrationService
from restaurants.models import Restaurant, StockItem

from .forms import (
    AddStockItemForm,
    DecreaseStockItemForm,
    LoginForm,
    RegistrationForm,
    RestaurantCreateForm,
)


def wildcard_view(request, page_name="landing"):
    # Prevents directory traversal attacks
    if ".." in page_name:
        raise Http404("Invalid path")

    # Try to find a restaurant with this name
    try:
        restaurant = Restaurant.objects.get(name__iexact=page_name)
        if not restaurant.website_content:
            return HttpResponse(
                f"<h1>Welcome to {restaurant.name}'s page!</h1><p>No website content has been added yet.</p>",
                content_type="text/html",
            )
        return HttpResponse(restaurant.website_content, content_type="text/html")
    except Restaurant.DoesNotExist:
        pass  # No restaurant found, proceed to check for static templates

    template_path = f"web/features/{page_name}/{page_name}.html"
    context = {}

    if page_name == "landing":
        context = {
            "tabs": ["REAL-TIME ANALYTICS", "EASY PROJECTS", "EMAIL NOTIFICATION", "CLOUD SERVERS"],
            "images": json.dumps(
                [
                    "/static/web/img/google-icon.png",
                    "/static/web/img/facebook-icon.png",
                    "/static/web/img/google-icon.png",
                    "/static/web/img/facebook-icon.png",
                ]
            ),
        }

    try:
        return render(request, template_path, context)
    except TemplateDoesNotExist:
        raise Http404(f"Page not found: {template_path}")


def registration_view(request):
    if request.method == "POST":
        form = RegistrationForm(request.POST)
        if form.is_valid():
            data = form.cleaned_data
            user_repo = DjangoUserRepository()
            registration_service = RegistrationService(user_repository=user_repo)
            try:
                registration_service.register_user(
                    email=str(data["email"]), name=data.get("name", ""), password=data["password"]
                )
            except UserAlreadyExistsError as e:
                form.add_error("email", str(e))
            except InvalidEmailError as e:
                form.add_error("email", str(e))
            else:
                return redirect("web:login")
    else:
        form = RegistrationForm()
    return render(request, "web/features/registration/registration.html", {"form": form})


def login_view(request):
    if request.method == "POST":
        form = LoginForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data["email"]
            password = form.cleaned_data["password"]
            user = authenticate(request, username=email, password=password)
            if user is not None:
                login(request, user)
                messages.success(request, f"Welcome back, {user.email}!")
                next_url = request.GET.get("next")
                if next_url:
                    return redirect(next_url)
                return redirect("web:landing")
            else:
                messages.error(request, "Invalid login credentials.")
        else:
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, f"{field}: {error}")
    else:
        form = LoginForm()
    return render(request, "web/features/login/login.html", {"form": form})


def password_reset_view(request):
    return render(request, "web/features/password_reset/password_reset.html")


@login_required
def paid_plan_view(request):
    if request.method == "POST":
        user = request.user
        user.has_paid_plan = True
        user.save()
        messages.success(request, "Congratulations! You have successfully upgraded to a paid plan.")
        return redirect("web:landing")  # Redirect to a suitable page after upgrade
    return render(request, "web/features/paid_plan/paid_plan.html")


def restaurant_list_view(request):
    limit = int(request.GET.get("limit", 10))
    cursor = request.GET.get("cursor")
    direction = request.GET.get("direction", "next")

    restaurants_queryset = Restaurant.objects.order_by("name")

    if cursor:
        if direction == "next":
            restaurants_queryset = restaurants_queryset.filter(name__gt=cursor)
        elif direction == "prev":
            # For 'prev', we need to get items *before* the current cursor
            # and then reverse them to get the correct order for the previous page.
            restaurants_queryset = Restaurant.objects.filter(name__lt=cursor).order_by("-name")

    # Fetch one more item than the limit to determine if there's a next/previous page
    fetched_restaurants = list(restaurants_queryset[: limit + 1])

    restaurants = []
    has_next = False
    next_cursor = None
    has_previous = False
    previous_cursor = None

    if direction == "next":
        if len(fetched_restaurants) > limit:
            has_next = True
            next_cursor = fetched_restaurants[limit - 1].name
            restaurants = fetched_restaurants[:-1]
        else:
            restaurants = fetched_restaurants

        # If there's a cursor, it means we came from a previous page, so we can go back.
        if cursor:
            has_previous = True
            # The previous_cursor for the 'prev' button will be the name of the first item on the *current* page.
            previous_cursor = restaurants[0].name if restaurants else None

    elif direction == "prev":
        if len(fetched_restaurants) > limit:
            has_previous = True
            previous_cursor = fetched_restaurants[limit - 1].name
            restaurants = fetched_restaurants[:-1]
        else:
            restaurants = fetched_restaurants
        restaurants.reverse()  # Restore original order for display

        # If there's a cursor, it means we came from a next page, so we can go next.
        if cursor:
            has_next = True
            # The next_cursor for the 'next' button will be the name of the last item on the *current* page.
            next_cursor = restaurants[-1].name if restaurants else None

    # If no cursor, it's the first page.
    if not cursor:
        has_previous = False
        if len(fetched_restaurants) > limit:
            has_next = True
            next_cursor = fetched_restaurants[limit - 1].name
            restaurants = fetched_restaurants[:-1]
        else:
            restaurants = fetched_restaurants

    context = {
        "restaurants": restaurants,
        "has_next": has_next,
        "next_cursor": next_cursor,
        "has_previous": has_previous,
        "previous_cursor": previous_cursor,
        "current_limit": limit,
    }
    return render(request, "web/features/restaurant_list/restaurant_list.html", context)


@login_required
def restaurant_create_view(request):
    if request.method == "POST":
        form = RestaurantCreateForm(request.POST)
        if form.is_valid():
            if not request.user.has_paid_plan:
                messages.error(request, "You must have a paid plan to create a restaurant.")
            else:
                restaurant_name = form.cleaned_data["name"]
                website_content = form.cleaned_data.get("website_content", "")
                Restaurant.objects.create(name=restaurant_name, owner=request.user, website_content=website_content)
                messages.success(request, f"Restaurant '{restaurant_name}' created successfully!")
                return redirect("web:landing")  # Redirect to a suitable page after creation
        else:
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, f"{field}: {error}")
    else:
        form = RestaurantCreateForm()
    return render(request, "web/features/restaurant_create/restaurant_create.html", {"form": form})


@method_decorator(login_required, name="dispatch")
class ManageMenuView(TemplateView):
    template_name = "restaurants/manage_menu.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Ensure the restaurant exists and the user is the owner
        restaurant = get_object_or_404(Restaurant, pk=self.kwargs["restaurant_id"], owner=self.request.user)
        context["restaurant"] = restaurant
        return context


@method_decorator(login_required, name="dispatch")
class ManageInventoryView(TemplateView):
    template_name = "web/manage_inventory.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        restaurant = get_object_or_404(Restaurant, pk=self.kwargs["restaurant_id"], owner=self.request.user)
        context["restaurant"] = restaurant
        context["stock_items"] = StockItem.objects.filter(restaurant=restaurant)
        context["add_form"] = AddStockItemForm()
        context["decrease_form"] = DecreaseStockItemForm()
        return context

    def post(self, request, *args, **kwargs):
        restaurant = get_object_or_404(Restaurant, pk=self.kwargs["restaurant_id"], owner=self.request.user)

        # Check which form is being submitted by looking for a unique field
        if "name" in request.POST:
            form = AddStockItemForm(request.POST)
            if form.is_valid():
                name = form.cleaned_data["name"]
                quantity = form.cleaned_data["quantity"]
                # Use update_or_create to handle both new and existing items gracefully
                stock_item, created = StockItem.objects.update_or_create(
                    restaurant=restaurant, name__iexact=name, defaults={"name": name, "quantity": quantity}
                )
                if created:
                    messages.success(request, f"'{stock_item.name}' added to inventory.")
                else:
                    messages.info(request, f"'{stock_item.name}' quantity updated.")
                return redirect("web:manage_inventory", restaurant_id=restaurant.pk)

        elif "item_id" in request.POST:
            form = DecreaseStockItemForm(request.POST)
            if form.is_valid():
                item_id = form.cleaned_data["item_id"]
                amount = form.cleaned_data["amount"]
                try:
                    stock_item = StockItem.objects.get(id=item_id, restaurant=restaurant)
                    if stock_item.quantity >= amount:
                        stock_item.quantity -= amount
                        stock_item.save()
                        messages.success(request, f"Decreased '{stock_item.name}' quantity by {amount}.")
                    else:
                        messages.error(request, f"Cannot decrease quantity by {amount}, only {stock_item.quantity} left.")
                except StockItem.DoesNotExist:
                    messages.error(request, "Invalid item.")
                return redirect("web:manage_inventory", restaurant_id=restaurant.pk)

        # If form is invalid or something went wrong, re-render with errors
        # This part is tricky because we have two forms. We need to pass the failing form back.
        context = self.get_context_data(**kwargs)
        if "name" in request.POST:
            context["add_form"] = AddStockItemForm(request.POST)
        elif "item_id" in request.POST:
            # To show the error on the correct item, this would need more complex handling in the template.
            # For now, we just show a general error.
            messages.error(request, "Invalid data submitted for decreasing stock.")

        return self.render_to_response(context)
