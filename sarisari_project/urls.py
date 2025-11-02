from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.contrib.auth import views as auth_views

urlpatterns = [
    path('password_reset_form/',
        auth_views.PasswordResetView.as_view(template_name='registration/password_reset_form.html'), 
        name='password_reset_form'),

    path('password_reset_done/',
        auth_views.PasswordResetDoneView.as_view(template_name='registration/password_reset_done.html'), 
        name='password_reset_done'),

    path('reset/<uidb64>/<token>/',
        auth_views.PasswordResetConfirmView.as_view(template_name='registration/password_reset_confirm.html'), 
        name='password_reset_confirm'),

    path('reset/done/',
        auth_views.PasswordResetCompleteView.as_view(template_name='registration/password_reset_complete.html'), 
        name='password_reset_complete'),

    path('admin/', admin.site.urls),
    path('auth/', include('users.urls')),
    path('my-products/', include('products.urls')),
    path('', include('pages.urls')), # Include the pages app URLs
    path('notifications/', include('notifications.urls')),
    path('messages/', include('messaging.urls')),
    path('dashboard/', include('dashboard.urls')),
]

# CRITICAL FIX: Conditionally serve Static and Media files only when DEBUG=True
if settings.DEBUG:
    # Serve media files (user uploads like milk.png, eggs.jpg)
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    
    # Also explicitly serve static files (like the placeholder.png)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)