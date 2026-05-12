from django.shortcuts import redirect, render
from django.http import JsonResponse
import json
from .models import HerbPin, PinReport
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST


@login_required
@require_POST
def submit_report(request, pin_id):

    try:
        pin = HerbPin.objects.get(pk=pin_id)

        data = json.loads(request.body)
        reason = data.get('reason', '').strip()

        if not reason:
            return JsonResponse({
                'status': 'error',
                'message': 'Reason is required.'
            }, status=400)
        
        existing = PinReport.objects.filter(
            reported_pin=pin,
            reported_by=request.user,
            status='PENDING'
        ).exists()

        if existing:
            return JsonResponse({
                'status': 'error',
                'message': 'You already reported this pin.'
            })

        PinReport.objects.create(
            reported_pin=pin,
            reported_by=request.user,
            reason=reason,
            original_pin_owner=pin.user.username # still showing the original name, for easier admin review
        )

        return JsonResponse({
            'status': 'ok'
        })

    except HerbPin.DoesNotExist:
        return JsonResponse({
            'status': 'not_found'
        }, status=404)


@login_required
def report_list(request):

    if not request.user.is_superuser:
        return redirect('/')

    reports = PinReport.objects.select_related(
        'reported_pin',
        'reported_pin__user',
        'reported_by'
    )

    # Status filtering
    status_filter = request.GET.get('status', '')

    if status_filter:
        reports = reports.filter(status=status_filter)

    # Sorting
    sort = request.GET.get('sort', 'newest')

    if sort == 'oldest':
        reports = reports.order_by('created_at')

    elif sort == 'id_asc':
        reports = reports.order_by('id')

    elif sort == 'id_desc':
        reports = reports.order_by('-id')

    else:
        reports = reports.order_by('-created_at')

    return render(request, 'reports/report_list.html', {
        'reports': reports,
        'status_filter': status_filter,
        'sort': sort,
    })

@login_required
@require_POST
def update_report_status(request, report_id, status):

    if not request.user.is_superuser:
        return redirect('/')

    try:
        report = PinReport.objects.get(pk=report_id)

        if status in ['APPROVED', 'DENIED']:
            report.status = status
            report.save()

            # delete pin automatically if approved
            if status == 'APPROVED':
                if report.reported_pin:
                    report.reported_pin.delete()

    except PinReport.DoesNotExist:
        pass

    return redirect('/reports/')


@login_required
@require_POST
def clear_logs(request):

    if not request.user.is_superuser:
        return redirect('/')

    PinReport.objects.exclude(status='PENDING').delete()

    return redirect('/reports/')