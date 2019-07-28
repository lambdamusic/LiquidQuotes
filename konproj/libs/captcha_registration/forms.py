from django import forms

from captcha_registration.recaptcha import fields as my_fields

from registration.forms import RegistrationForm

class RecaptchaRegistrationForm(RegistrationForm):
    recaptcha = my_fields.ReCaptchaField()