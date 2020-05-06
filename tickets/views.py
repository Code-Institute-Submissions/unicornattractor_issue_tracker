from django.shortcuts import render, redirect, reverse, get_object_or_404
from django.utils import timezone
from django.contrib import auth, messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from tickets.models import Ticket, Upvote, Donation, Comment
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from tickets.forms import AddTicketForm, PaymentForm, DonationForm, AddCommentForm
from django.db.models import Count, Sum
from django.conf import settings
import stripe

# Create your views here.

# Import the Stripe secret API key
stripe.api_key = settings.STRIPE_SECRET

@login_required
def add_or_edit_ticket(request, pk=None):
    '''
    Allows user to add a new ticket or edit an existing one
    If user wants to add a new ticket he or she is redirected to a blank
    add_ticket_form where all details can be supplied and submitted
    If user wants to edit the ticket they are redirected to the ticket form
    that is pre-filled with ticket details
    '''
    
    # Retrive the ticket if exists
    ticket = get_object_or_404(Ticket, pk=pk) if pk else None
    
    if request.method == "POST":
        add_ticket_form = AddTicketForm(request.POST, request.FILES, instance=ticket)

        if add_ticket_form.is_valid():
            add_ticket_form.instance.user = request.user
            add_ticket_form.instance.ticket_status = "Open"
            add_ticket_form.save()
            messages.success(request, "You have successfully submitted your \
                                ticket!")
            return redirect('all_tickets')
        else:
                messages.error(request, "Something went wrong. Please try again.")
            
    else:
        add_ticket_form = AddTicketForm(instance=ticket)
    
    return render(request, 'add_ticket.html', {'add_ticket_form': add_ticket_form} )
  
def all_tickets(request):
    '''
    View all tickets in a form of paginated table.
    Enable user to filter tickets by type and / or status
    Table is paginated to show only 10 records per page
    '''
    
    # Create type and status list for select option menu
    types_list = Ticket.objects.order_by().values_list('ticket_type',
                    flat=True).distinct()
    status_list = Ticket.objects.order_by().values_list('ticket_status',
                    flat=True).distinct()
    
    qs = Ticket.objects.all()
    
    # Queries
    type_filter_query = request.GET.get('ticket-type')
    status_filter_query = request.GET.get('ticket-status')
    
    # Filter queryset
    if type_filter_query and type_filter_query != "Select...":
        if status_filter_query and status_filter_query != "Select...":
           qs = qs.filter(ticket_type__iexact = type_filter_query,
           ticket_status__iexact = status_filter_query).order_by('ticket_type')
        else:
            qs = qs.filter(ticket_type__iexact = type_filter_query)
    elif status_filter_query and status_filter_query != "Select...":
        qs = qs.filter(ticket_status__iexact = status_filter_query)
    else:
        qs
    
    page = request.GET.get('page', 1)
    
    # Paginate tickets
    paginator = Paginator(qs, 10)
    try:
        tickets = paginator.page(page)
    except PageNotAnInteger:
        tickets = paginator.page(1)
    except EmptyPage:
        tickets = paginator.page(paginator.num_pages)
        
    args = {'tickets': tickets, 
            'types_list': types_list, 
            'status_list': status_list }
        
    return render(request, 'all_tickets.html', args )

def view_ticket(request, pk):
    '''
    Enables user to view page containing all details regarding a selected ticket
    Function retrieves a single ticket based on its ID (pk) and renders it to 
    the view_ticket.html template
    If object is not found 404 error is being returned
    '''
    
    # Retrive the ticket
    ticket = get_object_or_404(Ticket, pk=pk)
    
    # Allows to retrive forms on the view ticket page
    donation_form = DonationForm()
    payment_form = PaymentForm()
    comment_form = AddCommentForm()
    
    # Check if user upvoted ticket
    try:
        has_voted = Upvote.objects.get(user=request.user, ticket=ticket)
    except Upvote.DoesNotExist:
        has_voted = None
    
    # Check if user donated money for the feature
    try:
        has_donated = Donation.objects.get(user=request.user, ticket=ticket)
    except Donation.DoesNotExist:
        has_donated = None
    
    # Count all upvotes for a ticket
    upvote_count = Upvote.objects.filter(ticket=ticket).count()
    
    # Get a sum of donations for a given ticket
    total_donations = Donation.objects.filter(ticket=ticket
                    ).aggregate(Sum('donation_amount'))['donation_amount__sum']
    
    if total_donations is None:
        total_donations = 0
    else:
        total_donations
    
    # Retrive all comments for a given ticket
    try:
        comments = Comment.objects.filter(ticket_id=ticket.pk)
    except Comment.DoesNotExist:
        comments = None
    
    args = {
        'ticket': ticket, 
        'donation_form': donation_form, 
        'payment_form': payment_form,
        'has_voted': has_voted,
        'has_donated': has_donated,
        'upvote_count': upvote_count,
        'total_donations': total_donations,
        'comments': comments,
        'comment_form': comment_form
    }
    
    return render(request, 'view_ticket.html', args)

@login_required
def delete_ticket(request, pk):
    '''
    Allows user to delete their ticket
    '''
    
    ticket = get_object_or_404(Ticket, pk=pk)
    author= ticket.user
    
    if request.user.is_authenticated and request.user == author:
            ticket.delete()
            messages.success(request, "Ticket successfully deleted!")
            return redirect(reverse('all_tickets'))

@login_required
def upvote(request, pk):
    '''
    Allows user to upvote the ticket and donate (for features only)
    If user upvoted already they won't be allowed to vote again
    Also if user upvoted and donated for the feature they won't be allowed to 
    downvote and upvote ticket again for the saem ticket, so function will check
    it by using has_voted and has_donated
    Stripe API used to charge a user's credit card
    '''
    
    ticket = get_object_or_404(Ticket, pk=pk)
    
    # Check if user upvoted ticket
    try:
        has_voted = Upvote.objects.get(user=request.user, ticket=ticket)
    except Upvote.DoesNotExist:
        has_voted = None
        
    # Check if user donated money for the feature
    try:
        has_donated = Donation.objects.get(user=request.user, ticket=ticket)
    except Donation.DoesNotExist:
        has_donated = None
    
    if has_voted is None and (ticket.ticket_type == "Bug" or has_donated is not None):
       Upvote.objects.create(ticket_id=ticket.pk, user_id=request.user.id) 
       messages.success(request, "Your have successfully upvoted the ticket!")
       return redirect('view_ticket', pk)
    
    if has_voted is None and has_donated is None and request.method == "POST":
        payment_form = PaymentForm(request.POST)
        donation_form = DonationForm(request.POST)
        
        if payment_form.is_valid() and donation_form.is_valid():
            
            # Amount donated
            donation_amount = int(request.POST.get("donation_amount"))
            
            try:
                # Charge customer using Stripe API
                customer = stripe.Charge.create(
                    amount=int(donation_amount * 100),
                    currency="EUR",
                    description=request.user.email,
                    card = payment_form.cleaned_data['stripe_id'],
                )
            except stripe.error.CardError:
                # If card is declined display the error message
                messages.error(request, "Your card was declined!")
            
            # Payment was successful
            if customer.paid:
                donation_form.instance.user = request.user
                donation_form.instance.donation_amount = donation_amount
                donation_form.instance.ticket = ticket
                donation_form.save()
                
                # Create an upvote for the feature
                Upvote.objects.create(ticket_id=ticket.pk,
                                        user_id=request.user.id)
                
                messages.success(request, "Your have successfully donated!")
                return redirect('view_ticket', pk)
                
            # If payment didn't go through
            else:
                messages.error(request, "Unable to process the payment.")
        
        # Forms not valid
        else:
            messages.error(request, "We were unable to take a payment with that card!")
    else:
        payment_form = PaymentForm()
        donation_form = DonationForm()
    
    args = {
        'ticket': ticket,
        'donation_form': donation_form,
        'payment_form': payment_form,
        'publishable': settings.STRIPE_PUBLISHABLE
    }
    
    return render(request, 'view_ticket.html', args)

@login_required
def downvote(request, pk):
    
    ticket = get_object_or_404(Ticket, pk=pk)
    
    # Check if user upvoted ticket
    try:
        has_voted = Upvote.objects.get(user=request.user, ticket=ticket)
    except Upvote.DoesNotExist:
        has_voted = None
    
    if request.user.is_authenticated and has_voted is not None:
        upvote = Upvote.objects.get(ticket_id=ticket.pk,
                                        user_id=request.user.id)
        upvote.delete()
        messages.success(request, "Your upvote has been removed!")
        return redirect('view_ticket', pk)

@login_required
def add_or_edit_comment(request, ticket_pk, pk=None):
    
    # Retrive the comment and ticket if exists
    ticket = get_object_or_404(Ticket, pk=ticket_pk)
    comment = get_object_or_404(Comment, pk=pk) if pk else None

    if request.method == "POST":
        comment_form = AddCommentForm(request.POST, request.FILES, instance=comment)

        if comment_form.is_valid():
            comment_form.instance.user = request.user
            comment_form.instance.ticket = ticket
            comment_form.save()
            messages.success(request, "Thanks for sharing your thoughts!")
            return redirect('view_ticket', ticket.pk)
        else:
            messages.error(request, "Something went wrong. Please try again.")
            
    else:
        comment_form = AddCommentForm(instance=comment)
    
    args = {
        'comment_form': comment_form
    }
    
    return render(request, 'view_ticket.html', args )