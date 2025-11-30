# pages/views.py

from django.shortcuts import render, redirect
from products.models import Product  # Import the Product model
from django.contrib.auth.decorators import login_required
from users.models import SearchHistory, LoyaltyProfile

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

    # ----- Clear all searches -----
    if 'clear' in request.GET:
        request.session['search_history'] = []
        return redirect('search')

    # ----- Delete specific search -----
    if 'delete' in request.GET:
        term_to_delete = request.GET.get('delete')
        search_history = [t for t in search_history if t != term_to_delete]
        request.session['search_history'] = search_history
        return redirect('search')

    # ----- Actual search -----
    query = request.GET.get('query', '').strip()

    # DEFAULT: no results
    results = []

    if query:
        # Track in session history (UI only)
        if query not in search_history:
            search_history.insert(0, query)
        search_history = search_history[:5]
        request.session['search_history'] = search_history

        # Award loyalty points for UNIQUE search
        # FIX: Use get_or_create to prevent DoesNotExist error
        loyalty, created = LoyaltyProfile.objects.get_or_create(user=request.user)

        already_searched = SearchHistory.objects.filter(
            user=request.user,
            query=query
        ).exists()

        if not already_searched:
            loyalty.points += 5
            loyalty.save()

        # Permanent history (DB)
        SearchHistory.objects.create(user=request.user, query=query)

        # ----- PRODUCT SEARCH -----
        results = Product.objects.filter(
            name__icontains=query
        ) | Product.objects.filter(
            category__icontains=query
        )

    return render(request, 'pages/search.html', {
        "query": query,
        "results": results,
        "search_history": search_history,
    })



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

@login_required
def loyalty_rewards(request):
    loyalty, created = LoyaltyProfile.objects.get_or_create(user=request.user)

    # Define tier thresholds
    tiers = [
        ("Bronze", 0),
        ("Silver", 300),
        ("Gold", 1500),
        ("Platinum", 3000),
    ]

    current_points = loyalty.points

    next_tier = None
    points_needed = 0

    for tier_name, threshold in tiers:
        if current_points < threshold:
            next_tier = tier_name
            points_needed = threshold - current_points
            break

    context = {
        "loyalty": loyalty,
        "next_tier": next_tier,
        "points_needed": points_needed,
    }

    return render(request, "pages/loyalty_rewards.html", context)


@login_required
def redeem_points(request):
    if request.method == "POST":
        reward_raw = request.POST.get("reward")
        if reward_raw:
            reward_name, cost = reward_raw.split("|")
            cost = int(cost)

            loyalty = LoyaltyProfile.objects.get(user=request.user)

            if loyalty.points >= cost:
                loyalty.points -= cost
                loyalty.save()

    return redirect('loyalty_rewards')