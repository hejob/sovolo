from django.template.backends.django import Template
from django.template.loader import get_template
from django.core.mail import EmailMessage


def send_template_mail(template, context, from_address, to_addresses,
                       bcc_addresses=None):

    if not isinstance(template, Template):
        template = get_template(template)

    content = template.render(context)
    subject, body = content.split("\n", 1)

    email = EmailMessage(
        subject,
        body,
        from_address,
        to_addresses,
        bcc_addresses
    )
    email.send()
