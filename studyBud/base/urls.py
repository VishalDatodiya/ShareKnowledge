from django.urls import path

from base.views import home, room, create_room, update_room, detete_room, loginPage, logoutUser, registerPage, detete_message, userProfile, update_user, topicsPage, activityPage

urlpatterns = [
    path('login/', loginPage, name='login'),
    path('logout/', logoutUser, name="logout"),
    path('register/', registerPage, name='register'),
    
    path('', home, name="home"),
    path('room/<int:pk>/', room, name='room'),
    path('user-profile/<int:pk>/', userProfile, name='user-profile'),
    
    path('create-room/', create_room, name='create-room'),
    path('update-room/<int:pk>/', update_room, name='update-room'),
    path('delete-room/<int:pk>/', detete_room, name='delete-room'),
    path('delete-message/<int:pk>/', detete_message, name='delete-message'),
    path('update-user/', update_user, name='update-user'),
    
    # Mobile responsive urls
    path('topics/', topicsPage, name='topics'),
    path('activity/', activityPage, name='activity'),
]
