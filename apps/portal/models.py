from django.conf import settings
from django.db import models
from django.utils import timezone


class PersonalTask(models.Model):
    owner = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    title = models.CharField(max_length=200)
    notes = models.TextField(blank=True)
    due_date = models.DateField(null=True, blank=True)
    priority = models.CharField(max_length=10, choices=[('normal', 'Normal'), ('high', 'High'), ('low', 'Low')], default='normal')
    status = models.CharField(max_length=12, choices=[('todo', 'To do'), ('in_progress', 'In progress'), ('done', 'Completed')], default='todo')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = [models.F('due_date').asc(nulls_last=True), '-created_at']
        default_permissions = ()

    @property
    def is_overdue(self):
        return self.status != 'done' and self.due_date and self.due_date < timezone.localdate()


class PersonalPlan(models.Model):
    owner = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    notes = models.TextField(blank=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        default_permissions = ()
