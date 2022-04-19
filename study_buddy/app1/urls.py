from django.urls import path
from . import views

urlpatterns = [
    path('user_profile/<str:pk>/', views.userProfile, name="user_profile"),
    path('login/', views.loginPage, name="login"),
    path('logout/', views.logoutPage, name="logout"),
    path('register/', views.registerPage, name="register"),

    path('', views.home, name="home"),
    path('room/<str:pk>/', views.room, name="room"),
    path('create-room/', views.createRoom, name="create-room"),
    path('update-room/<str:pk>/', views.updateRoom, name="update-room"),
    path('delete-room/<str:pk>/', views.deleteRoom, name="delete-room"),
    
    path('delete-message/<str:pk>/', views.deleteMessage, name="delete-message"),
]

