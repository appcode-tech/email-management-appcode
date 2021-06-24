from django.db import models

# Create your models here.

class EmailLogsMaster(models.Model):
    email_log_id = models.AutoField(primary_key=True)
    email_sender = models.EmailField(null=True)
    email_receiver = models.TextField(null=True)
    email_subject = models.CharField(max_length=1000, null=True)
    email_body = models.TextField(null=True)
    email_timestamp = models.DateTimeField(null=True, auto_now_add=True)
    
    # Usually has count of emails delivered successfully
    email_result = models.CharField(max_length=255)
    # Specifies whether an email is sent to single or multiple users
    is_bulk_email = models.BooleanField(default=False)
    is_deleted = models.BooleanField(default=False)

class EmailAttachments(models.Model):
    email_attachment_id = models.AutoField(primary_key=True)
    email_log_id = models.ForeignKey(EmailLogsMaster, on_delete=models.CASCADE)
    attachment_name = models.TextField(null=True)
    email_file = models.FileField(upload_to='email_logs/attachments', null=True)