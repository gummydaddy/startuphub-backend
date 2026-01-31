"""
URL configuration for startuphub project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
# startuphub/urls.py

from django.contrib import admin
from django.urls import path, include
from django.shortcuts import redirect
from django.http import JsonResponse
from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

from founders.views import FounderProfileViewSet, ConnectionViewSet
from ideas.views import IdeaViewSet
from matching.views import MatchingViewSet
from rooms.views import CoWorkingRoomViewSet, ProgressUpdateViewSet
from direct_messages.views import DirectMessageViewSet  # ← UPDATED IMPORT


def redirect_to_frontend(request):
    return redirect('https://startuphub-umber.vercel.app/')


def api_root(request):
    return JsonResponse({
        'message': 'Welcome to startup.hub API',
        'version': '1.0.0',
        'frontend': 'https://startuphub-umber.vercel.app/',
        'endpoints': {
            'authentication': {
                'register': '/api/auth/register/',
                'login': '/api/token/',
                'refresh': '/api/token/refresh/',
            },
            'resources': {
                'founders': '/api/founders/',
                'connections': '/api/connections/',
                'ideas': '/api/ideas/',
                'matching': '/api/matching/',
                'rooms': '/api/rooms/',
                'messages': '/api/messages/',
                'progress': '/api/progress/',
            },
        }
    })


router = DefaultRouter()
router.register(r'founders', FounderProfileViewSet, basename='founder')
router.register(r'connections', ConnectionViewSet, basename='connection')
router.register(r'ideas', IdeaViewSet, basename='idea')
router.register(r'matching', MatchingViewSet, basename='matching')
router.register(r'rooms', CoWorkingRoomViewSet, basename='room')
router.register(r'messages', DirectMessageViewSet, basename='message')  # ← UPDATED
router.register(r'progress', ProgressUpdateViewSet, basename='progress')

urlpatterns = [
    path('', redirect_to_frontend, name='home'),
    path('admin/', admin.site.urls),
    
    path('api/', api_root, name='api_root'),
    path('api/', include(router.urls)),
    
    path('api/auth/', include('accounts.urls')),
    path('api/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
]