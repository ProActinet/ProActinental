from django.urls import path
from .views import GenerateLicenseKeyView, GetLicenseKeysView

urlpatterns = [
    path('generate/', GenerateLicenseKeyView.as_view(), name='generate-license-key'),
    path('list/', GetLicenseKeysView.as_view(), name='get-license-keys'),
]