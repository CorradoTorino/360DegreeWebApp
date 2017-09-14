from django.shortcuts import render, get_object_or_404
from django.http import HttpResponse, HttpResponseRedirect
from django.contrib import messages 
from django.views.generic import ListView

from django.core.urlresolvers import reverse

from Degree360.forms import FeedbackProviderForm

from Degree360.models import FeedbackProvider, Survey

def workInProgress(request):
    return HttpResponse("Generic view for Degree360. Work in progress.")

def requestFeedback(request, pk):
    feedbackProviders = FeedbackProvider.objects.all()
    context = {
        'pk': pk,
        'feedbackProviders': feedbackProviders
        }
    
    return render(request, 'Degree360/requestFeedback.html', context)

def addFeedbackProvider(request, pk):
    template = 'Degree360/FeedbackProvider.html'
    
    if request.method == "POST":      
        form = FeedbackProviderForm(request.POST)
        if form.is_valid():
            feedbackProvider = form.save(commit=False)
            feedbackProvider.survey = Survey.objects.get(id=pk)
            feedbackProvider.save()
            return HttpResponseRedirect(reverse('Degree360:requestFeedback', args=(pk,)))
    else:
        form = FeedbackProviderForm()

    context = {
        'form':form,
         'pk':pk
         }
    
    return render(request, template, context)

def editFeedbackProvider(request, pk, email):   
    feedbackProvider = get_object_or_404(FeedbackProvider, survey=pk, email=email)  
    template = 'Degree360/FeedbackProvider.html'
    
    if request.method == "POST":      
        form = FeedbackProviderForm(request.POST, instance=feedbackProvider)
        if form.is_valid():
            feedbackProvider = form.save(commit=False)
            feedbackProvider.survey = Survey.objects.get(id=pk)
            feedbackProvider.save()
            return HttpResponseRedirect(reverse('Degree360:requestFeedback', args=(pk,)))
        else:
            messages.error(request, "Error")
    else:
        initial = {
            'name': feedbackProvider.name,
            'last_name': feedbackProvider.last_name,
            'email': feedbackProvider.email,
            'relation_type': feedbackProvider.relation_type
            }
        form = FeedbackProviderForm(initial)

    context = {
        'form':form,
         'pk':pk
         }
    
    return render(request, template, context)

class SurveyIndexView(ListView):
    template_name = 'Degree360/SurveyIndex.html'
    context_object_name = 'surveys_list'
    
    def get_queryset(self):
        return Survey.objects.all()


