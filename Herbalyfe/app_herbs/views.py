from django.shortcuts import redirect, render, get_object_or_404
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import json
from .models import Herb
from .models import HerbPin
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST
from django.contrib.auth.models import User
from .models import Favorite, HerbPin


# Create your views here.
def herb_list(request):
    herbs = Herb.objects.all().order_by('name')  # Fetch all herb objects ordered by name
    return render(request, 'herbs/herbs_list.html', {'herbs': herbs}) # Render the herbs list template with the herbs context


def herb_page(request, slug):
    herb = get_object_or_404(Herb, slug=slug)  # Fetch the herb object based on the provided slug
    return render(request, 'herbs/herb_page.html', {'herb': herb}) # Render the herb page template with the herb context

def herb_pins_json(request):
    herb_id = request.GET.get('herb_id')
    username = request.GET.get('username')

    pins = HerbPin.objects.select_related('herb', 'user')

    if herb_id:
        pins = pins.filter(herb_id=herb_id)
    if username:
        pins = pins.filter(user__username=username)

    user_favorites = set()
    if request.user.is_authenticated:
        user_favorites = set(
            Favorite.objects
            .filter(user=request.user)
            .values_list('pin_id', flat=True)
        )

    data = []
    for pin in pins:
        data.append({
            'id': pin.id,
            'herb': {
                'id': pin.herb.id,
                'name': pin.herb.name,
                'slug': pin.herb.slug,
            },
            'user': pin.user.username,
            'latitude': pin.latitude,
            'longitude': pin.longitude,
            'created_at': pin.created_at.isoformat(),
            'favorited': pin.id in user_favorites,
        })

    return JsonResponse({'pins': data})

def pin_users(request):
    """Return JSON list of users who have pinned herbs."""
    users = (
        User.objects
        .filter(herb_pins__isnull=False)
        .distinct()
        .values('username')
    )
    return JsonResponse({'users': list(users)})

@csrf_exempt
def pin_herb(request):
    """Accepts POST JSON: {herb_id, latitude, longitude} and saves a HerbPin."""
    if request.method != 'POST': # Ensure the request method is POST
        return JsonResponse({'error': 'bad method'}, status=405)

    if not request.user.is_authenticated: # Check if user is logged in
        return JsonResponse({'error': 'login required'}, status=403)

    try: # Parse the JSON data from the request body 
        data = json.loads(request.body)
        herb = Herb.objects.get(pk=int(data.get('herb_id')))
        lat = float(data.get('latitude'))
        lng = float(data.get('longitude'))

        # Create a new HerbPin
        pin = HerbPin.objects.create(
            herb=herb,
            user=request.user,
            latitude=lat,
            longitude=lng
        )

        return JsonResponse({
            'status': 'ok',
            'pin': {
                'id': pin.id,
                'herb': {'id': herb.id, 'name': herb.name, 'slug': herb.slug},
                'user': request.user.username,
                'latitude': lat,
                'longitude': lng,
            }
        })
    except Herb.DoesNotExist:
        return JsonResponse({'error': 'invalid herb_id'}, status=400)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=400)

@login_required
@require_POST
def delete_herb_pin(request, pin_id):
    """Delete a pin if the user is owner or superuser."""
    try:
        pin = HerbPin.objects.get(pk=pin_id)
        if request.user == pin.user or request.user.is_superuser:
            pin.delete()
            return JsonResponse({'status': 'ok'})
        else:
            return JsonResponse({'status': 'forbidden'}, status=403)
    except HerbPin.DoesNotExist:
        return JsonResponse({'status': 'not_found'}, status=404)

def herb_coords(request):
    """Return JSON list of herbs with coordinates."""
    herbs = Herb.objects.filter(latitude__isnull=False, longitude__isnull=False)
    data = [{'id': h.id, 'name': h.name, 'latitude': h.latitude, 'longitude': h.longitude, 'slug': h.slug} for h in herbs]
    return JsonResponse({'herbs': data})


def herb_list_json(request):
    """Return JSON list of all herbs (id, name, slug) for populating UI choices."""
    herbs = Herb.objects.all().order_by('name')
    data = [{'id': h.id, 'name': h.name, 'slug': h.slug} for h in herbs]
    return JsonResponse({'herbs': data})

@login_required
def favorite_pins_json(request):
    favorites = request.user.favorite_pins.select_related(
        'pin__herb', 'pin__user'
    )

    data = []
    for fav in favorites:
        pin = fav.pin
        data.append({
            'id': pin.id,
            'herb': {
                'id': pin.herb.id,
                'name': pin.herb.name,
                'slug': pin.herb.slug
            },
            'user': pin.user.username,
            'latitude': pin.latitude,
            'longitude': pin.longitude,
            'created_at': pin.created_at.isoformat(),
            'favorited': True,
        })

    return JsonResponse({'pins': data})

@login_required
@require_POST
def toggle_favorite(request, pin_id):
    """Toggle favorite/unfavorite for the logged-in user."""
    try:
        pin = HerbPin.objects.get(pk=pin_id)
        favorite, created = Favorite.objects.get_or_create(user=request.user, pin=pin)
        if not created:
            favorite.delete()
            return JsonResponse({'status': 'unfavorited'})
        return JsonResponse({'status': 'favorited'})
    except HerbPin.DoesNotExist:
        return JsonResponse({'status': 'not_found'}, status=404)
