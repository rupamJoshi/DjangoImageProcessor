from django.db import models
class Member(models.Model):
	email_id=models.CharField(max_length=100)
	name=models.CharField(max_length=100)
	requested_at=models.DateTimeField('Requested at')
	uploaded_file=models.CharField(max_length=100)
	processing_time=models.IntegerField()
	action=models.CharField(max_length=200)
