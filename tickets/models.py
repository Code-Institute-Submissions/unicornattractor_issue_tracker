from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone

# Create your models here.

class Ticket(models.Model):
    '''
    Enable user to submit a ticket with a choice of ticket type (bug or feature)
    Status choice - default status will be set to "Open" and admin will be able
    update it.
    Auto_now_add used to add date and time when ticket was created, and auto_now
    used to add date and time when ticket was updated / edited.
    '''
    
    TYPE_CHOICES = (
        ("Bug", "Bug"),
        ("Feature", "Feature"),
        )
    
    STATUS_CHOICES = (
        ("Open", "Open"),
        ("In Progress", "In Progress"),
        ("Completed", "Completed"),
        ("Closed", "Closed"),
        )
    
    user = models.ForeignKey(
        User, 
        null=True, 
        on_delete=models.CASCADE)
        
    ticket_type = models.CharField(
        max_length=7, 
        choices=TYPE_CHOICES)
        
    ticket_status = models.CharField(
        max_length=11, 
        choices=STATUS_CHOICES)
    
    subject = models.CharField(
        max_length=100,
        blank=False)
        
    description = models.TextField(
        max_length=3000,
        blank=False)
        
    date_created = models.DateTimeField(
        blank=False,
        null=False,
        auto_now_add=True)
        
    date_updated = models.DateTimeField(
        blank=False,
        null=False,
        auto_now=True,
        )
        
    class Meta:
        ordering = ['-id']
        
    def __str__(self):
        return "Ticket #{0} [{1}] {2} - {3}".format(
            self.id, self.ticket_status, self.ticket_type, self.subject)
        
    