from django.urls import path
from .views import (
    CreateUserView,
    AssessmentListCreate,
    AssessmentDelete,
    ResourceListCreate,
    ResourceDelete,
    #PacketListCreate,
    PacketDelete,
    GeneratePacketView,
    BulkResourceUploadView,
    ResourceUploadView,
    AssessmentGetUpdate,
    PacketDetailView,
    
)

urlpatterns = [
    # User registration
    path("users/create/", CreateUserView.as_view(), name="create-user"),

    # Assessment routes
    path("assessments/", AssessmentListCreate.as_view(), name="assessment-list-create"),
    path("assessments/<int:pk>/", AssessmentGetUpdate.as_view(), name="assessment-get-update"),
    path("assessments/<int:pk>/delete/", AssessmentDelete.as_view(), name="assessment-delete"),

    # Resource routes (requires assessment_id for context)
    path(
        "resources/<int:assessment_id>/",
        ResourceListCreate.as_view(),
        name="resource-list-create",
    ),
    path("resources/<int:assessment_id>/bulk/upload/", BulkResourceUploadView.as_view(), name="bulk-resource-upload"),
    path("resources/<int:assessment_id>/upload/", ResourceUploadView.as_view(), name="resource-upload"),
    path("resources/<int:pk>/delete/", ResourceDelete.as_view(), name="resource-delete"),

    # Packet routes
    path("packets/<int:assessment_id>/", PacketDetailView.as_view(), name="packet-list-create"),
    path("packets/<int:pk>/delete/", PacketDelete.as_view(), name="packet-delete"),
    path("assessments/<int:assessment_id>/generate-packet/", GeneratePacketView.as_view(), name="generate-packet"),
]