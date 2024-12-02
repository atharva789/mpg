from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse
from django.urls import reverse
from rest_framework import generics, status
from django.contrib.auth.models import User  # Import the User model
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.views import APIView
from .serializers import (
    UserSerializer,
    ResourceSerializer,
    AssessmentSerializer,
    AssessmentPacketSerializer,
)
from resources.models import Resource
from assessment.models import Assessment
from exam_packet.models import Packet


# User creation
class CreateUserView(generics.CreateAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [AllowAny]


# Assessment views
class AssessmentListCreate(generics.ListCreateAPIView):
    serializer_class = AssessmentSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Assessment.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        if serializer.is_valid():
            assessment = serializer.save(user=self.request.user)
            # Redirect to resource creation page after creating an assessment
            # redirect_url = reverse("resource-list-create", kwargs={"assessment_id": assessment.id})
            # self.response = redirect(redirect_url)
            print(f"Assessment {assessment.id} successfully created!")
            return assessment
        else:
            self.response = HttpResponse(serializer.errors, status=400)
            return None

    # def post(self, request, *args, **kwargs):
    #     super().post(request, *args, **kwargs)
    #     return self.response

class AssessmentGetUpdate(generics.RetrieveUpdateAPIView):
  serializer_class = AssessmentSerializer
  permission_classes = [IsAuthenticated]

  def get_queryset(self):
    return Assessment.objects.filter(user=self.request.user)
  

class AssessmentDelete(generics.DestroyAPIView):
    serializer_class = AssessmentSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Assessment.objects.filter(user=self.request.user)


# Packet views
# class PacketListCreate(generics.ListCreateAPIView):
#   serializer_class = AssessmentPacketSerializer
#   permission_classes = [IsAuthenticated]

#   def get_queryset(self):
#     assessment_id = self.request.data.get("assessment_id")
#     assessment = get_object_or_404(Assessment, id=assessment_id, user=self.request.user)
#     return Packet.objects.filter(user=self.request.user, assessment=assessment)

#   def perform_create(self, serializer):
#     assessment_id = self.request.data.get("assessment_id")
#     assessment = get_object_or_404(Assessment, id=assessment_id, user=self.request.user)

#     # Auto-fill packet details
#     packet = serializer.save(
#       user=self.request.user,
#       assessment=assessment,
#       # title=f"Packet for {assessment.title}",
#     )
#     # Add logic here to generate the actual exam packet if needed

#   def post(self, request, *args, **kwargs):
#     super().post(request, *args, **kwargs)
#     return HttpResponse("Packet generated successfully.", status=201)

class GeneratePacketView(generics.CreateAPIView):
    serializer_class = AssessmentPacketSerializer
    permission_classes = [IsAuthenticated]
      
    def post(self, request, assessment_id):
      # Retrieve the assessment, ensuring it belongs to the current user
      assessment = get_object_or_404(Assessment, id=assessment_id, user=request.user)
      packet, created = Packet.objects.get_or_create(user=request.user, assessment=assessment)
      
      if created:
        # Packet was just created
        # Perform any necessary initialization or PDF generation here
        packet = packet.save()
        serializer = AssessmentPacketSerializer(packet)
        return Response(serializer.data, status=status.HTTP_201_CREATED)
      else:
        # Packet already exists
        if packet.pdf_file == None:
          packet = packet.save()
        serializer = AssessmentPacketSerializer(packet)
        return Response(serializer.data, status=status.HTTP_200_OK)
      
    
class PacketDetailView(generics.RetrieveAPIView):
  serializer_class = AssessmentPacketSerializer
  permission_classes = [IsAuthenticated]

  def get_object(self):
      assessment_id = self.kwargs['assessment_id']
      assessment = get_object_or_404(Assessment, id=assessment_id, user=self.request.user)
      return get_object_or_404(Packet, assessment=assessment)

class PacketDelete(generics.DestroyAPIView):
    serializer_class = AssessmentPacketSerializer  # Fixed typo
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Packet.objects.filter(user=self.request.user)


# Resource views

from rest_framework.response import Response  # Import Response
from rest_framework import status  # Import status

class ResourceUploadView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, assessment_id):
        assessment = get_object_or_404(Assessment, id=assessment_id, user=request.user)

        # Handle syllabus upload
        syllabus_file = request.FILES.get("syllabus")
        if syllabus_file:
            Resource.objects.create(
                assessment=assessment,
                resource_pdf_file=syllabus_file,
                resource_type="syllabus",
                user=request.user,  # Ensure user is set
                title="syllabus",   # Provide a title
            )

        # Handle additional resource uploads
        resource_files = [f for key, f in request.FILES.items() if key.startswith("resources_")]
        for idx, file in enumerate(resource_files):
            Resource.objects.create(
                assessment=assessment,
                resource_pdf_file=file,
                resource_type="General",
                user=request.user,  # Ensure user is set
                title=f"Resource {idx + 1}",  # Provide a title
            )

        return Response({"message": "Resources uploaded successfully."}, status=status.HTTP_201_CREATED)

class ResourceListCreate(generics.ListCreateAPIView):
    serializer_class = ResourceSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        assessment_id = self.kwargs.get("assessment_id")
        return Resource.objects.filter(assessment__id=assessment_id, assessment__user=self.request.user)

    def perform_create(self, serializer):
        assessment_id = self.kwargs.get("assessment_id")
        assessment = get_object_or_404(Assessment, id=assessment_id, user=self.request.user)
        serializer.save(assessment=assessment)


class BulkResourceUploadView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, assessment_id):
        assessment = get_object_or_404(Assessment, id=assessment_id, user=request.user)
        resource_files = request.FILES.getlist("resource_files")

        for file in resource_files:
            Resource.objects.create(
                assessment=assessment,
                resource_pdf_file=file,
                resource_type="General",
            )

        return Response({"message": "Resources uploaded successfully."}, status=status.HTTP_201_CREATED)

class ResourceDelete(generics.DestroyAPIView):
    serializer_class = ResourceSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Resource.objects.filter(user=self.request.user)