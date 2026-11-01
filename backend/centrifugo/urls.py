from django.urls import path
from .views import CentrifugoTokenView


urlpatterns = [
    path(
        'tokens/',
        CentrifugoTokenView.as_view(),
        name='centrifugo-tokens'
    ),
]