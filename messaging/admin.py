# messaging/admin.py
from django.contrib import admin
from django.utils import timezone
from .models import Conversation, Message, MessageReport
from users.models import CustomUser 
from notifications.utils import create_moderation_warning # <-- NEW IMPORT

# Admin for Message model - to view all messages and the soft-delete status
@admin.register(Message)
class MessageAdmin(admin.ModelAdmin):
    list_display = ('id', 'sender', 'conversation', 'text_content', 'timestamp', 'is_moderator_deleted')
    list_filter = ('is_moderator_deleted', 'timestamp')
    search_fields = ('text_content', 'sender__username')

admin.site.register(Conversation)

# CORE: The Message Report Admin Dashboard and Actions (Task 1.7.3)
@admin.register(MessageReport)
class MessageReportAdmin(admin.ModelAdmin):
    # Task: Build admin moderation dashboard
    list_display = (
        'id', 'get_message_content', 'reporter', 'reported_at', 
        'is_resolved', 'moderation_action', 'moderator',
    )
    list_filter = ('is_resolved', 'moderation_action', 'reported_at')
    search_fields = ('reason', 'message__text_content', 'reporter__username')
    
    fields = ('message', 'reporter', 'reported_at', 'reason', 'is_resolved', 'moderation_action', 'resolution_notes', 'moderator', 'resolved_at')
    readonly_fields = ('message', 'reporter', 'reported_at', 'moderator', 'resolved_at')

    # Task: Implement moderation actions (warn, delete, ban)
    actions = ['mark_resolved_action', 'warn_user_action', 'delete_message_action', 'ban_user_action']
    
    @admin.display(description='Message Snippet')
    def get_message_content(self, obj):
        return obj.message.text_content[:50] + '...' if obj.message.text_content else '[Media File]'

    # Helper function to bulk resolve reports
    def _resolve_reports(self, queryset, action, request, notes):
        updated = queryset.filter(is_resolved=False).update(
            moderation_action=action,
            is_resolved=True,
            moderator=request.user,
            resolved_at=timezone.now(),
            resolution_notes=notes
        )
        return updated

    # --- ACTION 1: Warn User ---
    @admin.action(description='Warn reported user(s) and resolve report(s)')
    def warn_user_action(self, request, queryset):
        for report in queryset.filter(is_resolved=False):
            reported_user = report.message.sender
            
            # Send warning notification
            snippet = report.message.text_content[:20] + '...' if report.message.text_content else '[Media File]'
            create_moderation_warning(recipient=reported_user, message_content_snippet=snippet) 
            
            self._resolve_reports(
                queryset.filter(pk=report.pk), 
                'warn', 
                request, 
                f"User was warned and notified. Action taken by {request.user.username}."
            )

        self.message_user(request, f"Successfully warned user(s) and resolved {queryset.count()} report(s).")

    # --- ACTION 2: Delete Message ---
    @admin.action(description='Delete (hide) message(s) and resolve related report(s)')
    def delete_message_action(self, request, queryset):
        for report in queryset.filter(is_resolved=False):
            # Soft-delete the message by flagging it
            message_to_delete = report.message
            message_to_delete.is_moderator_deleted = True
            message_to_delete.save()
            
            self._resolve_reports(
                queryset.filter(pk=report.pk), 
                'delete', 
                request, 
                f"Message was marked as hidden/deleted. Action taken by {request.user.username}."
            )

        self.message_user(request, f"Successfully deleted/hidden message(s) and resolved {queryset.count()} report(s).")

    # --- ACTION 3: Ban User ---
    @admin.action(description='Ban reported user(s) and resolve report(s)')
    def ban_user_action(self, request, queryset):
        for report in queryset.filter(is_resolved=False):
            reported_user = report.message.sender
            
            # Ban the user: setting is_active=False prevents the user from logging in
            reported_user.is_active = False 
            reported_user.save()

            self._resolve_reports(
                queryset.filter(pk=report.pk), 
                'ban', 
                request, 
                f"User was banned (is_active set to False) for severe violation. Action taken by {request.user.username}."
            )
            
        self.message_user(request, f"Successfully banned user(s) and resolved {queryset.count()} report(s).")
        
    # --- Helper Action: Mark as Resolved (No Action) ---
    @admin.action(description='Mark selected reports as resolved (No action needed)')
    def mark_resolved_action(self, request, queryset):
        updated = self._resolve_reports(
            queryset, 
            'none', 
            request, 
            "Report dismissed as not violating policy."
        )
        self.message_user(request, f"{updated} reports successfully marked as resolved with no action.")