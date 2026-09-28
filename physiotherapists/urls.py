from django.urls import path
from .views import MyPhysiotherapistProfileView

app_name = "physiotherapists"


urlpatterns = [
    path("me/",MyPhysiotherapistProfileView.as_view(), name="me"),
]
