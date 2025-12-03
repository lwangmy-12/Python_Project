from django.shortcuts import render, get_object_or_404, redirect
from django.http import HttpResponse, JsonResponse
from django.core.paginator import Paginator
from .models import Bridge, Feedback
from .forms import FeedbackForm
import openpyxl
from django.db.models import Count

def dashboard(request):
    # Get unique years for filter
    years = Bridge.objects.values_list('data_year', flat=True).distinct().order_by('-data_year')
    selected_year = request.GET.get('year')
    
    if not selected_year and years:
        selected_year = years[0]
    
    bridges = Bridge.objects.all()
    if selected_year:
        bridges = bridges.filter(data_year=selected_year)
    
    # Limit for map performance, or use API for map data
    # For the initial load, maybe just send some stats or a subset
    
    # Condition stats for chart
    cond_stats = bridges.values('deck_cond').annotate(count=Count('deck_cond')).order_by('deck_cond')
    
    context = {
        'years': years,
        'selected_year': selected_year,
        'cond_stats': list(cond_stats),
        'total_bridges': bridges.count()
    }
    return render(request, 'bridges/dashboard.html', context)

def map_data(request):
    year = request.GET.get('year')
    bridges = Bridge.objects.all()
    if year:
        bridges = bridges.filter(data_year=year)
    
    # Return JSON for Leaflet
    data = list(bridges.values('id', 'structure_number', 'latitude', 'longitude', 'deck_cond', 'features_desc'))
    return JsonResponse(data, safe=False)

def bridge_detail(request, bridge_id):
    bridge = get_object_or_404(Bridge, id=bridge_id)
    feedbacks = bridge.feedbacks.all().order_by('-created_at')
    
    if request.method == 'POST':
        form = FeedbackForm(request.POST)
        if form.is_valid():
            feedback = form.save(commit=False)
            feedback.bridge = bridge
            feedback.save()
            return redirect('bridge_detail', bridge_id=bridge.id)
    else:
        form = FeedbackForm()
        
    return render(request, 'bridges/detail.html', {
        'bridge': bridge,
        'feedbacks': feedbacks,
        'form': form
    })

def export_bridges(request):
    response = HttpResponse(content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
    response['Content-Disposition'] = 'attachment; filename=bridges.xlsx'
    
    wb = openpyxl.Workbook()
    ws = wb.active
    ws.title = "Bridges"
    
    columns = ['Structure Number', 'Year', 'County', 'Location', 'Deck Condition', 'Latitude', 'Longitude']
    ws.append(columns)
    
    year = request.GET.get('year')
    bridges = Bridge.objects.all()
    if year:
        bridges = bridges.filter(data_year=year)
        
    for bridge in bridges[:5000]: # Limit to avoid timeout for this demo
        ws.append([
            bridge.structure_number,
            bridge.data_year,
            bridge.county_code,
            bridge.location,
            bridge.deck_cond,
            bridge.latitude,
            bridge.longitude
        ])
        
    wb.save(response)
    return response
