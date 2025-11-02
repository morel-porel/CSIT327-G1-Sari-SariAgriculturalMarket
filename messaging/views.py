# messaging/views.py
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.db.models import Count, Q
from .models import Conversation, Message, MessageReport 
from users.models import CustomUser
from notifications.utils import create_notification
from django.urls import reverse
from notifications.models import Notification
from django.http import JsonResponse, HttpResponseBadRequest 
from django.views.decorators.http import require_POST 

import datetime 

MESSENGER_TEMPLATE = 'messaging/messenger.html'

@login_required
def inbox_view(request):
    # ... (Your existing inbox_view logic) ...
    all_conversations = Conversation.objects.filter(participants=request.user).prefetch_related('participants', 'messages')
    
    conversations_with_recipient = []
    for convo in all_conversations:
        recipient = convo.participants.exclude(id=request.user.id).first()
        last_message = convo.messages.all().order_by('-timestamp').first() 
        unread_count = convo.messages.filter(Q(is_read=False) & ~Q(sender=request.user)).count()
        conversations_with_recipient.append((convo, recipient, last_message, unread_count))
    
    epoch = datetime.datetime(1970, 1, 1, tzinfo=datetime.timezone.utc)
    conversations_with_recipient.sort(key=lambda x: x[2].timestamp if x[2] else epoch, reverse=True)

    context = {
        'conversations_with_recipient': conversations_with_recipient,
        'other_participant': None,
    }
    return render(request, MESSENGER_TEMPLATE, context)

@login_required
def conversation_detail_view(request, conversation_id):
    conversation = get_object_or_404(Conversation, id=conversation_id)

    if request.user not in conversation.participants.all():
        return redirect('inbox')

    # --- Handle sending a new message (POST request) ---
    if request.method == 'POST':
        text_content = request.POST.get('text_content', '').strip()
        media_file = request.FILES.get('media_file')
        
        if text_content or media_file:
            
            # *** THIS IS THE FIX ***
            # We create the message object first, *then* save the file.
            # This is a more robust way to ensure the file is written to disk.
            new_message = Message.objects.create(
                conversation=conversation,
                sender=request.user,
                text_content=text_content
                # We add the media file in the next step
            )
            
            if media_file:
                new_message.media_file = media_file
                new_message.save() # This explicitly saves the file to the media directory
            # *** END OF FIX ***

            recipient = conversation.participants.exclude(id=request.user.id).first()
            if recipient:
                notification_text = f"New message from {request.user.username}"
                notification_link = reverse('conversation_detail', kwargs={'conversation_id': conversation.id})
                create_notification(
                    recipient=recipient,
                    message=notification_text,
                    link=notification_link
                )
        return redirect('conversation_detail', conversation_id=conversation.id)

    # --- GET Request Logic ---
    conversation_url = reverse('conversation_detail', kwargs={'conversation_id': conversation.id})
    Notification.objects.filter(
        recipient=request.user, 
        is_read=False, 
        link=conversation_url
    ).update(is_read=True)

    messages = conversation.messages.filter(is_moderator_deleted=False).order_by('timestamp')
    messages.filter(conversation=conversation).exclude(sender=request.user).update(is_read=True)
    other_participant = conversation.participants.exclude(id=request.user.id).first()

    all_conversations = Conversation.objects.filter(participants=request.user).prefetch_related('participants', 'messages')
    
    conversations_with_recipient = []
    for convo in all_conversations:
        recipient = convo.participants.exclude(id=request.user.id).first()
        last_message = convo.messages.all().order_by('-timestamp').first()
        unread_count = convo.messages.filter(Q(is_read=False) & ~Q(sender=request.user)).count()
        conversations_with_recipient.append((convo, recipient, last_message, unread_count))
    
    epoch = datetime.datetime(1970, 1, 1, tzinfo=datetime.timezone.utc)
    conversations_with_recipient.sort(key=lambda x: x[2].timestamp if x[2] else epoch, reverse=True)

    context = {
        'conversations_with_recipient': conversations_with_recipient,
        'conversation': conversation,
        'chat_messages': messages,
        'other_participant': other_participant
    }
    
    return render(request, MESSENGER_TEMPLATE, context)


# NEW VIEW: To handle the report message feature (AJAX endpoint)
@login_required
@require_POST
def report_message_view(request, message_id):
    message = get_object_or_404(Message, id=message_id)
    reporter = request.user
    reason = request.POST.get('reason', '').strip() 

    if reporter not in message.conversation.participants.all():
        return HttpResponseBadRequest("Cannot report a message in a conversation you are not part of.")

    if not reason:
        return HttpResponseBadRequest("A reason for the report is required.")
    
    if MessageReport.objects.filter(message=message, reporter=reporter).exists():
        return JsonResponse({'status': 'exists', 'message': 'You have already reported this message.'}, status=200)

    MessageReport.objects.create(
        message=message,
        reporter=reporter,
        reason=reason
    )
    
    return JsonResponse({'status': 'success', 'message': 'Message reported successfully. An admin will review it shortly.'})


@login_required
def start_conversation_view(request, recipient_id):
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