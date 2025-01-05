from django.forms import ValidationError
from django.shortcuts import get_object_or_404, render, redirect
from django.core.mail import send_mail
from django.conf import settings
from django.contrib import messages
from django.template.loader import render_to_string
from django.utils import timezone
from django.contrib.auth.decorators import login_required
import pytz
import logging
from .models import Certification, CoachingRequest, HomePageContent, PricingPlan
from .forms import CertificationForm, CoachingRequestForm, PricingPlanForm

logger = logging.getLogger(__name__)

def index(request):
    plans = PricingPlan.objects.all()
    home_content = HomePageContent.objects.first()
    certifications = Certification.objects.all() 
    return render(
        request, "coaching/index.html", {"plans": plans, "home_content": home_content, 'certifications': certifications}
    )

def coaching_request_view(request, plan_id):
    try:
        plan = get_object_or_404(PricingPlan, pk=plan_id)
    except PricingPlan.DoesNotExist:
        messages.error(request, "الخطة المحددة غير صالحة.")
        return redirect("coaching:index")

    if request.method == "POST":
        form = CoachingRequestForm(request.POST)
        if form.is_valid():
            selected_date = form.cleaned_data["scheduled_datetime"]
            selected_time = form.cleaned_data["available_times"]
            user_timezone = form.cleaned_data["timezone"]

            # Combine selected date and time
            combined_datetime_str = (
                f"{selected_date.strftime('%Y-%m-%d')} {selected_time}"
            )
            combined_datetime = timezone.datetime.strptime(
                combined_datetime_str, "%Y-%m-%d %H:%M"
            )

            # 1. Localize the combined datetime to the default timezone (e.g., 'Africa/Cairo')
            egypt_tz = pytz.timezone(
                "Africa/Cairo"
            )  # Or settings.TIME_ZONE if you have it set
            localized_datetime = egypt_tz.localize(combined_datetime)

            # 2. Convert the localized datetime to the user's timezone
            user_tz = pytz.timezone(user_timezone)
            user_datetime = localized_datetime.astimezone(user_tz)

            # 3. Save the datetime to the database in UTC
            coaching_request = form.save(commit=False)
            coaching_request.scheduled_datetime = localized_datetime.astimezone(pytz.utc)  # Save in UTC
            coaching_request.plan = plan

            # Check for double-booking before saving
            is_double_booked = CoachingRequest.objects.filter(
                scheduled_datetime=coaching_request.scheduled_datetime
            ).exists()

            if is_double_booked:
                messages.error(request, "لقد تم حجز هذه الفترة الزمنية بالفعل. يرجى اختيار وقت آخر.")
                return render(request, "coaching/coaching_request_form.html", {"form": form, "plan": plan})

            coaching_request.save()

            user_email = form.cleaned_data["email"]
            user_name = form.cleaned_data["name"]

            # User email context (in user's timezone)
            context = {
                "name": user_name,
                "scheduled_date": user_datetime.strftime("%Y-%m-%d"),
                "scheduled_time": user_datetime.strftime("%I:%M %p"),
                "plan_name": plan.name,
            }
            subject = "تأكيد طلب الاستشارة التدريبية الخاص بك"
            html_message = render_to_string(
                "coaching/emails/coaching_request_confirmation.html", context
            )
            send_mail(
                subject,
                "",
                settings.DEFAULT_FROM_EMAIL,
                [user_email],
                html_message=html_message,
                fail_silently=False,
            )

            # Admin email context (in default/Egypt timezone)
            admin_email = settings.ADMIN_EMAIL
            admin_context = {
                "name": user_name,
                "phone": form.cleaned_data["phone"],
                "email": user_email,
                "scheduled_date": localized_datetime.strftime("%Y-%m-%d"),
                "scheduled_time": localized_datetime.strftime("%I:%M %p"),
                "timezone": user_timezone,
                "details": form.cleaned_data["details"],
                "plan_name": plan.name,
            }
            admin_subject = f"طلب استشارة تدريبية جديد من {user_name}"
            admin_html_message = render_to_string(
                "coaching/emails/new_coaching_request_notification.html", admin_context
            )
            send_mail(
                admin_subject,
                "",
                settings.DEFAULT_FROM_EMAIL,
                [admin_email],
                html_message=admin_html_message,
                fail_silently=False,
            )

            messages.success(
                request,
                "تم تقديم طلب الاستشارة التدريبية الخاص بك بنجاح، وسوف نتواصل معك قريباً لتأكيد الموعد!",
            )
            return redirect("coaching:index")
        else:
            logger.error(f"Form is invalid. Errors: {form.errors}")

            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, f"{form.fields[field].label}: {error}")
            return render(
                request,
                "coaching/coaching_request_form.html",
                {"form": form, "plan": plan},
            )
    else:
        form = CoachingRequestForm(initial={"plan": plan})

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
    home_content, created = (
        HomePageContent.objects.get_or_create()
    )  # Get or create a single object
    if request.method == "POST":
        home_content.hero_title = request.POST.get("hero_title")
        home_content.hero_description = request.POST.get("hero_description")
        home_content.about_title = request.POST.get("about_title")
        home_content.about_description = request.POST.get("about_description")

        # handle image upload
        if "about_image" in request.FILES:
            home_content.about_image = request.FILES["about_image"]

        try:
            home_content.save()
            return redirect("coaching:home_content")
        except ValidationError as e:
            context = {"home_content": home_content, "errors": e}
            return render(request, "coaching/dashboard/home_content.html", context)

    context = {"home_content": home_content}
    return render(request, "coaching/dashboard/home_content.html", context)


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
        form = PricingPlanForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect("coaching:plan_list")
    else:
        form = PricingPlanForm()

    return render(request, "coaching/dashboard/plan_create.html", {"form": form})


@login_required
def plan_edit(request, plan_id):
    """
    Displays a form to edit an existing pricing plan and handles the update.
    """
    plan = get_object_or_404(PricingPlan, id=plan_id)
    if request.method == "POST":
        form = PricingPlanForm(request.POST, instance=plan)
        if form.is_valid():
            form.save()
            return redirect("coaching:plan_list")
    else:
        form = PricingPlanForm(instance=plan)

    return render(
        request, "coaching/dashboard/plan_edit.html", {"form": form, "plan": plan}
    )


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


# Certification Views
@login_required
def certification_list(request):
    """Displays a list of all certifications."""
    certifications = Certification.objects.all()
    context = {"certifications": certifications}
    return render(request, "coaching/dashboard/certification_list.html", context)

@login_required
def certification_create(request):
    if request.method == "POST":
        form = CertificationForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            return redirect("coaching:certification_list")
    else:
        form = CertificationForm()
    return render(request, "coaching/dashboard/certification_create.html", {"form": form})

@login_required
def certification_edit(request, certification_id):
    """Displays a form to edit an existing certification and handles the update."""
    certification = get_object_or_404(Certification, id=certification_id)
    if request.method == "POST":
        form = CertificationForm(request.POST, request.FILES, instance=certification)
        if form.is_valid():
            form.save()
            return redirect("coaching:certification_list")
    else:
        form = CertificationForm(instance=certification)
    return render(
        request, "coaching/dashboard/certification_edit.html", {"form": form, "certification": certification}
    )

@login_required
def certification_delete(request, certification_id):
    """Deletes a certification using its ID after confirmation."""
    certification = get_object_or_404(Certification, id=certification_id)
    if request.method == "POST":
        certification.delete()
        return redirect("coaching:certification_list")
    return render(
        request, "coaching/dashboard/certification_delete_confirmation.html", {"certification": certification}
    )