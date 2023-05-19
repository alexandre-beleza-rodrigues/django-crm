from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path
from django.contrib.auth.views import LoginView, LogoutView

from leads.views import LandingPageView, SinupView

urlpatterns = [
    path("", LandingPageView.as_view(), name="landing-page"),
    path("admin/", admin.site.urls),
    path("signup/", SinupView.as_view(), name="signup"),
    path("login/", LoginView.as_view(), name="login"),
    path("logout/", LogoutView.as_view(), name="logout"),
    path("leads/", include("leads.urls", namespace="leads")),
    path("agents/", include("agents.urls", namespace="agents")),
]

if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
