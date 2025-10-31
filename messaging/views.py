# messaging/views.py
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.db.models import Count
from .models import Conversation, Message
from users.models import CustomUser #

@login_required
def inbox_view(request):
    """
    Display a list of all conversations for the current user.
    """
    conversations = Conversation.objects.filter(participants=request.user).prefetch_related('participants')
    
    # We'll create a new list to pass to the template
    # This list will contain (conversation, other_participant) tuples
    conversations_with_recipient = []
    
    for convo in conversations:
        # Find the other participant
        other_participant = convo.participants.exclude(id=request.user.id).first()
        conversations_with_recipient.append((convo, other_participant))

    context = {
        'conversations_with_recipient': conversations_with_recipient
    }
    return render(request, 'messaging/inbox.html', context)

@login_required
def conversation_detail_view(request, conversation_id):
    """
    Display a single conversation and its messages.
    Handles POST requests to send a new message.
    """
    conversation = get_object_or_404(Conversation, id=conversation_id)

    # Security check: Ensure the user is a participant
    if request.user not in conversation.participants.all():
        return redirect('inbox')

    # Handle sending a new message
    if request.method == 'POST':
        text_content = request.POST.get('text_content', '').strip() # .strip() removes whitespace
        media_file = request.FILES.get('media_file')
        
        # Check that the message is not empty
        if text_content or media_file:
            Message.objects.create(
                conversation=conversation,
                sender=request.user,
                text_content=text_content,
                media_file=media_file
            )
        
        # ALWAYS redirect after a POST to prevent re-submissions
        # This fixes the "it looks like it didn't send" issue
        return redirect('conversation_detail', conversation_id=conversation.id)

    # (GET request) Load all messages for this conversation
    messages = conversation.messages.all()
    # Mark messages as read (for Task 2.1.2)
    messages.filter(sender=request.user).update(is_read=True)

    context = {
        'conversation': conversation,
        'messages': messages,
        'other_participant': conversation.participants.exclude(id=request.user.id).first()
    }
    return render(request, 'messaging/conversation_detail.html', context)

@login_required
def start_conversation_view(request, recipient_id):
    """
    Finds or creates a 1-on-1 conversation with a recipient.
    """
    recipient = get_object_or_404(CustomUser, id=recipient_id)

    if recipient == request.user:
        # User can't message themselves
        return redirect('home') # Or wherever you prefer

    # Find an existing 1-on-1 conversation
    conversation = Conversation.objects.annotate(
        num_participants=Count('participants')
    ).filter(
        participants=request.user
    ).filter(
        participants=recipient
    ).filter(
        num_participants=2
    ).first()

    # If no 1-on-1 conversation exists, create one
    if not conversation:
        conversation = Conversation.objects.create()
        conversation.participants.add(request.user, recipient)

    # Redirect to the conversation detail page
    return redirect('conversation_detail', conversation_id=conversation.id)