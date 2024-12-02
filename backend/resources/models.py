from django.db import models
from django.contrib.auth.models import User
from enum import Enum
from assessment.models import Assessment


class ResourceType(Enum):
    SYLLABUS = "syllabus"
    SLIDES = "slides"
    WRITTEN_NOTE = "handwritten note"
    TEXTBOOK = "textbook"
    PRACTICE_EXAM = "past exam"


class Resource(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    assessment = models.ForeignKey(Assessment, on_delete=models.CASCADE, related_name="resources")
    resource_type = models.CharField(
        max_length=50,
        choices=[(member.value, member.value) for member in ResourceType]
    )
    title = models.CharField(max_length=255)
    is_scanned = models.BooleanField(default=False)
    resource_pdf_file = models.FileField(upload_to="resources/")
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.title} ({self.resource_type})"