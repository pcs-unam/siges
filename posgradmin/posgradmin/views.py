from django.views.generic import ListView
from django.views import View
from django.shortcuts import render
from posgradmin.models import Asunto
from posgradmin.forms import AsuntoEstudiantilForm


class MyView(View):

    form_class = AsuntoEstudiantilForm
    template_name = 'posgradmin/try.html'

    def get(self, request, *args, **kwargs):

        return render(request,
                      self.template_name,
                      {'form': self.form_class(),
                       'title': 'Asunto nuevo'})


class AsuntoList(ListView):
    model = Asunto
