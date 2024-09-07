from django.contrib import admin
from django.urls import include, path, reverse_lazy
from django.conf import settings
from django.views.generic.edit import CreateView
from django.conf.urls.static import static

from users.forms import CustomUserCreationForm


handler404 = 'core.views.page_not_found'

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('homepage.urls')),
    path('catalog/', include('catalog.urls')),
    path('constructions/', include('constructions.urls')),
    path('reminders/', include('reminders.urls')),
    path('about/', include('about.urls')),
    path('users/', include('users.urls')),
    path('api/', include('api.urls')),
    path('auth/', include('django.contrib.auth.urls')),

    path(
        'auth/registration/',
        CreateView.as_view(
            template_name='registration/registration_form.html',
            form_class=CustomUserCreationForm,
            success_url=reverse_lazy('homepage:index'),
        ),
        name='registration',
    ),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)


if settings.DEBUG:
    import debug_toolbar
    urlpatterns += (path('__debug__/', include(debug_toolbar.urls)),)
