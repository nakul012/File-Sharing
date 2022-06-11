from email.message import EmailMessage


from django.core.mail import EmailMessage
class Util:
    @staticmethod
    def send_email(data1):
        email=EmailMessage(subject=data1['email_subject'], body=data1['email_body'], to=[data1['to_email']] )
        email.send()