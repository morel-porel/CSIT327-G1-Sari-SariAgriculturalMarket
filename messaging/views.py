# messaging/views.py
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.db.models import Count, Q
# UPDATED: Import the new MessageReport model
from .models import Conversation, Message, MessageReport 
from users.models import CustomUser
from notifications.utils import create_notification
from django.urls import reverse
from notifications.models import Notification
# NEW IMPORTS for the report AJAX endpoint
from django.http import JsonResponse, HttpResponseBadRequest 
from django.views.decorators.http import require_POST 

import datetime 

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
        # NOTE: If you want to only show the last *undeleted* message in the inbox list, 
        # modify this line: .filter(is_moderator_deleted=False)
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
        return redirect('inbox')

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
                notification_link = reverse('conversation_detail', kwargs={'conversation_id': conversation.id})

                # Call your helper function
                create_notification(
                    recipient=recipient,
                    message=notification_text,
                    link=notification_link
                )
        # Redirect back to the same page to show the new message
        return redirect('conversation_detail', conversation_id=conversation.id)

    # --- GET Request Logic ---

    # Construct the URL path for the current conversation
    conversation_url = reverse('conversation_detail', kwargs={'conversation_id': conversation.id})

    Notification.objects.filter(
        recipient=request.user, 
        is_read=False, 
        link=conversation_url
    ).update(is_read=True)

    # 1. Get data for the Right Panel (Active Chat)
    # UPDATED: Filter out messages that have been deleted by a moderator
    messages = conversation.messages.filter(is_moderator_deleted=False).order_by('timestamp')
    
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
        'chat_messages': messages,
        'other_participant': other_participant
    }
    
    # Render the new messenger.html template
    return render(request, MESSENGER_TEMPLATE, context)


# NEW VIEW: To handle the report message feature (AJAX endpoint)
@login_required
@require_POST
def report_message_view(request, message_id):
    """
    Handles the AJAX request to report a message.
    """
    message = get_object_or_404(Message, id=message_id)
    reporter = request.user
    reason = request.POST.get('reason', '').strip() # The 'reason' is the report message

    # Security check: User must be a participant in the conversation
    if reporter not in message.conversation.participants.all():
        return HttpResponseBadRequest("Cannot report a message in a conversation you are not part of.")

    if not reason:
        return HttpResponseBadRequest("A reason for the report is required.")
    
    # Prevent duplicate reports from the same user on the same message
    if MessageReport.objects.filter(message=message, reporter=reporter).exists():
        return JsonResponse({'status': 'exists', 'message': 'You have already reported this message.'}, status=200)

    # Create the report
    MessageReport.objects.create(
        message=message,
        reporter=reporter,
        reason=reason
    )
    
    # Optional: Send a notification to staff/admin to alert them of the new report
    # The report will also appear in the Django Admin Moderation Dashboard (Message Reports)
    
    return JsonResponse({'status': 'success', 'message': 'Message reported successfully. An admin will review it shortly.'})


@login_required
def start_conversation_view(request, recipient_id):
    """
    Finds or creates a 1-on-1 conversation and redirects to it.
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