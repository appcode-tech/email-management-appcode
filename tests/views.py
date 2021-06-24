'''
Integration tests for user_management_app - views
'''
from django.views import View
from django.http import HttpResponse
from email_app.utils import *

# Create your views here.

class SendEmailTests(View):

    def get(self, request):        
        '''
        Note: 'result' contains number of successfully delivered email recipients
        '''
        
        subject = 'test'    
        email_body = "email body"

        # Init object
        email_sender_object = EmailSender(email_header='header', email_footer='footer', email_logs=False)

        # Send single email with single attachment
        result = email_sender_object.send_single_email(subject=subject, body=email_body, receiver='test@example.com', attachmentType='url', file_list=['https://file-examples-com.github.io/uploads/2017/10/file-example_PDF_500_kB.pdf', 'https://file-examples-com.github.io/uploads/2017/10/file-sample_150kB.pdf'])
        
        # Send single email with multiple attachment
        # result = email_sender_object.send_single_email(subject=subject, body=email_body, receiver='test2@example.com', attachmentType='url', file_list=['https://file-examples-com.github.io/uploads/2017/10/file-example_PDF_500_kB.pdf', 'https://file-examples-com.github.io/uploads/2017/10/file-sample_150kB.pdf'])

        # Send single email to multiple users
        # result = email_sender_object.send_multiple_email(subject=subject, body=email_body, receiver_list=['test@example.com', 'test2@example.com'], attachmentType='filesystem', file_list=['/home/username/email/file-example_PDF_500_kB.pdf'])

        return HttpResponse(result)