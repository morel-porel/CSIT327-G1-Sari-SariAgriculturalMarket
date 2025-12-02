from django.shortcuts import render, redirect, get_object_or_404
from products.models import Product
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST
from users.models import SearchHistory, LoyaltyProfile, CustomUser
from django.http import JsonResponse
from django.urls import reverse
from django.db.models import Count
from messaging.models import Conversation, Message
from notifications.utils import create_notification
from datetime import datetime
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

    # Tier thresholds
    tiers = [
        ("Bronze", 0),
        ("Silver", 300),
        ("Gold", 1500),
        ("Platinum", 3000),
    ]

    current_points = loyalty.points
    current_tier = "Bronze"
    next_tier = None
    current_tier_points = 0
    next_tier_points = None

    # Determine current tier and next tier
    for tier_name, threshold in tiers:
        if current_points >= threshold:
            current_tier = tier_name
            current_tier_points = threshold
        else:
            next_tier = tier_name
            next_tier_points = threshold
            break

    # Calculate progress
    if next_tier:
        total_needed = next_tier_points - current_tier_points
        gained = current_points - current_tier_points
        progress_percentage = int((gained / total_needed) * 100)
        points_needed = next_tier_points - current_points
    else:
        # Highest tier reached
        progress_percentage = 100
        points_needed = 0

    context = {
        "loyalty": loyalty,
        "next_tier": next_tier,
        "points_needed": points_needed,
        "progress_percentage": progress_percentage,
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

                # APPLY REWARD EFFECT
                if reward_name == "5% Discount":
                    loyalty.has_5_discount = True

                elif reward_name == "Free Delivery":
                    loyalty.free_delivery = True

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
    
@login_required
@require_POST
def checkout_api(request):
    try:
        data = json.loads(request.body)
        grouped_orders = data.get('orders', [])
        
        if not grouped_orders:
            return JsonResponse({'status': 'error', 'message': 'Cart is empty or invalid.'}, status=400)

        # 1. Notify the Consumer (Buyer)
        total_items = sum(len(order['items']) for order in grouped_orders)
        create_notification(
            recipient=request.user,
            message=f"Order placed successfully! You checked out {total_items} item(s) from {len(grouped_orders)} vendor(s).",
            link="#"
        )

        # 2. Process Orders per Vendor (Messaging and Notification)
        for order in grouped_orders:
            vendor_id = order['vendor_id']
            vendor = get_object_or_404(CustomUser, pk=vendor_id)
            shop_name = order['shop_name']
            total_price = order['total_price']
            
            # --- A. Construct Receipt Message ---
            receipt_body = f"Thank you for your sale, {vendor.username}!\n"
            receipt_body += f"NEW ORDER from {request.user.username} (Consumer):\n\n"
            
            for item in order['items']:
                receipt_body += f"- {item['qty']}x {item['name']} @ ₱{item['price']}\n"
            
            receipt_body += f"\nTOTAL SALE: ₱{total_price:.2f}"
            receipt_body += f"\nOrder placed on: {datetime.now().strftime('%Y-%m-%d %H:%M')}"

            # --- B. Find or Create Conversation ---
            conversation = Conversation.objects.annotate(
                num_participants=Count('participants')
            ).filter(
                participants=request.user
            ).filter(
                participants=vendor
            ).filter(
                num_participants=2
            ).first()

            if not conversation:
                conversation = Conversation.objects.create()
                conversation.participants.add(request.user, vendor)
            
            # --- C. Send Receipt Message (as the Buyer) ---
            Message.objects.create(
                conversation=conversation,
                sender=request.user,
                text_content=receipt_body
            )

            # --- D. Notify the Vendor ---
            notification_text = f"NEW SALE! {request.user.username} checked out {len(order['items'])} item(s) from your shop {shop_name}."
            notification_link = reverse('conversation_detail', kwargs={'conversation_id': conversation.id})
            
            create_notification(
                recipient=vendor,
                message=notification_text,
                link=notification_link
            )

        return JsonResponse({'status': 'success', 'redirect_url': reverse('cart')})

    except json.JSONDecodeError:
        return JsonResponse({'status': 'error', 'message': 'Invalid JSON data.'}, status=400)
    except Exception as e:
        print(f"Checkout error: {e}")
        return JsonResponse({'status': 'error', 'message': 'Server processing error.'}, status=500)