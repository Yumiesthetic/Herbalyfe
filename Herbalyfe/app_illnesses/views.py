from django.shortcuts import render
from .models import Illness

# Create your views here.
def illness_list(request):
    illnesses = Illness.objects.all().order_by('name') # Fetch all illness objects ordered by name
    return render(request, 'illnesses/illnesses_list.html', {'illnesses': illnesses}) # Render the herbs list template with the herbs context

def illness_page(request, slug):
    illness = Illness.objects.get(slug=slug)  # Fetch the illness object based on the provided slug
    return render(request, 'illnesses/illness_page.html', {'illness': illness}) # Render the illness page template with the illness context
