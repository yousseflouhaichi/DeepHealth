from django.urls import path
from .views import *
from django.conf import settings
from django.conf.urls.static import static
# from . import views

urlpatterns = [
    path('register/', registerForm, name='register'),
    path('login/', loginForm, name='login'),
    path('logout/', logoutUser, name="logout"),
    path('dashboard/', predict, name="dashboard"),
    path("predict/", predict, name="predict"),
    path("history", history, name="history"),
]

urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)