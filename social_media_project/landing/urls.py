from django.urls import path
from landing.views import index
urlpatterns = [
    path('',index.as_view(),name='index'),
]