from django.contrib import admin
from .models import Bridge, Feedback

@admin.register(Bridge)
class BridgeAdmin(admin.ModelAdmin):
    list_display = ('structure_number', 'data_year', 'county_code', 'deck_cond')
    list_filter = ('data_year', 'deck_cond')
    search_fields = ('structure_number', 'location')

@admin.register(Feedback)
class FeedbackAdmin(admin.ModelAdmin):
    list_display = ('bridge', 'name', 'rating', 'created_at')
    list_filter = ('rating', 'created_at')
    search_fields = ('bridge__structure_number', 'name', 'comment')
