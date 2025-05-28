from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse
from django.contrib import messages
from .models import Violation, Offender
from .forms import ImageUploadForm
from django.conf import settings
import os
import uuid
from violation_detector import ViolationDetector

def dashboard(request):
    return redirect('detect_violation')

def detect_violation(request):
    results = None
    uploaded_image_url = None
    if request.method == 'POST':
        form = ImageUploadForm(request.POST, request.FILES)
        if form.is_valid():
            image = form.cleaned_data['image']
            # Save uploaded image to media directory
            media_root = getattr(settings, 'MEDIA_ROOT', os.path.join(settings.BASE_DIR, 'media'))
            os.makedirs(media_root, exist_ok=True)
            filename = f"{uuid.uuid4().hex}_{image.name}"
            image_path = os.path.join(media_root, filename)
            with open(image_path, 'wb+') as f:
                for chunk in image.chunks():
                    f.write(chunk)
            # Prepare uploaded image URL for display
            rel_path = os.path.relpath(image_path, media_root)
            uploaded_image_url = settings.MEDIA_URL + rel_path.replace('\\', '/')
            # Run detection (no DB logging here!)
            detector = ViolationDetector()
            detection_result = detector.process_image(image_path)
            # Log violations using Django ORM
            results = []
            plate_number = detection_result['plate_number']
            if detection_result['violations'] and plate_number:
                # Get or create offender
                from .models import Offender, Violation
                offender, created = Offender.objects.get_or_create(plate_number=plate_number)
                for violation_type in detection_result['violations']:
                    Violation.objects.create(
                        plate_number=offender,
                        violation_type=violation_type,
                        image_path=uploaded_image_url,
                        confidence=0.0  # You can pass real confidence if available
                    )
                # Update offender stats
                total_violations = Violation.objects.filter(plate_number=offender).count()
                last_violation = Violation.objects.filter(plate_number=offender).order_by('-date_time').first().date_time
                is_repeat = total_violations > 3
                offender.total_violations = total_violations
                offender.last_violation = last_violation
                offender.is_repeat_offender = is_repeat
                offender.save()
                results.append(f"Violations Detected: {', '.join(detection_result['violations'])}")
                results.append(f"License Plate: {plate_number}")
                results.append(f"Repeat Offender: {'Yes' if is_repeat else 'No'} (Total: {total_violations})")
            elif detection_result['violations']:
                results.append(f"Violations Detected: {', '.join(detection_result['violations'])}")
                results.append("License Plate: Not Detected")
            else:
                results.append("No violations detected.")
        else:
            messages.error(request, 'Invalid image upload.')
    else:
        form = ImageUploadForm()
    return render(request, 'violations/detect.html', {
        'form': form,
        'results': results,
        'uploaded_image_url': uploaded_image_url
    })

def offender_logs(request, plate_number):
    from .models import Violation, Offender
    offender = Offender.objects.filter(plate_number=plate_number).first()
    violations = Violation.objects.filter(plate_number=offender).order_by('-date_time')
    return render(request, 'violations/logs.html', {'violations': violations, 'offender': offender})

# Violation logs table
def violation_logs(request):
    violations = Violation.objects.select_related('plate_number').order_by('-date_time')
    return render(request, 'violations/logs.html', {'violations': violations})

# Repeat offenders table
def repeat_offenders(request):
    offenders = Offender.objects.filter(is_repeat_offender=True).order_by('-total_violations')
    return render(request, 'violations/repeat_offenders.html', {'offenders': offenders})

# Delete a single violation
def delete_violation(request, violation_id):
    violation = get_object_or_404(Violation, id=violation_id)
    # Delete associated image file if not used elsewhere
    if violation.image_path:
        from django.conf import settings
        import os
        # Remove MEDIA_URL prefix to get relative path
        rel_path = violation.image_path.replace(settings.MEDIA_URL, '').replace('\\', '/').lstrip('/')
        abs_path = os.path.join(settings.MEDIA_ROOT, rel_path)
        # Only delete if no other violation uses this image
        if not Violation.objects.filter(image_path=violation.image_path).exclude(id=violation.id).exists():
            if os.path.exists(abs_path):
                os.remove(abs_path)
    violation.delete()
    messages.success(request, 'Violation deleted.')
    return redirect('violation_logs')

# Delete all violations for an offender
def delete_offender(request, plate_number):
    offender = get_object_or_404(Offender, plate_number=plate_number)
    offender.delete()
    messages.success(request, f'All violations for {plate_number} deleted.')
    return redirect('repeat_offenders')

# Delete all violations
def delete_all_violations(request):
    from django.conf import settings
    import os
    # Delete all associated image files
    for violation in Violation.objects.all():
        if violation.image_path:
            rel_path = violation.image_path.replace(settings.MEDIA_URL, '').replace('\\', '/').lstrip('/')
            abs_path = os.path.join(settings.MEDIA_ROOT, rel_path)
            if os.path.exists(abs_path):
                os.remove(abs_path)
    Violation.objects.all().delete()
    Offender.objects.all().delete()
    messages.success(request, 'All violations and images deleted.')
    return redirect('violation_logs')
