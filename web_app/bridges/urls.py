from django.urls import path
from . import views

urlpatterns = [
    path('', views.dashboard, name='dashboard'),
    path('api/map-data/', views.map_data, name='map_data'),
    path('bridge/<int:bridge_id>/', views.bridge_detail, name='bridge_detail'),
    path('export/', views.export_bridges, name='export_bridges'),
]
