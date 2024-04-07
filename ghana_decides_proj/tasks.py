from celery import shared_task
from django.core.mail import send_mail

@shared_task
def send_generic_email(subject, txt_, from_email, recipient_list, html_):
    send_mail(
        subject,
        txt_,
        from_email,
        recipient_list,
        html_message=html_,
        fail_silently=False,
    )


