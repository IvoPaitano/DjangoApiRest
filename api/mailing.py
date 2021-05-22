from django.contrib.sites.shortcuts import get_current_site
from django.shortcuts import render
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode
from django.core.mail import EmailMultiAlternatives
from django.template.loader import get_template
from django.contrib.auth.tokens import default_token_generator

def send_confirmation_email(user, request):
    current_site = get_current_site(request)
    plaintext = get_template('emailVerify.txt')
    html_template = get_template('emailVerify.html')
    data = {
        'user': user,
        'domain': current_site.domain,
        'uid': urlsafe_base64_encode(force_bytes(user.pk)),
        'token': default_token_generator.make_token(user),  # Genera el token
    }
    text_content = plaintext.render(data)
    html_content = html_template.render(data)
    mail_subject = 'Verificá tu Cuenta'
    msg = EmailMultiAlternatives(mail_subject, text_content, to=[user.email])
    msg.attach_alternative(html_content, "text/html")
    msg.send()