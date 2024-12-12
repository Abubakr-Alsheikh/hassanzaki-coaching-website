import datetime
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, render, redirect
from django.core.mail import send_mail
from django.conf import settings  # Import settings for email configuration
from django.contrib import messages
from django.template.loader import render_to_string
from django.utils import timezone
from django.contrib.auth.decorators import login_required

from .models import CoachingRequest, PricingPlan
from .forms import CoachingRequestForm


def index(request):
    plans = PricingPlan.objects.all()
    return render(request, 'coaching/index.html', {'plans': plans})

def coaching_request_view(request, plan_id):
    try:
        plan = get_object_or_404(PricingPlan, pk=plan_id)
    except PricingPlan.DoesNotExist:
        messages.error(request, "Invalid plan selected.")
        return redirect('coaching:index')

    if request.method == 'POST':
        form = CoachingRequestForm(request.POST)
        if form.is_valid():

            selected_date = form.cleaned_data['scheduled_datetime']
            selected_time = form.cleaned_data['available_times']
            # Combine selected date and time
            combined_datetime_str = f"{selected_date.strftime('%Y-%m-%d')} {selected_time}"
            combined_datetime = timezone.datetime.strptime(combined_datetime_str, '%Y-%m-%d %H:%M')
            coaching_request = form.save(commit=False)
            coaching_request.scheduled_datetime = combined_datetime
            coaching_request.plan = plan
            coaching_request.save()
            # Send email to the user
            # user_email = form.cleaned_data['email']
            # user_name = form.cleaned_data['name']
            # context = {
            #     'name': user_name,
            #     'scheduled_date':coaching_request.scheduled_datetime.strftime("%Y-%m-%d"),
            #     'scheduled_time': coaching_request.scheduled_datetime.strftime("%H:%M"),
            # }
            # subject = 'Your Coaching Request Confirmation'
            # html_message = render_to_string('emails/coaching_request_confirmation.html', context)
            # send_mail(subject, '', settings.DEFAULT_FROM_EMAIL,[user_email], html_message=html_message, fail_silently=False)


            # # Send email to the coach/admin
            # admin_email = settings.ADMIN_EMAIL  # Replace with your admin email
            # admin_context = {
            #     'name': user_name,
            #     'phone': form.cleaned_data['phone'],
            #     'email':user_email,
            #     'scheduled_date': coaching_request.scheduled_datetime.strftime("%Y-%m-%d"),
            #     'scheduled_time': coaching_request.scheduled_datetime.strftime("%H:%M"),
            #     'coaching_niche': form.cleaned_data['coaching_niche'],
            #     'details':form.cleaned_data['details'],

            # }
            # admin_subject = f'New Coaching Request from {user_name}'
            # admin_html_message = render_to_string('emails/new_coaching_request_notification.html', admin_context)
            # send_mail(admin_subject, '', settings.DEFAULT_FROM_EMAIL, [admin_email], html_message=admin_html_message, fail_silently=False)

            messages.success(request, 'Your coaching request has been submitted successfully, wait until we contact you!')
            return redirect('coaching:index')
    else:
        try:
            selected_plan = PricingPlan.objects.get(pk=plan_id)
            form = CoachingRequestForm(initial={'plan': selected_plan})
        except PricingPlan.DoesNotExist:
             form = CoachingRequestForm()

    return render(request, 'coaching/coaching_request_form.html', {'form': form, 'plan': plan})

@login_required
def dashboard(request):
    context = {'user': request.user}
    return render(request, 'coaching/dashboard/_dashboard.html', context)

@login_required
def request_list(request):
    coaching_requests = CoachingRequest.objects.order_by('-created_at')
    context = {'coaching_requests': coaching_requests}
    return render(request, 'coaching/dashboard/request_list.html', context)
