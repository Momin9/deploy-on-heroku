# from todoproject.celery import app
# from django.core.mail import EmailMultiAlternatives
# from django.template.loader import render_to_string
# from todoproject import settings
#
#
# @app.task
# def send_password_reset_email(username, email, key):
#     context = {
#         'username': username,
#         'email': email,
#         'reset_password_token': "{}".format(key),
#     }
#     email_html_message = render_to_string('email/user_reset_password.html', context)
#     email_plaintext_message = render_to_string('email/user_reset_password.txt', context)
#     msg = EmailMultiAlternatives(
#         "Password Reset for {}".format(username),
#         email_plaintext_message,
#         "{}".format(settings.SERVER_EMAIL),
#         [email]
#     )
#     msg.attach_alternative(email_html_message, "text/html")
#     msg.send()
#     return True
