from django.urls import path
from kiwi import views

urlpatterns = [
    path('', views.index, name="home"),
    path('get-data/', views.getflys),
    path('check-fly/', views.checkfly)
]
