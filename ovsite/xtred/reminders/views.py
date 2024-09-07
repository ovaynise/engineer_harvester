from django.views.generic import ListView, CreateView, UpdateView, DeleteView
from django.urls import reverse_lazy
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import Http404

from reminders.models import Reminder
from .forms import ReminderForm


class RemindersDeleteView(LoginRequiredMixin,DeleteView):
    model = Reminder
    success_url = reverse_lazy('reminders:reminders')


class RemindersUpdateView(LoginRequiredMixin,UpdateView):
    model = Reminder
    form_class = ReminderForm
    success_url = reverse_lazy('reminders:reminders')


class RemindersCreateView(LoginRequiredMixin,CreateView):
    model = Reminder
    fields = '__all__'
    success_url = reverse_lazy('reminders:reminders')


class RemindersListView(LoginRequiredMixin,ListView):
    model = Reminder
    ordering = 'id'
    paginate_by = 10

    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_superuser:
            raise Http404("Page not found.")
        return super().dispatch(request, *args, **kwargs)
