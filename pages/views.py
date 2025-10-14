from django.shortcuts import render

def about_us_view(request):
    # This view's only job is to render the 'about.html' template.
    return render(request, 'pages/about.html')

def home_view(request):
    return render(request, 'pages/home.html')