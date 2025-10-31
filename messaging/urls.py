# messaging/urls.py
from django.urls import path
from . import views

urlpatterns = [
    # /messages/
    path('', views.inbox_view, name='inbox'),
    
    # /messages/1/ (where 1 is the conversation ID)
    path('<int:conversation_id>/', views.conversation_detail_view, name='conversation_detail'),
    
    # /messages/start/2/ (where 2 is the recipient's user ID)
    path('start/<int:recipient_id>/', views.start_conversation_view, name='start_conversation'),
]