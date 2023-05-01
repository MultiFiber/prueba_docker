from django.dispatch import receiver
from django_rest_passwordreset.signals import reset_password_token_created
from django.core.mail import EmailMultiAlternatives
from django.template.loader import get_template
from dotenv import load_dotenv
import os

@receiver(reset_password_token_created)
def password_reset_token_created(sender, instance, reset_password_token, *args, **kwargs):
    load_dotenv()
    host = os.getenv('HOST_PASSWORD_RESET')
    email = os.getenv('EMAIL_HOST_USER')
    email_plaintext_message = "{}?token={}".format(f'http://{host}/api/v1/password_reset/confirm/', reset_password_token.key)
    context = {'user': reset_password_token.user.name, 'link': email_plaintext_message}
    template = get_template('email.html').render(context)
    msg = EmailMultiAlternatives(
        # title:
        "Solicitud: Cambio de Contraseña {title}".format(title="BRÚJULA"),
        # message:
        None,
        # from:
        email,
        # to:
        [reset_password_token.user.email],
    )
    msg.attach_alternative(template, "text/html")
    msg.send(fail_silently=False)
    
