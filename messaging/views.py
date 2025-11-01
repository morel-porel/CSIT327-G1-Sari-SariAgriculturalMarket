# messaging/views.py
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.db.models import Count, Q
from .models import Conversation, Message
from users.models import CustomUser
from notifications.utils import create_notification

import datetime # <--- IMPORT IS ADDED HERE

# This is our new, single template file
MESSENGER_TEMPLATE = 'messaging/messenger.html'

@login_required
def inbox_view(request):
    """
    Display the main chat UI.
    Left panel: Populated with all conversations.
    Right panel: Empty (shows placeholder).
    """
    
    # Get all conversations for the left panel
    all_conversations = Conversation.objects.filter(participants=request.user).prefetch_related('participants', 'messages')
    
    conversations_with_recipient = []
    for convo in all_conversations:
        recipient = convo.participants.exclude(id=request.user.id).first()
        last_message = convo.messages.all().order_by('-timestamp').first()
        unread_count = convo.messages.filter(Q(is_read=False) & ~Q(sender=request.user)).count()
        
        conversations_with_recipient.append((convo, recipient, last_message, unread_count))
    
    # --- THIS IS THE FIX ---
    # Define a timezone-aware "epoch" (a very old date) for sorting
    epoch = datetime.datetime(1970, 1, 1, tzinfo=datetime.timezone.utc)
    # Sort by last message time, using the epoch for empty conversations
    conversations_with_recipient.sort(key=lambda x: x[2].timestamp if x[2] else epoch, reverse=True)
    # --- END OF FIX ---

    context = {
        # Data for the Left Panel
        'conversations_with_recipient': conversations_with_recipient,
        
        # 'other_participant' is None, so the template will show the placeholder
        'other_participant': None,
    }
    
    # Render the new messenger.html template
    return render(request, MESSENGER_TEMPLATE, context)

@login_required
def conversation_detail_view(request, conversation_id):
    """
    Display the main chat UI with an active conversation.
    Left panel: All conversations.
    Right panel: Active chat messages.
    """
    conversation = get_object_or_404(Conversation, id=conversation_id)

    # Security check
    if request.user not in conversation.participants.all():
        return redirect('inbox') # 'inbox' should be the name of your inbox_view URL

    # --- Handle sending a new message (POST request) ---
    if request.method == 'POST':
        text_content = request.POST.get('text_content', '').strip()
        media_file = request.FILES.get('media_file')
        
        if text_content or media_file:
            Message.objects.create(
                conversation=conversation,
                sender=request.user,
                text_content=text_content,
                media_file=media_file
            )
            recipient = conversation.participants.exclude(id=request.user.id).first()

            if recipient:
                notification_text = f"New message from {request.user.username}"
                notification_link = request.build_absolute_uri(
                    redirect('conversation_detail', conversation_id=conversation.id).url
                )

                # Call your helper function
                create_notification(
                    recipient=recipient,
                    message=notification_text,
                    link=notification_link
                )
        # Redirect back to the same page to show the new message
        return redirect('conversation_detail', conversation_id=conversation.id)

    # --- GET Request Logic ---

    # 1. Get data for the Right Panel (Active Chat)
    messages = conversation.messages.all().order_by('timestamp')
    # Mark messages from the *other* user as read
    messages.filter(conversation=conversation).exclude(sender=request.user).update(is_read=True)
    other_participant = conversation.participants.exclude(id=request.user.id).first()

    # 2. Get data for the Left Panel (All Conversations)
    all_conversations = Conversation.objects.filter(participants=request.user).prefetch_related('participants', 'messages')
    
    conversations_with_recipient = []
    for convo in all_conversations:
        recipient = convo.participants.exclude(id=request.user.id).first()
        last_message = convo.messages.all().order_by('-timestamp').first()
        unread_count = convo.messages.filter(Q(is_read=False) & ~Q(sender=request.user)).count()
        
        conversations_with_recipient.append((convo, recipient, last_message, unread_count))
    
    # --- THIS IS THE FIX ---
    # Define a timezone-aware "epoch" (a very old date) for sorting
    epoch = datetime.datetime(1970, 1, 1, tzinfo=datetime.timezone.utc)
    # Sort by last message time, using the epoch for empty conversations
    conversations_with_recipient.sort(key=lambda x: x[2].timestamp if x[2] else epoch, reverse=True)
    # --- END OF FIX ---


    context = {
        # Data for the Left Panel
        'conversations_with_recipient': conversations_with_recipient,
        
        # Data for the Right Panel
        'conversation': conversation,
        'chat_messages': messages,  # <--- RENAMED (This fixes the bug)
        'other_participant': other_participant
    }
    
    # Render the new messenger.html template
    return render(request, MESSENGER_TEMPLATE, context)

@login_required
def start_conversation_view(request, recipient_id):
    """
    Finds or creates a 1-on-1 conversation and redirects to it.
    (This view logic does not need to change)
    """
    recipient = get_object_or_404(CustomUser, id=recipient_id)

    if recipient == request.user:
        return redirect('home') 

    conversation = Conversation.objects.annotate(
        num_participants=Count('participants')
    ).filter(
        participants=request.user
    ).filter(
        participants=recipient
    ).filter(
        num_participants=2
    ).first()

    if not conversation:
        conversation = Conversation.objects.create()
        conversation.participants.add(request.user, recipient)

    return redirect('conversation_detail', conversation_id=conversation.id)