from django.shortcuts import render, redirect
from django.contrib import messages
from .forms import CoachingRequestForm
from django.utils import timezone

def index(request):
    return render(request, 'index.html')


def coaching_request_view(request):
    if request.method == 'POST':
        form = CoachingRequestForm(request.POST)
        if form.is_valid():
            # Check if scheduled_datetime is in the future
            scheduled_datetime = form.cleaned_data['scheduled_datetime']
            if scheduled_datetime <= timezone.now() + timezone.timedelta(hours=24):
                 messages.error(request, 'Please select a date and time at least 24 hours in the future.')
            else:
                form.save()
                messages.success(request, 'Your coaching request has been submitted successfully!')
                return redirect('coaching_request')  # Redirect to a success page or the same form
        else:
             for error in form.errors.values():
                  messages.error(request, error)

    else:
        form = CoachingRequestForm()

    return render(request, 'coaching_request_form.html', {'form': form})