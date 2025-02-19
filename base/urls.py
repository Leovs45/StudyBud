from django.urls import path
from . import views # Importa las vistas del archivo views.py

urlpatterns = [
    
    path('login/', views.loginPage, name="login"),
    path('logout/', views.logoutUser, name="logout"),
    path('register/', views.registerPage, name="register"),
    
    path('', views.home, name="home"),
    path('room/<str:pk>/', views.room, name="room"),
    path('profile/<str:pk>', views.userProfile, name="user-profile"),

    path('create-room/', views.createRoom, name="create-room"),
    path('update-room/<str:pk>/', views.updateRoom, name="update-room"),
    path('delete-room/<str:pk>/', views.deleteRoom, name="delete-room"),
    path('delete-message/<str:pk>/', views.deleteMessage, name="delete-message"),
    path('update-user/', views.updateUser, name="update-user"),

    path('topics/', views.topicsPage, name="topics"),
    path('activity/', views.activityPage, name="activity"),
#     -Aquí, path('room/<int:pk>/', views.room, name='room'):
#    -Define que la URL /room/1/ llamará a la función room(request, pk=1).
#    -La parte <int:pk> indica que se espera un número entero como parámetro.
#    -name='room' permite que las plantillas usen {% url 'room' room.id %} en lugar de escribir manualmente la URL.
]