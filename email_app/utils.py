import smtplib, requests
import urllib.request
from django.core import mail
from pathlib import Path

from django.conf import settings
import logging
from django.core import files
from io import BytesIO

from .models import *

# Get an instance of a logger
logger = logging.getLogger(__name__)

class EmailSender:
    '''
    This constructor accepts email header & footer, and a choice to save 
    email logs to database.
    '''
    def __init__(self, email_header=None, email_footer=None, email_logs=False):
        self.email_header = email_header
        self.email_footer = email_footer
        self.email_logs = email_logs

    def send_single_email(self, subject=None, body=None, receiver=None, attachmentType=None, file_list=[]):
        '''
        Sends an email to a single recipient
        EMAIL_HOST_USER: Host email sender to be defined in settings.py
        receiver: Email address of email recipient
        body: HTML Message
        attachmentType: Either from 'url' or 'filesystem'

        Email formatted as MIME type 'text/html'. Not compatible with very old clients.
        '''

        # Concat header & footer
        if self.email_header and self.email_footer:
            body = f"{self.email_header}<br><br>{body}<br><br><i>{self.email_footer}</i>"
            
        email_message = mail.EmailMessage(subject, body, settings.EMAIL_HOST_USER, [receiver])
        email_message.content_subtype = "html"

        if file_list:
            for fileURL in file_list:
                try:
                    # Create file object, read and attach to email_message object
                    if attachmentType.lower() == 'url':
                        fp = urllib.request.urlopen(fileURL)
                        file_name = fileURL.split("/")[-1]
                        email_message.attach(filename=file_name, content=fp.read())
                        fp.close()
                    elif attachmentType.lower() == 'filesystem':
                        path = Path(fileURL)
                        with path.open('rb') as file:
                            email_message.attach(filename=path.name, content=file.read())

                except Exception as e:
                    self.logEmailError(e)
                    return

        try:
            result = email_message.send()
            
            # Log the operation to database
            if self.email_logs:
                self.email_logger(
                    result=result, subject=subject, body=body, sender=settings.EMAIL_HOST_USER, receiver=receiver,
                    file_list=file_list, attachmentType=attachmentType
                )

            return result

        except smtplib.SMTPException as e:
            self.logEmailError(e)
            return
        except Exception as e:
            self.logEmailError(e)
            return


    def send_multiple_email(self, subject=None, body=None, receiver_list=[], attachmentType=None, file_list=[]):
        '''
        Sends same email to multiple recipients separately

        EMAIL_HOST_USER: Host email sender to be defined in settings.py
        receiver: List of email recipients (email addresses)
        body: HTML Message
        attachmentType: Either from 'url' or 'filesystem'

        Email formatted as MIME type 'text/html'. Not compatible with very old clients.
        
        Reference:
        https://docs.djangoproject.com/en/3.2/topics/email/#sending-multiple-emails
        https://docs.djangoproject.com/en/3.0/_modules/django/core/mail/
        '''

        # Manually open the connection
        try:
            connection = mail.get_connection()
            connection.open()
        except Exception as e:
            self.logEmailError(e)
            return

        # Concat header & footer
        body = f"{self.email_header}<br><br>{body}<br><br><i>{self.email_footer}</i>"

        messages = [
            # Build EmailMessage object * no. of recipients
            self.get_email_message_object(subject, body, settings.EMAIL_HOST_USER, [recipient], connection, attachmentType, file_list)
            for recipient in receiver_list
        ]
        
        # Send multiple emails in a single call
        try:
            result = connection.send_messages(messages)
            connection.close()

            # Log the operation to database
            if self.email_logs:
                self.email_logger(
                    result=result, subject=subject, body=body, sender=settings.EMAIL_HOST_USER, receiver=receiver_list, 
                    is_bulk_email=True, file_list=file_list
                )

            return result

        except smtplib.SMTPException as e:
            self.logEmailError(e)
            connection.close()
            return
            
        except Exception as e:
            self.logEmailError(e)
            connection.close()
            return


    # Helper functions
    def get_email_message_object(self, subject, message, sender, recipient, connection, attachmentType, file_list):
        email_message = mail.EmailMessage()

        # Override class attribute
        email_message.content_subtype = 'html'

        email_message.subject = subject
        email_message.body = message
        email_message.from_email = sender
        email_message.to = recipient
        email_message.connection = connection

        if file_list:
            for fileURL in file_list:
                try:
                    # Create file object, read and attach to message object
                    if attachmentType.lower() == 'url':
                        fp = urllib.request.urlopen(fileURL)
                        file_name = fileURL.split("/")[-1]
                        email_message.attach(filename=file_name, content=fp.read())
                        fp.close()
                    elif attachmentType.lower() == 'filesystem':
                        path = Path(fileURL)
                        with path.open('rb') as file:
                            email_message.attach(filename=path.name, content=file.read())

                except Exception as e:
                    self.logEmailError(e)
                    return
        
        return email_message

    def logEmailError(self, e):
        logger.error(f"Email sending failed, Exception: {e}")

    def email_logger(self, result=None, subject=None, body=None, sender=None, receiver=None, 
                    is_bulk_email=False, file_list=[], attachmentType=None):

        email_log_object = EmailLogsMaster.objects.create(
            email_sender = sender,
            email_receiver = receiver,
            email_subject = subject,
            email_body = body,
            is_bulk_email = is_bulk_email,
            email_result = result
        )

        for i in file_list:
            try:
                file_name = i.split("/")[-1]

                if attachmentType.lower() == 'url':
                    resp = requests.get(i)                    

                    fp = BytesIO()
                    fp.write(resp.content)
                    email_attachment_object = EmailAttachments.objects.create(
                        email_log_id = email_log_object,
                        email_file = files.File(fp, name=file_name)
                    )
                    email_attachment_object.save()

                elif attachmentType.lower() == 'filesystem':
                    
                    file_object = files.File(open(i, mode='rb'), name=file_name)
                    email_attachment_object = EmailAttachments.objects.create(
                        email_log_id = email_log_object,
                        email_file = file_object
                    )
                    email_attachment_object.save()

            except Exception as e:
                self.logEmailError(e)
                return
        
        email_log_object.save()