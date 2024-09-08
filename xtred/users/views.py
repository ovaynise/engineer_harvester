from django.contrib.auth import get_user_model
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.http import Http404
from django.shortcuts import get_object_or_404
from django.urls import reverse_lazy
from django.views.generic import DetailView, ListView, UpdateView
from users.forms import CustomUserChangeForm
from users.models import TelegramUserModel

User = get_user_model()


class OnlyAuthorMixin(UserPassesTestMixin):
    def test_func(self):
        object = self.get_object()
        return object.author == self.request.user


class ProfileDetailView(DetailView):
    template_name = "users/profile.html"
    model = User
    slug_field = "username"
    slug_url_kwarg = "username"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        profile_username = self.kwargs.get("username")
        profile = get_object_or_404(User, username=profile_username)
        context["profile"] = profile
        return context


class ProfileUpdateView(LoginRequiredMixin, UpdateView):
    template_name = "users/user.html"
    model = User
    form_class = CustomUserChangeForm
    success_url = reverse_lazy("homepage:index")

    def get_object(self, queryset=None):
        user = self.request.user
        return get_object_or_404(User, pk=user.pk)


class UsersListView(LoginRequiredMixin, ListView):
    model = User
    ordering = "id"
    paginate_by = 10

    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_superuser:
            raise Http404("Page not found.")
        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["telegram_users"] = TelegramUserModel.objects.all()
        return context
