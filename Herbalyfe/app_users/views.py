from django.shortcuts import render, redirect
from .forms import CustomUserCreationForm, ProfileUpdateForm, CustomPasswordChangeForm, PasswordRecoveryForm, VerificationCodeForm, ResetPasswordForm
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.contrib.auth import update_session_auth_hash
from django.contrib.auth.models import User
import random
from django.utils import timezone
from datetime import timedelta
from django.core.mail import EmailMultiAlternatives


def register_view(request):
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST, request.FILES)
        if form.is_valid():
            user = form.save()
            login(request, user)

            # Save avatar to user's Profile
            avatar = form.cleaned_data.get('avatar')
            if avatar:
                user.profile.avatar = avatar  # assign uploaded image to Profile
                user.profile.save()

            return redirect('/')
    else:
        form = CustomUserCreationForm()

    return render(request, 'users/register.html', {'form': form})

def login_view(request):
    if request.method == "POST":
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            login(request, form.get_user())
            return redirect('/')
    else:
        form = AuthenticationForm()
    
    return render(request, 'users/login.html', {"form": form})

def logout_view(request):
    logout(request)
    return redirect('/')

def password_recovery(request):
    if request.method == "POST":
        form = PasswordRecoveryForm(request.POST)

        if form.is_valid():
            email = form.cleaned_data["email"]

            try:
                user = User.objects.get(email=email)

                # Generate random 6-digit code
                code = str(random.randint(100000, 999999))

                # Store in session with 1 minute expiry
                request.session['recovery_email'] = email
                request.session['recovery_code'] = code
                request.session['recovery_expiry'] = (
                    timezone.now() + timedelta(minutes=1)
                ).isoformat()

                # Send email with HTML formatting
                subject = 'Herbalyfe Password Recovery Code'

                text_content = f'''
                Your Herbalyfe recovery code is: {code}

                This code expires in 1 minute.
                '''

                html_content = f'''
                <p>Your Herbalyfe recovery code is:</p>

                <h2><b>{code}</b></h2>

                <p>This code expires in 1 minute.</p>
                '''

                email_message = EmailMultiAlternatives(
                    subject,
                    text_content,
                    None,
                    [email]
                )

                email_message.attach_alternative(html_content, "text/html")
                email_message.send()

                return redirect('users:verify_code')

            except User.DoesNotExist:
                messages.error(request, "❌ This email is not registered.")

    else:
        form = PasswordRecoveryForm()

    return render(request, "users/password_recovery.html", {"form": form})

def verify_code(request):
    email = request.session.get('recovery_email')
    stored_code = request.session.get('recovery_code')
    expiry = request.session.get('recovery_expiry')

    if not email or not stored_code or not expiry:
        return redirect('users:password_recovery')

    expiry_time = timezone.datetime.fromisoformat(expiry)

    # Expired code check
    if timezone.now() > expiry_time:
        messages.error(request, "❌ Recovery code expired.")
        return redirect('users:password_recovery')

    if request.method == "POST":

        # Resend code if user clicks "Resend Code" button
        if 'resend_code' in request.POST:

            new_code = str(random.randint(100000, 999999))

            request.session['recovery_code'] = new_code
            request.session['recovery_expiry'] = (
                timezone.now() + timedelta(minutes=1)
            ).isoformat()

            subject = 'Herbalyfe Password Recovery Code'

            text_content = f'''
            Your new Herbalyfe recovery code is: {new_code}

            This code expires in 1 minute.
            '''

            html_content = f'''
            <p>Your new Herbalyfe recovery code is:</p>

            <h2><b>{new_code}</b></h2>

            <p>This code expires in 1 minute.</p>
            '''

            email_message = EmailMultiAlternatives(
                subject,
                text_content,
                None,
                [email]
            )

            email_message.attach_alternative(html_content, "text/html")
            email_message.send()

            messages.success(request, "✅ New recovery code sent.")
            return redirect('users:verify_code')

        # Verify entered code against stored code
        form = VerificationCodeForm(request.POST)

        if form.is_valid():
            entered_code = form.cleaned_data['code']

            if entered_code == stored_code:
                request.session['verified_recovery'] = True
                return redirect('users:reset_password')

            else:
                messages.error(request, "❌ Invalid verification code.")

    else:
        form = VerificationCodeForm()

    return render(request, 'users/verify_code.html', {
        'form': form
    })

def reset_password_view(request):
    verified = request.session.get('verified_recovery')
    email = request.session.get('recovery_email')

    if not verified or not email:
        return redirect('users:password_recovery')

    try:
        user = User.objects.get(email=email)
    except User.DoesNotExist:
        return redirect('users:password_recovery')

    if request.method == "POST":
        form = ResetPasswordForm(user, request.POST)

        if form.is_valid():
            form.save()

            # Clear recovery session
            request.session.pop('recovery_email', None)
            request.session.pop('recovery_code', None)
            request.session.pop('recovery_expiry', None)
            request.session.pop('verified_recovery', None)

            messages.success(request, "✅ Password updated successfully.")
            return redirect('users:login')

    else:
        form = ResetPasswordForm(user)

    return render(request, 'users/reset_password.html', {
        'form': form
    })

@login_required
def profile_view(request):
    user = request.user
    profile = user.profile  # get the related Profile object

    if request.method == 'POST':
        if 'update_profile' in request.POST:
            profile_form = ProfileUpdateForm(request.POST, request.FILES, instance=user)
            password_form = CustomPasswordChangeForm(user)

            if profile_form.is_valid():
                user.username = profile_form.cleaned_data['username']
                user.email = profile_form.cleaned_data['email']
                user.save()

                avatar = profile_form.cleaned_data.get('avatar')
                if avatar:
                    profile.avatar = avatar
                    profile.save()

                messages.success(request, 'Profile updated successfully!')
                return redirect('users:profile')

        elif 'change_password' in request.POST:
            password_form = CustomPasswordChangeForm(user, request.POST)
            profile_form = ProfileUpdateForm(instance=user)

            if password_form.is_valid():
                password_form.save()
                update_session_auth_hash(request, user)
                messages.success(request, 'Password changed successfully!', extra_tags='password_success')
                return redirect('users:profile')

    else:
        profile_form = ProfileUpdateForm(
            initial={'username': user.username, 'email': user.email, 'avatar': profile.avatar}
        )
        password_form = CustomPasswordChangeForm(user)

    context = {
        'profile_form': profile_form,
        'password_form': password_form
    }
    return render(request, 'users/profile.html', context)
