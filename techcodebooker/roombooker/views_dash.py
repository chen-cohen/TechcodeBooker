from .models import Rooms, Bookings, Companies
from django.http import HttpResponse
from django.shortcuts import render, redirect
import json, datetime
from .forms import CompanyForm, RoomForm, BookingForm
from django.contrib.auth.decorators import login_required

models = {'rooms': Rooms, 'bookings': Bookings, 'companies': Companies}

# Associated url: /booker/dashboard
# Displays the index page of the community manager dashboard.
@login_required
def index(request):
    bookings = Bookings.objects.filter(status=True).order_by('-date')
    context = {'bookings': bookings}
    return render(request, 'communitymanager/index.html', context)

#Retrieves relevant querysets of models used in the dashboard.
def get_model(model):
    current_date = datetime.date.today()
    models = {}
    models['rooms'] = Rooms.objects.all()
    models['companies'] = Companies.objects.all()
    models['bookings'] = Bookings.objects.filter(date__gte=current_date).order_by('-date')
    return models[model]

#Retrieves modelform subclasses to be used in the updating and creation views for models in the dashboard.
def get_modelform(model):
    modelforms = {}
    modelforms['rooms'] = RoomForm
    modelforms['companies'] = CompanyForm
    modelforms['bookings'] = BookingForm
    return modelforms[model]

# Associated url: booker/dashboard/MODEL NAME(companies,bookings,or rooms)
# Returns the template depending on the value of the "model" argument passed from the url.
@login_required
def show_model(request, model):
    render_model = get_model(model)
    context = {model: render_model}
    url = 'communitymanager/{}.html'.format(model)
    return render(request, url, context)

# View linked to ajax request. Handles user action on pending bookings which are displayed in the index.
def pendingaction(request):
    action = request.GET.get('action')
    id = int(request.GET.get('id'))
    booking = Bookings.objects.get(pk=id)
    msg = {}
    if action == 'delete':
        booking.delete()
        msg['msg'] = "Pending booking was deleted."
    else:
        booking.status = False
        booking.save()
        msg['msg'] = "Pending booking was approved."
    return HttpResponse(json.dumps(msg), content_type='application/json')

# Associated url: booker/dashboard/MODEL NAME/ID
# View for rendering model editing forms.
@login_required
def edit_instance(request, model, id):
    instance = models[model].objects.get(pk=id)
    ModForm = get_modelform(model)
    url = '/booker/dashboard/{}'.format(model)
    if request.method == 'POST':
        if request.POST.get('delete'):
            instance.delete()
            return redirect(url)
        request_args = [request.POST]
        if model == 'rooms':
            request_args.append(request.FILES)
        form = ModForm(*request_args, instance=instance)
        if form.is_valid():
            form.save()
            return redirect(url)
    else:
        form = ModForm(instance=instance)
        return render(request, 'communitymanager/edit_form.html', {'form': form,'title':model})

# Associated url: booker/dashboard/MODEL NAME/new
# View for rendering forms for new models.
@login_required
def new_instance(request, model):
    ModForm = get_modelform(model)
    if request.method == "POST":
        request_args = [request.POST]
        if model == 'rooms':
            request_args.append(request.FILES)
        form = ModForm(*request_args)
        if form.is_valid():
            form.save()
            url = '/booker/dashboard/{}'.format(model)
            return redirect(url)
    else:
        form = ModForm()
    return render(request, 'communitymanager/edit_form.html', {'form': form, 'new': True, 'title':model})
