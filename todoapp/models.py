# from django.db import models
#
#
# class Tasks(models.Model):
#     title = models.CharField(max_length=100)
#     description = models.TextField()
#     due_date = models.DateTimeField()
#     is_completed = models.BooleanField(default=False)
#     created = models.DateTimeField(auto_now_add=True, editable=False)
#     last_updated = models.DateTimeField(auto_now=True, editable=False)
#
#     def __str__(self):
#         return self.title
