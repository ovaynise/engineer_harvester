from constructions.models import (BrandType, Comment, Constructions,
                                  ConstructionsCompany, ConstructionsWorks,
                                  Location)
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.core.paginator import Paginator
from django.db.models import Count
from django.http import HttpResponseRedirect
from django.urls import reverse, reverse_lazy
from django.views.generic import (CreateView, DeleteView, DetailView, ListView,
                                  UpdateView)

from .forms import (BrandTypeForm, ConstructionsCompanyForm, ConstructionsForm,
                    ConstructionsWorksForm, LocationForm)


class OnlyAuthorMixin(UserPassesTestMixin):
    def test_func(self):
        object = self.get_object()
        return object.author == self.request.user


class OnlyAuthorAndAdminMixin(UserPassesTestMixin):
    def test_func(self):
        obj = self.get_object()
        user = self.request.user
        return obj.author == user or user.is_staff


class ConstructionsCompanyDetailView(LoginRequiredMixin, DetailView):
    model = ConstructionsCompany

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        return context


class ConstructionsDetailView(LoginRequiredMixin, DetailView):
    model = Constructions

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        current_construction = self.object
        all_companies = ConstructionsCompany.objects.filter(
            constructions_company=current_construction
        )
        constructions = Constructions.objects.all()
        comments_list = Comment.objects.filter(
            constructions=current_construction
        )
        works_list = ConstructionsWorks.objects.filter(
            constructions=current_construction
        )
        paginator_comments = Paginator(comments_list, 3)
        page_number_comments = self.request.GET.get("page_comments")
        page_obj_comments = paginator_comments.get_page(page_number_comments)
        paginator_works = Paginator(works_list, 10)
        page_number_works = self.request.GET.get("page_works")
        page_obj_works = paginator_works.get_page(page_number_works)

        context["all_companies"] = all_companies
        context["entity"] = "entities"
        context["constructions"] = constructions
        context["comments"] = page_obj_comments
        context["works"] = page_obj_works
        context["paginator_comments"] = paginator_comments
        context["paginator_works"] = paginator_works

        return context


class ConstructionsDeleteView(
    OnlyAuthorAndAdminMixin, LoginRequiredMixin, DeleteView
):
    model = Constructions
    success_url = reverse_lazy("constructions:constructions")


class ConstructionsUpdateView(
    OnlyAuthorAndAdminMixin, LoginRequiredMixin, UpdateView
):
    model = Constructions
    form_class = ConstructionsForm
    success_url = reverse_lazy("constructions:constructions")


class ConstructionsCreateView(LoginRequiredMixin, CreateView):
    model = Constructions
    form_class = ConstructionsForm
    success_url = reverse_lazy("constructions:constructions")

    def form_valid(self, form):
        form.instance.author = self.request.user
        return super().form_valid(form)

    def get_queryset(self):
        return Constructions.objects.all().order_by("created_at")


class СonstructionsListView(LoginRequiredMixin, ListView):
    model = Constructions
    ordering = "id"
    paginate_by = 10


class ConstructionsCompanyListView(LoginRequiredMixin, ListView):
    model = ConstructionsCompany
    ordering = "id"
    paginate_by = 10


class LocationListView(LoginRequiredMixin, ListView):
    model = Location
    ordering = "id"
    paginate_by = 10


class LocationCreateView(LoginRequiredMixin, CreateView):
    model = Location
    form_class = LocationForm
    success_url = reverse_lazy("constructions:location")

    def form_valid(self, form):
        form.instance.author = self.request.user
        return super().form_valid(form)

    def get_queryset(self):
        return Location.objects.annotate(
            constructions_count=Count("constructions")
        )


class BrandTypeListView(LoginRequiredMixin, ListView):
    model = BrandType
    ordering = "id"
    paginate_by = 10

    def get_queryset(self):
        return BrandType.objects.annotate(constructions_count=Count("brand"))


class BrandTypeCreateView(LoginRequiredMixin, CreateView):
    model = BrandType
    form_class = BrandTypeForm
    success_url = reverse_lazy("constructions:brandtype")

    def form_valid(self, form):
        form.instance.author = self.request.user
        return super().form_valid(form)

    def get_queryset(self):
        return BrandType.objects.all().order_by("created_at")


class ConstructionsCompanyDeleteView(
    OnlyAuthorMixin, LoginRequiredMixin, DeleteView
):
    model = ConstructionsCompany
    success_url = reverse_lazy("constructions:constructions_company")


class ConstructionsCompanyUpdateView(
    OnlyAuthorMixin, LoginRequiredMixin, UpdateView
):
    model = ConstructionsCompany
    form_class = ConstructionsCompanyForm
    success_url = reverse_lazy("constructions:constructions_company")


class ConstructionsCompanyCreateView(LoginRequiredMixin, CreateView):
    model = ConstructionsCompany
    form_class = ConstructionsCompanyForm
    success_url = reverse_lazy("constructions:constructions_company")

    def form_valid(self, form):
        form.instance.author = self.request.user
        return super().form_valid(form)

    def get_queryset(self):
        return ConstructionsCompany.objects.all().order_by("created_at")


class ConstructionsWorkCreateView(LoginRequiredMixin, CreateView):
    model = ConstructionsWorks
    form_class = ConstructionsWorksForm

    def form_valid(self, form):
        form.instance.author = self.request.user
        form.instance.constructions = self.get_constructions()
        self.object = form.save()
        return HttpResponseRedirect(self.get_success_url())

    def get_success_url(self):
        return reverse(
            "constructions:constructions_detail",
            kwargs={"pk": self.kwargs["pk"]},
        )

    def get_constructions(self):
        return Constructions.objects.get(id=self.kwargs["pk"])
