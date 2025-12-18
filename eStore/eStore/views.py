from django.shortcuts import render
from store.models import Store


def home(request):
    stores = Store.objects.all()[:8].prefetch_related(
        "products"
    )  # Get first 8 stores
    return render(request, "home.html", {"stores": stores})
