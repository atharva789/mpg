from django.contrib.auth.models import User
from rest_framework import serializers
from resources.models import Resource
from exam_packet.models import Packet
from assessment.models import Assessment

#ORM: python onjects that will automatically be converted to database operations
#serializer: allows us to convert objects to JSON

class UserSerializer(serializers.ModelSerializer):
  class Meta:
    model = User
    fields = ("id", "username", "email", "password",)
    extra_kwargs = {"password": {"write_only": True}}
  
  def create(self, validated_data):
    user = User.objects.create_user(**validated_data)
    return user
  
class ResourceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Resource
        fields = ("id", "title", "resource_pdf_file", "created_at", "resource_type", "user", "assessment")
        extra_kwargs = {
            "user": {"read_only": True},
            "assessment": {"required": True},
        }


class AssessmentPacketSerializer(serializers.ModelSerializer):
  class Meta:
      model = Packet
      fields = ("id", "pdf_file", "created_at", "user", "assessment")
      extra_kwargs = {
          "user": {"read_only": True},
          "assessment": {"required": True},
      }

class AssessmentSerializer(serializers.ModelSerializer):
    resources = ResourceSerializer(many=True, read_only=True)
    exam_packet = AssessmentPacketSerializer(read_only=True)

    class Meta:
        model = Assessment
        fields = ("id", "user", "title", "assessment_type", "created_at", "due_date", "resources", "exam_packet")
        extra_kwargs = {
            "user": {"read_only": True},
        }