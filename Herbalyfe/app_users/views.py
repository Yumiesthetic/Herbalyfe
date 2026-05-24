from django.shortcuts import render, redirect
from .forms import (
    CustomUserCreationForm,
    ProfileUpdateForm,
    CustomPasswordChangeForm,
    PasswordRecoveryForm,
    VerificationCodeForm,
    ResetPasswordForm,
    DeleteAccountForm,
)

from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth import (
    login,
    logout,
    update_session_auth_hash,
    authenticate
)

from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.contrib.auth.models import User

import random

from django.utils import timezone
from datetime import timedelta

from django.core.mail import EmailMultiAlternatives


# =========================================
# HELPER FUNCTION
# =========================================

def send_verification_email(email, code, subject_text):

    text_content = f'''
    Your Herbalyfe verification code is: {code}

    This code expires in 5 minutes.

    This email is automated. Please do not reply.

    If this is not coming from you, please ignore this email.
    '''

    html_content = f'''
    <p>Your Herbalyfe verification code is:</p>

    <h2><b>{code}</b></h2>

    <p>This code expires in 5 minutes.</p>

    <p>This email is automated. Please do not reply.</p>

    <p>If this is not coming from you, please ignore this email.</p>
    '''

    email_message = EmailMultiAlternatives(
        subject_text,
        text_content,
        None,
        [email]
    )

    email_message.attach_alternative(
        html_content,
        "text/html"
    )

    email_message.send()


# =========================================
# REGISTRATION
    # User fills registration form
    # DOES NOT create account yet
    # Stores temporary registration data in session
    # Sends 6-digit code
    # Verifies code
    # Then create the user
    # Then login
# =========================================

def register_view(request):
    
    if request.method == 'POST':

        form = CustomUserCreationForm(
            request.POST,
            request.FILES
        )

        if form.is_valid():

            code = str(
                random.randint(100000, 999999)
            )

            request.session['verification_type'] = (
                'register'
            )

            request.session['verification_email'] = (
                form.cleaned_data['email']
            )

            request.session['verification_code'] = code

            request.session['verification_expiry'] = (
                timezone.now() + timedelta(minutes=5)
            ).isoformat()

            request.session['register_data'] = {
                'username': form.cleaned_data['username'],
                'email': form.cleaned_data['email'],
                'password': form.cleaned_data['password1'],
            }

            request.session.modified = True

            avatar = request.FILES.get('avatar')

            if avatar:
                request.session['temp_avatar_bytes'] = (
                    avatar.read().hex()
                )

                request.session['temp_avatar_name'] = (
                    avatar.name
                )

                request.session.modified = True

            send_verification_email(
                form.cleaned_data['email'],
                code,
                'Herbalyfe Registration Verification'
            )

            return redirect('users:register_verify')

    else:
        form = CustomUserCreationForm()

    return render(
        request,
        'users/register.html',
        {
            'form': form
        }
    )


# =========================================
# LOGIN
# =========================================

def login_view(request):

    if request.method == "POST":

        form = AuthenticationForm(
            request,
            data=request.POST
        )

        if form.is_valid():

            login(
                request,
                form.get_user()
            )

            return redirect('/')

    else:
        form = AuthenticationForm()

    return render(request, 'users/login.html', {
        "form": form
    })


# =========================================
# LOGOUT
# =========================================

def logout_view(request):

    logout(request)

    return redirect('/')


# =========================================
# PASSWORD RECOVERY
# =========================================

def password_recovery(request):

    storage = messages.get_messages(request)

    for _ in storage:
        pass

    if request.method == "POST":

        form = PasswordRecoveryForm(request.POST)

        if form.is_valid():

            email = form.cleaned_data["email"]

            try:

                User.objects.get(email=email)

                code = str(
                    random.randint(100000, 999999)
                )

                request.session['verification_type'] = (
                    'password_reset'
                )

                request.session['verification_email'] = email

                request.session['verification_code'] = code

                request.session['verification_expiry'] = (
                    timezone.now() + timedelta(minutes=5)
                ).isoformat()

                request.session.modified = True

                send_verification_email(
                    email,
                    code,
                    'Herbalyfe Password Recovery'
                )

                return redirect('users:verify_code')

            except User.DoesNotExist:

                form.add_error(
                    'email',
                    '❌ This email is not registered.'
                )

    else:
        form = PasswordRecoveryForm()

    return render(
        request,
        "users/password_recovery.html",
        {"form": form}
    )


# =========================================
# VERIFY CODE
# =========================================

def verify_code(request):

    storage = messages.get_messages(request)

    for _ in storage:
        pass

    verification_type = request.session.get(
        'verification_type'
    )

    email = request.session.get(
        'verification_email'
    )

    stored_code = request.session.get(
        'verification_code'
    )

    expiry = request.session.get(
        'verification_expiry'
    )

    if not all([
        verification_type,
        email,
        stored_code,
        expiry
    ]):
        return redirect('/')

    expiry_time = timezone.datetime.fromisoformat(
        expiry
    )

    expired = timezone.now() > expiry_time

    if request.method == "POST":

        form = VerificationCodeForm(request.POST)

        if form.is_valid():

            entered_code = form.cleaned_data['code']

            if expired:

                if entered_code == stored_code:

                    form.add_error(
                        'code',
                        '❌ Verification code expired.'
                    )

                else:

                    form.add_error(
                        'code',
                        '❌ Invalid verification code.'
                    )

            elif entered_code == stored_code:

                # =================================
                # REGISTER FLOW
                # =================================

                if verification_type == 'register':

                    data = request.session.get(
                        'register_data'
                    )

                    user = User.objects.create_user(
                        username=data['username'],
                        email=data['email'],
                        password=data['password']
                    )

                    # Auto login after successful verification
                    login(request, user)

                    # Restore avatar
                    avatar_bytes = request.session.get(
                        'temp_avatar_bytes'
                    )

                    avatar_name = request.session.get(
                        'temp_avatar_name'
                    )

                    if avatar_bytes and avatar_name:

                        from django.core.files.base import ContentFile

                        avatar_file = ContentFile(
                            bytes.fromhex(avatar_bytes),
                            name=avatar_name
                        )

                        user.profile.avatar.save(
                            avatar_name,
                            avatar_file,
                            save=True
                        )

                    # Clear ONLY verification-related session data
                    for key in [
                        'verification_type',
                        'verification_email',
                        'verification_code',
                        'verification_expiry',
                        'register_data',
                        'temp_avatar_bytes',
                        'temp_avatar_name',
                    ]:
                        request.session.pop(key, None)

                    # Auto login AFTER cleanup
                    login(request, user)

                    return redirect('/')

                # =================================
                # PASSWORD RESET FLOW
                # =================================

                elif verification_type == 'password_reset':

                    request.session[
                        'verified_recovery'
                    ] = True

                    request.session.modified = True

                    return redirect(
                        'users:reset_password'
                    )

                # =================================
                # EMAIL CHANGE FLOW
                # =================================

                elif verification_type == 'change_email':

                    new_email = request.session.get(
                        'pending_new_email'
                    )

                    pending_username = request.session.get(
                        'pending_username'
                    )

                    request.user.email = new_email

                    if pending_username:
                        request.user.username = pending_username

                    request.user.save()

                    avatar_bytes = request.session.get(
                        'temp_avatar_bytes'
                    )

                    avatar_name = request.session.get(
                        'temp_avatar_name'
                    )

                    if avatar_bytes and avatar_name:

                        from django.core.files.base import ContentFile

                        avatar_file = ContentFile(
                            bytes.fromhex(avatar_bytes),
                            name=avatar_name
                        )

                        request.user.profile.avatar.save(
                            avatar_name,
                            avatar_file,
                            save=True
                        )

                    messages.success(
                        request,
                        'Email updated successfully!'
                    )

                    for key in [
                        'pending_new_email',
                        'pending_username',
                        'temp_avatar_bytes',
                        'temp_avatar_name',
                        'verification_type',
                        'verification_email',
                        'verification_code',
                        'verification_expiry'
                    ]:
                        request.session.pop(key, None)

                    return redirect('users:profile')

            else:

                form.add_error(
                    'code',
                    '❌ Invalid verification code.'
                )

    else:
        form = VerificationCodeForm()

    verification_message = (
        f"An email has been sent to {email}"
    )

    return render(
        request,
        'users/verify_code.html',
        {
            'form': form,
            'verification_message': verification_message
        }
    )


# =========================================
# RESET PASSWORD
# =========================================

def reset_password_view(request):

    verified = request.session.get(
        'verified_recovery'
    )

    email = request.session.get(
        'verification_email'
    )

    if not verified or not email:
        request.session.modified = True
        return redirect('/')

    try:
        user = User.objects.get(email=email)

    except User.DoesNotExist:
        return redirect('/')

    if request.method == "POST":

        form = ResetPasswordForm(
            user,
            request.POST
        )

        if form.is_valid():

            form.save()

            request.session.flush()

            messages.success(
                request,
                "✅ Password updated successfully."
            )

            return redirect('users:login')

    else:

        form = ResetPasswordForm(user)

    return render(
        request,
        'users/reset_password.html',
        {
            'form': form
        }
    )


# =========================================
# PROFILE
# =========================================

@login_required
def profile_view(request):

    storage = messages.get_messages(request)

    for _ in storage:
        pass

    user = request.user

    profile = user.profile

    if request.method == 'POST':

        if 'update_profile' in request.POST:

            # STORE ORIGINAL EMAIL BEFORE FORM VALIDATION
            original_email = User.objects.get(
                pk=user.pk
            ).email.strip().lower()

            profile_form = ProfileUpdateForm(
                request.POST,
                request.FILES,
                instance=user
            )

            password_form = (
                CustomPasswordChangeForm(user)
            )

            if profile_form.is_valid():

                new_email = profile_form.cleaned_data['email'].strip().lower()

                current_email = original_email

                if new_email != current_email:

                    request.session['pending_username'] = (
                        profile_form.cleaned_data['username']
                    )

                    avatar = request.FILES.get('avatar')

                    if avatar:

                        request.session['temp_avatar_bytes'] = (
                            avatar.read().hex()
                        )

                        request.session['temp_avatar_name'] = (
                            avatar.name
                        )

                    code = str(
                        random.randint(100000, 999999)
                    )

                    request.session['verification_type'] = (
                        'change_email'
                    )

                    request.session['verification_email'] = (
                        new_email
                    )

                    request.session['verification_code'] = code

                    request.session['verification_expiry'] = (
                        timezone.now() + timedelta(minutes=5)
                    ).isoformat()

                    request.session['pending_new_email'] = (
                        new_email
                    )

                    request.session.modified = True

                    send_verification_email(
                        new_email,
                        code,
                        'Herbalyfe Email Change Verification'
                    )

                    return redirect('users:change_email_verify')
                
                user.username = profile_form.cleaned_data['username']
                user.save()

                avatar = profile_form.cleaned_data.get(
                    'avatar'
                )

                if avatar:
                    profile.avatar = avatar
                    profile.save()

                messages.success(
                    request,
                    'Profile updated successfully!'
                )

                return redirect('users:profile')

        elif 'change_password' in request.POST:

            password_form = (
                CustomPasswordChangeForm(
                    user,
                    request.POST
                )
            )

            profile_form = ProfileUpdateForm(
                instance=user
            )

            if password_form.is_valid():

                password_form.save()

                update_session_auth_hash(
                    request,
                    user
                )

                messages.success(
                    request,
                    'Password changed successfully!',
                    extra_tags='password_success'
                )

                return redirect('users:profile')

    else:

        profile_form = ProfileUpdateForm(
            initial={
                'username': user.username,
                'email': user.email,
                'avatar': profile.avatar
            }
        )

        password_form = (
            CustomPasswordChangeForm(user)
        )

    return render(
        request,
        'users/profile.html',
        {
            'profile_form': profile_form,
            'password_form': password_form
        }
    )


# =========================================
# DELETE ACCOUNT STEP 1
# =========================================

@login_required
def delete_account_view(request):

    if request.method == 'POST':

        form = DeleteAccountForm(request.POST)

        if form.is_valid():

            password = form.cleaned_data['password']

            user = authenticate(
                request,
                username=request.user.username,
                password=password
            )

            if user is not None:

                request.session[
                    'delete_account_verified'
                ] = True

                request.session.modified = True

                return redirect(
                    'users:delete_account_final'
                )

            else:

                form.add_error(
                    'password',
                    'Incorrect password.'
                )

    else:

        form = DeleteAccountForm()

    return render(
        request,
        'users/delete_account.html',
        {
            'form': form
        }
    )


# =========================================
# DELETE ACCOUNT FINAL
# =========================================

@login_required
def delete_account_final_view(request):

    verified = request.session.get(
        'delete_account_verified'
    )

    if not verified:
        return redirect('users:delete_account')

    if request.method == 'POST':

        user = request.user

        logout(request)

        user.delete()

        request.session.flush()

        return redirect('/')

    return render(
        request,
        'users/delete_account_final.html'
    )