from django.urls import path
from .views import (
    AdminPhysiotherapistDetailView,
    AdminPhysiotherapistListView,
    ApprovePhysiotherapistView,
    RejectPhysiotherapistView,
)

app_name = "administration"


urlpatterns = [
    path("physiotherapists/", AdminPhysiotherapistListView.as_view(), name="physiotherapist-list"),
    path("physiotherapists/<int:physiotherapist_id>/", AdminPhysiotherapistDetailView.as_view(), name="physiotherapist-detail"),
    path("physiotherapists/<int:physiotherapist_id>/approve/", ApprovePhysiotherapistView.as_view(), name="physiotherapist-approve"),
    path("physiotherapists/<int:physiotherapist_id>/reject/", RejectPhysiotherapistView.as_view(), name="physiotherapist-reject"),
]
