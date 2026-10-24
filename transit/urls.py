from django.urls import path
from . import views

urlpatterns = [
    path('transit/', views.transit_schedules_view, name='transit_schedules'),
    path('transit/book/<int:schedule_id>/', views.book_ticket_view, name='book_ticket'),
]
