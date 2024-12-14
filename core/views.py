import datetime
from django.forms import ValidationError
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, render, redirect
from django.core.mail import send_mail
from django.conf import settings  # Import settings for email configuration
from django.contrib import messages
from django.template.loader import render_to_string
from django.utils import timezone
from django.contrib.auth.decorators import login_required

from .models import CoachingRequest, HomePageContent, PricingPlan
from .forms import CoachingRequestForm


def index(request):
    plans = PricingPlan.objects.all()
    home_content = HomePageContent.objects.first()
    return render(request, 'coaching/index.html', {'plans': plans, 'home_content': home_content})


def coaching_request_view(request, plan_id):
    try:
        plan = get_object_or_404(PricingPlan, pk=plan_id)
    except PricingPlan.DoesNotExist:
        messages.error(request, "Invalid plan selected.")
        return redirect("coaching:index")

    if request.method == "POST":
        form = CoachingRequestForm(request.POST)
        if form.is_valid():
            selected_date = form.cleaned_data["scheduled_datetime"]
            selected_time = form.cleaned_data["available_times"]
            # Combine selected date and time
            combined_datetime_str = (
                f"{selected_date.strftime('%Y-%m-%d')} {selected_time}"
            )
            combined_datetime = timezone.datetime.strptime(
                combined_datetime_str, "%Y-%m-%d %H:%M"
            )
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

            messages.success(
                request,
                "Your coaching request has been submitted successfully, wait until we contact you!",
            )
            return redirect("coaching:index")
        else:
            return render(
                request, "coaching/coaching_request_form.html", {"form": form, "plan": plan}
            )
    else:
        try:
            selected_plan = PricingPlan.objects.get(pk=plan_id)
            form = CoachingRequestForm(initial={"plan": selected_plan})
        except PricingPlan.DoesNotExist:
            form = CoachingRequestForm()

    return render(
        request, "coaching/coaching_request_form.html", {"form": form, "plan": plan}
    )


@login_required
def dashboard(request):
    context = {"user": request.user}
    return render(request, "coaching/dashboard/_dashboard.html", context)


@login_required
def home_content(request):
    """Displays the form to edit the home page content."""
    home_content, created = HomePageContent.objects.get_or_create()  # Get or create a single object
    if request.method == 'POST':
        home_content.hero_title = request.POST.get('hero_title')
        home_content.hero_description = request.POST.get('hero_description')
        home_content.about_title = request.POST.get('about_title')
        home_content.about_description = request.POST.get('about_description')

        # handle image upload
        if 'about_image' in request.FILES:
            home_content.about_image = request.FILES['about_image']


        try:
           home_content.save()
           return redirect('coaching:home_content')
        except ValidationError as e:
            context = {'home_content': home_content, 'errors': e}
            return render(request, 'coaching/dashboard/home_content.html', context)

    context = {'home_content': home_content}
    return render(request, 'coaching/dashboard/home_content.html', context)

@login_required
def request_list(request):
    """
    Displays a list of coaching requests.
    Allows toggling between future requests only and all requests, including hiding functionality.
    """
    show_all = request.GET.get("show_all", False) == "true"
    now = timezone.now()

    if show_all:
        coaching_requests = CoachingRequest.objects.all().order_by("scheduled_datetime")
    else:
        coaching_requests = CoachingRequest.objects.filter(
            scheduled_datetime__gte=now, is_hidden=False
        ).order_by("scheduled_datetime")

    context = {
        "coaching_requests": coaching_requests,
        "show_all": show_all,
    }
    return render(request, "coaching/dashboard/request_list.html", context)


@login_required
def hide_request(request, request_id):
    """
    Hides a coaching request using its ID.
    """
    coaching_request = get_object_or_404(CoachingRequest, id=request_id)
    coaching_request.is_hidden = True
    coaching_request.save()
    return redirect("coaching:request_list")


@login_required
def delete_request(request, request_id):
    """
    Deletes a coaching request using its ID after confirmation.
    """
    coaching_request = get_object_or_404(CoachingRequest, id=request_id)
    if request.method == "POST":
        coaching_request.delete()
        return redirect("coaching:request_list")
    return render(
        request,
        "coaching/dashboard/request_delete.html",
        {"coaching_request": coaching_request},
    )


@login_required
def plan_list(request):
    """Displays a list of all pricing plans."""
    plans = PricingPlan.objects.all().order_by("price")
    context = {"plans": plans}
    return render(request, "coaching/dashboard/plan_list.html", context)


@login_required
def plan_create(request):
    if request.method == "POST":
        name = request.POST.get("name")
        description = request.POST.get("description")
        price = request.POST.get("price")
        sessions = request.POST.get("sessions")
        featured = request.POST.get("featured") == "on"

        try:
            PricingPlan.objects.create(
                name=name,
                description=description,
                price=price,
                sessions=sessions,
                featured=featured,
            )
            return redirect("coaching:plan_list")
        except ValidationError as e:
            context = {"errors": e}
            return render(request, "coaching/dashboard/plan_create.html", context)
    return render(request, "coaching/dashboard/plan_create.html")


@login_required
def plan_edit(request, plan_id):
    """
    Displays a form to edit an existing pricing plan and handles the update.
    """
    plan = get_object_or_404(PricingPlan, id=plan_id)
    if request.method == "POST":
        plan.name = request.POST.get("name")
        plan.description = request.POST.get("description")
        plan.price = request.POST.get("price")
        plan.sessions = request.POST.get("sessions")
        plan.featured = request.POST.get("featured") == "on"
        try:
            plan.save()
            return redirect("coaching:plan_list")
        except ValidationError as e:
            context = {"plan": plan, "errors": e}
            return render(request, "coaching/dashboard/plan_edit.html", context)

    context = {"plan": plan}
    return render(request, "coaching/dashboard/plan_edit.html", context)


@login_required
def plan_delete(request, plan_id):
    """
    Deletes a pricing plan using its ID after confirmation.
    """
    plan = get_object_or_404(PricingPlan, id=plan_id)
    if request.method == "POST":
        plan.delete()
        return redirect("coaching:plan_list")
    return render(
        request, "coaching/dashboard/plan_delete_confirmation.html", {"plan": plan}
    )
