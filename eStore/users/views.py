from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .forms import RegisterForm
from store.models import Store, Product
from store.forms import StoreForm, ProductForm


def register(request):
    """Handle user registration for both customers and vendors.

    Args:
        request (HttpRequest): The HTTP request object containing POST data
            with registration form data or GET for empty form.

    Returns:
        HttpResponse: Renders registration form or redirects to user_home on
            successful registration.

    The function handles both GET and POST requests:
    - GET: Displays empty registration form
    - POST: Processes form data, creates new user, and sets up account type
    """
    if request.method == "POST":
        form = RegisterForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            account_type = form.cleaned_data["account_type"]
            if account_type == "vendor":
                messages.success(
                    request, "Registration successful! Welcome, Vendor."
                )
            else:
                messages.success(
                    request, "Registration successful! Welcome to eStore."
                )
            return redirect("user_home")
    else:
        form = RegisterForm()
    return render(request, "users/register.html", {"form": form})


def login_view(request):
    """Handle user authentication and login.

    Args:
        request (HttpRequest): The HTTP request object containing POST data
            with login credentials or GET for login form.

    Returns:
        HttpResponse: Redirects to user_home for authenticated users, renders
            login form, or shows error message for invalid credentials.

    The function manages user authentication:
    - Redirects if user is already logged in
    - Authenticates credentials on POST
    - Handles next parameter for redirect after login
    """
    if request.user.is_authenticated:
        return redirect("user_home")

    if request.method == "POST":
        username = request.POST.get("username")
        password = request.POST.get("password")
        user = authenticate(request, username=username, password=password)
        if user:
            login(request, user)
            return redirect(request.GET.get("next") or "user_home")
        else:
            messages.error(request, "Invalid credentials")
    return render(request, "users/login.html")


@login_required
def logout_view(request):
    """Handle user logout.

    Args:
        request (HttpRequest): The HTTP request object.

    Returns:
        HttpResponse: Redirects to home page with logout message.
    """
    logout(request)
    messages.info(request, "You have been logged out successfully.")
    return redirect("home")


@login_required
def user_home(request):
    """Display user's dashboard with relevant information.

    Args:
        request (HttpRequest): The HTTP request object.

    Returns:
        HttpResponse: Renders dashboard template with user profile data and,
            for vendors, their stores and recent products.

    The dashboard shows different content based on user type:
    - All users see their profile information
    - Vendors see their stores and recent products
    """
    profile = request.user.profile

    # Get vendor data if user is a seller
    stores = None
    products = None
    if profile.is_seller:
        stores = Store.objects.filter(owner=request.user)
        if stores.exists():
            # Get all products from user's stores
            products = Product.objects.filter(
                store__owner=request.user
            ).order_by("-created_at")[:10]

    context = {
        "profile": profile,
        "stores": stores,
        "products": products,
    }
    return render(request, "users/dashboard.html", context)


# Vendor Dashboard Views
@login_required
def vendor_dashboard(request):
    """Display the main vendor dashboard with store and product statistics.

    Args:
        request (HttpRequest): The HTTP request object.

    Returns:
        HttpResponse: Renders vendor dashboard template with store list and
            product statistics, or redirects non-vendors to user_home.

    Shows:
    - List of vendor's stores
    - Total number of products
    - Count of active products
    """
    if not request.user.profile.is_seller:
        messages.error(request, "You need to be a vendor to access this page.")
        return redirect("user_home")

    stores = Store.objects.filter(owner=request.user)
    total_products = Product.objects.filter(store__owner=request.user).count()
    active_products = Product.objects.filter(
        store__owner=request.user, active=True
    ).count()

    context = {
        "stores": stores,
        "total_products": total_products,
        "active_products": active_products,
    }
    return render(request, "users/vendor_dashboard.html", context)


@login_required
def create_store(request):
    """Handle creation of a new vendor store."""
    if not request.user.profile.is_seller:
        messages.error(request, "You need to be a vendor to create a store.")
        return redirect("user_home")

    if request.method == "POST":
        form = StoreForm(
            request.POST, request.FILES
        )  # Added request.FILES for logo
        if form.is_valid():
            store = form.save(commit=False)
            store.owner = request.user
            store.save()

            # Tweet about the new store
            try:
                from store.twitter_utils import tweet_new_store

                print(
                    "🐦 Attempting to tweet about new store: %s" % store.name
                )
                success = tweet_new_store(store)
                if success:
                    print("✅ Tweet sent successfully!")
                else:
                    print("❌ Tweet failed (but store was created)")
            except Exception as e:
                print(f"❌ Error tweeting: {e}")

            messages.success(
                request, f"Store '{store.name}' created successfully!"
            )
            return redirect("vendor_dashboard")
    else:
        form = StoreForm()

    return render(
        request, "users/store_form.html", {"form": form, "action": "Create"}
    )


@login_required
def edit_store(request, slug):
    """Handle editing of an existing store.

    Args:
        request (HttpRequest): The HTTP request object containing POST data
            with updated store information or GET for pre-filled form.
        slug (str): URL slug of the store to edit.

    Returns:
        HttpResponse: Renders store edit form or redirects to vendor
            dashboard on successful update.

    Validates store ownership and processes update form.
    """
    if not request.user.profile.is_seller:
        messages.error(request, "You need to be a vendor to access this page.")
        return redirect("user_home")

    store = get_object_or_404(Store, slug=slug, owner=request.user)

    if request.method == "POST":
        form = StoreForm(request.POST, instance=store)
        if form.is_valid():
            form.save()
            messages.success(
                request, f"Store '{store.name}' updated successfully!"
            )
            return redirect("vendor_dashboard")
    else:
        form = StoreForm(instance=store)

    return render(
        request,
        "users/store_form.html",
        {"form": form, "action": "Edit", "store": store},
    )


@login_required
def delete_store(request, slug):
    """Handle deletion of an existing store.

    Args:
        request (HttpRequest): The HTTP request object with POST confirmation
            or GET for confirmation page.
        slug (str): URL slug of the store to delete.

    Returns:
        HttpResponse: Renders deletion confirmation page or redirects to vendor
            dashboard after successful deletion.

    Validates store ownership and handles deletion confirmation.
    """
    if not request.user.profile.is_seller:
        messages.error(request, "You need to be a vendor to access this page.")
        return redirect("user_home")

    store = get_object_or_404(Store, slug=slug, owner=request.user)

    if request.method == "POST":
        store_name = store.name
        store.delete()
        messages.success(
            request, f"Store '{store_name}' deleted successfully!"
        )
        return redirect("vendor_dashboard")

    return render(request, "users/store_confirm_delete.html", {"store": store})


@login_required
def manage_products(request, store_slug):
    """Display and manage products for a specific store.

    Args:
        request (HttpRequest): The HTTP request object.
        store_slug (str): URL slug of the store whose products to manage.

    Returns:
        HttpResponse: Renders product management page with list of store's
            products ordered by creation date.

    Validates store ownership and displays product management interface.
    """
    if not request.user.profile.is_seller:
        messages.error(request, "You need to be a vendor to access this page.")
        return redirect("user_home")

    store = get_object_or_404(Store, slug=store_slug, owner=request.user)
    products = store.products.all().order_by("-created_at")

    return render(
        request,
        "users/manage_products.html",
        {"store": store, "products": products},
    )


@login_required
def create_product(request, store_slug):
    """Handle creation of a new product in a store."""
    if not request.user.profile.is_seller:
        messages.error(request, "You need to be a vendor to access this page.")
        return redirect("user_home")

    store = get_object_or_404(Store, slug=store_slug, owner=request.user)

    if request.method == "POST":
        form = ProductForm(request.POST, request.FILES)
        if form.is_valid():
            product = form.save(commit=False)
            product.store = store
            product.save()

            # Tweet about the new product
            try:
                from store.twitter_utils import tweet_new_product

                print(
                    "🐦 Attempting to tweet about new product: %s"
                    % product.name
                )
                success = tweet_new_product(product)
                if success:
                    print("✅ Tweet sent successfully!")
                else:
                    print("❌ Tweet failed (but product was created)")
            except Exception as e:
                print("❌ Error tweeting: %s" % e)

            messages.success(
                request, f"Product '{product.name}' created successfully!"
            )
            return redirect("manage_products", store_slug=store.slug)
    else:
        form = ProductForm()

    return render(
        request,
        "users/product_form.html",
        {"form": form, "action": "Create", "store": store},
    )


@login_required
def edit_product(request, store_slug, product_slug):
    """Handle editing of an existing product.

    Args:
        request (HttpRequest): The HTTP request object containing POST data
            with updated product information or GET for pre-filled form.
        store_slug (str): URL slug of the store containing the product.
        product_slug (str): URL slug of the product to edit.

    Returns:
        HttpResponse: Renders product edit form or redirects to product
            management page on successful update.

    Validates store ownership and product existence, processes update form.
    """
    if not request.user.profile.is_seller:
        messages.error(request, "You need to be a vendor to access this page.")
        return redirect("user_home")

    store = get_object_or_404(Store, slug=store_slug, owner=request.user)
    product = get_object_or_404(Product, slug=product_slug, store=store)

    if request.method == "POST":
        form = ProductForm(request.POST, request.FILES, instance=product)
        if form.is_valid():
            form.save()
            messages.success(
                request, f"Product '{product.name}' updated successfully!"
            )
            return redirect("manage_products", store_slug=store.slug)
    else:
        form = ProductForm(instance=product)

    return render(
        request,
        "users/product_form.html",
        {"form": form, "action": "Edit", "store": store, "product": product},
    )


@login_required
def delete_product(request, store_slug, product_slug):
    """Handle deletion of an existing product.

    Args:
        request (HttpRequest): The HTTP request object with POST confirmation
            or GET for confirmation page.
        store_slug (str): URL slug of the store containing the product.
        product_slug (str): URL slug of the product to delete.

    Returns:
        HttpResponse: Renders deletion confirmation page or redirects to
            product management page after successful deletion.

    Validates store ownership and product existence, handles deletion
    confirmation.
    """
    if not request.user.profile.is_seller:
        messages.error(request, "You need to be a vendor to access this page.")
        return redirect("user_home")

    store = get_object_or_404(Store, slug=store_slug, owner=request.user)
    product = get_object_or_404(Product, slug=product_slug, store=store)

    if request.method == "POST":
        product_name = product.name
        product.delete()
        messages.success(
            request, f"Product '{product_name}' deleted successfully!"
        )
        return redirect("manage_products", store_slug=store.slug)

    return render(
        request,
        "users/product_confirm_delete.html",
        {"product": product, "store": store},
    )
