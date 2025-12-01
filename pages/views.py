from django.shortcuts import render, redirect, get_object_or_404
from products.models import Product
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST
from users.models import SearchHistory, LoyaltyProfile
from django.http import JsonResponse
import json

def about_us_view(request):
    return render(request, 'pages/about.html')

def home_view(request):
    products = Product.objects.all().select_related('vendor__vendorprofile').order_by('-created_at')
    context = {
        'products': products
    }
    return render(request, 'pages/home.html', context)

@login_required
def cart_view(request):
    return render(request, 'pages/cart.html')

@login_required
def become_vendor_view(request):
    return render(request, 'pages/become_vendor.html')

@login_required
def search_view(request):
    search_history = request.session.get('search_history', [])

    if 'clear' in request.GET:
        request.session['search_history'] = []
        SearchHistory.objects.filter(user=request.user).delete()
        return redirect('search')

    if 'delete' in request.GET:
        term_to_delete = request.GET.get('delete')
        search_history = [t for t in search_history if t != term_to_delete]
        request.session['search_history'] = search_history
        SearchHistory.objects.filter(user=request.user, query=term_to_delete).delete()
        return redirect('search')

    query = request.GET.get('q', '').strip()
    results = []

    if query:
        if query not in search_history:
            search_history.insert(0, query)
        search_history = search_history[:5]
        request.session['search_history'] = search_history

        loyalty, created = LoyaltyProfile.objects.get_or_create(user=request.user)
        
        already_searched = SearchHistory.objects.filter(
            user=request.user,
            query=query
        ).exists()

        if not already_searched:
            loyalty.points += 5
            loyalty.save()
            SearchHistory.objects.create(user=request.user, query=query)
        else:
            recent_entry = SearchHistory.objects.filter(user=request.user, query=query).first()
            if recent_entry:
                recent_entry.save()

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
    return redirect('search')

@login_required
def clear_search_history(request):
    request.session['search_history'] = []
    SearchHistory.objects.filter(user=request.user).delete()
    return redirect('search')

@login_required
def loyalty_rewards(request):
    loyalty, created = LoyaltyProfile.objects.get_or_create(user=request.user)
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

@login_required
def recent_searches_api(request):
    searches = SearchHistory.objects.filter(user=request.user).order_by('-searched_at').values_list('query', flat=True).distinct()[:8]
    data = list(searches)
    return JsonResponse({'searches': data})

@login_required
@require_POST
def delete_search_item_api(request):
    try:
        data = json.loads(request.body)
        term = data.get('term')
        if term:
            SearchHistory.objects.filter(user=request.user, query=term).delete()
            return JsonResponse({'status': 'success'})
        return JsonResponse({'status': 'error', 'message': 'No term provided'}, status=400)
    except Exception as e:
        return JsonResponse({'status': 'error', 'message': str(e)}, status=500)

@login_required
@require_POST
def clear_search_history_api(request):
    try:
        SearchHistory.objects.filter(user=request.user).delete()
        request.session['search_history'] = []
        return JsonResponse({'status': 'success'})
    except Exception as e:
        return JsonResponse({'status': 'error', 'message': str(e)}, status=500)