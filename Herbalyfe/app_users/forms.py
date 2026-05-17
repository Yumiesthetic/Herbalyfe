from django import forms
from django.contrib.auth.forms import UserCreationForm, PasswordChangeForm
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.core.validators import validate_email
from django.contrib.auth.password_validation import validate_password
from django.contrib.auth.validators import UnicodeUsernameValidator
from PIL import Image
from io import BytesIO
from django.core.files.uploadedfile import InMemoryUploadedFile
import sys, os
from django.contrib.auth.forms import SetPasswordForm

# Custom registration form with email and avatar
class CustomUserCreationForm(UserCreationForm):
    email = forms.EmailField(required=True, label="Email Address")
    avatar = forms.ImageField(
        required=False,
        label="Profile Picture",
        help_text="Upload a JPG or PNG image (max 10 MB, recommended size 300×300).",
    )

    class Meta:
        model = User
        fields = ['username', 'email', 'password1', 'password2', 'avatar']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['username'].widget.attrs.update({'autocomplete': 'new-username'})
        self.fields['email'].widget.attrs.update({'autocomplete': 'new-email'})
        self.fields['password1'].widget.attrs.update({'autocomplete': 'new-password'})
        self.fields['password2'].widget.attrs.update({'autocomplete': 'new-password'})
        self.fields['avatar'].widget.attrs.update({'accept': 'image/png,image/jpeg'})

    def clean_avatar(self):
        image = self.cleaned_data.get('avatar')

        if image:
            # Check file type
            ext = os.path.splitext(image.name)[1].lower()
            if ext not in ['.jpg', '.jpeg', '.png']:
                raise ValidationError("Only JPG and PNG files are allowed.")
            if ext in ['.jfif', '.pjpeg', '.pjp']:
                raise ValidationError("JFIF images are not allowed, only JPG and PNG.")

            # Check file size (10 MB)
            if image.size > 10 * 1024 * 1024:
                raise ValidationError("Image size must be under 10 MB.")

            # Auto-resize if image is too large
            img = Image.open(image)
            if img.height > 300 or img.width > 300:
                img = img.convert("RGB")
                img.thumbnail((300, 300))

                buffer = BytesIO()
                img.save(buffer, format="JPEG", quality=90)
                buffer.seek(0)

                image = InMemoryUploadedFile(
                    buffer,
                    'ImageField',
                    image.name,
                    'image/jpeg',
                    sys.getsizeof(buffer),
                    None
                )
        return image
    
    def clean_email(self):
        email = self.cleaned_data.get('email')

        if User.objects.filter(email=email).exists():
            raise ValidationError(
                "This email is already registered."
            )

        return email

# Update username, email, and avatar
class ProfileUpdateForm(forms.ModelForm):
    avatar = forms.ImageField(
        required=False, label="Change Avatar", 
        widget=forms.FileInput  # use simple file input instead of ClearableFileInput
    )
    username = forms.CharField(
        max_length=20,
        min_length=3,
        validators=[UnicodeUsernameValidator()]
    )
    email = forms.EmailField()

    class Meta:
        model = User
        fields = ['username', 'email', 'avatar']

    def clean_username(self):
        username = self.cleaned_data.get('username')
        if User.objects.filter(username=username).exclude(pk=self.instance.pk).exists():
            raise ValidationError("This username is already taken.")
        return username

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if User.objects.filter(email=email).exclude(pk=self.instance.pk).exists():
            raise ValidationError("This email is already registered.")
        return email

# Change password with old/new confirmation and proper password validation
class CustomPasswordChangeForm(PasswordChangeForm):
    old_password = forms.CharField(widget=forms.PasswordInput(attrs={'autocomplete': 'current-password'}))
    new_password1 = forms.CharField(widget=forms.PasswordInput(attrs={'autocomplete': 'new-password'}))
    new_password2 = forms.CharField(widget=forms.PasswordInput(attrs={'autocomplete': 'new-password'}))

    # Ensure new password uses Django's built-in password validation
    def clean_new_password1(self):
        password1 = self.cleaned_data.get('new_password1')
        validate_password(password1, self.user)  # runs built-in validators
        return password1

# Password recovery form to request password reset link via email
class PasswordRecoveryForm(forms.Form):
    email = forms.EmailField(
        required=True,
        label="Email Address",
        widget=forms.EmailInput(attrs={
            "placeholder": "Enter your registered email",
            "autocomplete": "off"
        })
    )

# Verification form
class VerificationCodeForm(forms.Form):
    code = forms.CharField(
        max_length=6,
        min_length=6,
        widget=forms.TextInput(attrs={
            'placeholder': 'Enter 6-digit code',
            'autocomplete': 'off'
        })
    )

# Reset password form
class ResetPasswordForm(SetPasswordForm):
    pass


# Delete account confirmation form
class DeleteAccountForm(forms.Form):
    password = forms.CharField(
        label="Confirm Password",
        widget=forms.PasswordInput(attrs={
            'autocomplete': 'current-password',
            'placeholder': 'Enter your password'
        })
    )

# Email change verification form
class EmailChangeForm(forms.Form):
    new_email = forms.EmailField(
        label="New Email Address",
        widget=forms.EmailInput(attrs={
            'autocomplete': 'off',
            'placeholder': 'Enter new email'
        })
    )

    def clean_new_email(self):
        email = self.cleaned_data.get('new_email')

        if User.objects.filter(email=email).exists():
            raise ValidationError(
                "This email is already registered."
            )

        return email