from django.urls import path
from django.contrib.auth import views as auth_views
from . import views

# Pre-configured password reset views to keep lines short
password_reset_view = auth_views.PasswordResetView.as_view(
    template_name="users/password_reset/password_reset_form.html",
    email_template_name="users/password_reset/password_reset_email.txt",
    subject_template_name="users/password_reset/password_reset_subject.txt",
)

password_reset_done_view = auth_views.PasswordResetDoneView.as_view(
    template_name="users/password_reset/password_reset_done.html"
)

password_reset_confirm_view = auth_views.PasswordResetConfirmView.as_view(
    template_name="users/password_reset/password_reset_confirm.html"
)

password_reset_complete_view = auth_views.PasswordResetCompleteView.as_view(
    template_name="users/password_reset/password_reset_complete.html"
)

urlpatterns = [
    # User authentication
    path("", views.user_home, name="user_home"),
    path("register/", views.register, name="register"),
    path("login/", views.login_view, name="login"),
    path("logout/", views.logout_view, name="logout"),
    # Password reset (15 minute expiry)
    path("password-reset/", password_reset_view, name="password_reset"),
    path(
        "password-reset/done/",
        password_reset_done_view,
        name="password_reset_done",
    ),
    path(
        "password-reset-confirm/<uidb64>/<token>/",
        password_reset_confirm_view,
        name="password_reset_confirm",
    ),
    path(
        "password-reset-complete/",
        password_reset_complete_view,
        name="password_reset_complete",
    ),
    # Vendor dashboard
    path("vendor/", views.vendor_dashboard, name="vendor_dashboard"),
    # Store management
    path("vendor/store/create/", views.create_store, name="create_store"),
    path(
        "vendor/store/<slug:slug>/edit/", views.edit_store, name="edit_store"
    ),
    path(
        "vendor/store/<slug:slug>/delete/",
        views.delete_store,
        name="delete_store",
    ),
    # Product management
    path(
        "vendor/store/<slug:store_slug>/products/",
        views.manage_products,
        name="manage_products",
    ),
    path(
        "vendor/store/<slug:store_slug>/products/create/",
        views.create_product,
        name="create_product",
    ),
    path(
        "vendor/store/<slug:store_slug>/products/<slug:product_slug>/edit/",
        views.edit_product,
        name="edit_product",
    ),
    path(
        "vendor/store/<slug:store_slug>/products/<slug:product_slug>/delete/",
        views.delete_product,
        name="delete_product",
    ),
]
