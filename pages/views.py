# pages/views.py

from django.shortcuts import render, redirect
from products.models import Product  # Import the Product model
from django.contrib.auth.decorators import login_required


def about_us_view(request):
    # This view's only job is to render the 'about.html' template.
    return render(request, 'pages/about.html')


def home_view(request):
    products = Product.objects.all().select_related('vendor__vendorprofile').order_by('-created_at')  # Get all products
    context = {
        'products': products
    }
    return render(request, 'pages/home.html', context)


@login_required
def become_vendor_view(request):
    """
    A page that informs consumers how to become a vendor
    before sending them to the vendor signup form.
    """
    return render(request, 'pages/become_vendor.html')


@login_required
def search_view(request):
    # Get search history from session
    search_history = request.session.get('search_history', [])

    # --- Handle clear all ---
    if 'clear' in request.GET:
        request.session['search_history'] = []
        return redirect('search')

    # --- Handle delete individual search ---
    if 'delete' in request.GET:
        term_to_delete = request.GET.get('delete')
        search_history = [item for item in search_history if item != term_to_delete]
        request.session['search_history'] = search_history
        return redirect('search')

    # --- Handle search query ---
    query = request.GET.get('query', '').strip()
    if query:
        if query not in search_history:
            search_history.insert(0, query)
        if len(search_history) > 5:
            search_history = search_history[:5]
        request.session['search_history'] = search_history

    context = {
        'query': query,
        'search_history': search_history,
    }
    return render(request, 'pages/search.html', context)


@login_required
def delete_search_history(request, history_id):
    """Deletes a single search entry by index."""
    search_history = request.session.get('search_history', [])
    if 0 <= history_id < len(search_history):
        del search_history[history_id]
        request.session['search_history'] = search_history
    return redirect('search')


@login_required
def clear_search_history(request):
    """Clears all saved searches."""
    request.session['search_history'] = []
    return redirect('search')