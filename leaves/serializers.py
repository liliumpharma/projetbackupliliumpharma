from rest_framework import serializers
from .models import *


def format_username(user):
    if not user:
        return "-"

    first_name = user.first_name if user.first_name else ""
    last_name = user.last_name if user.last_name else ""

    if not first_name and not last_name:
        return user.username

    return f"{first_name} {last_name}"


class LeaveTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = LeaveType
        fields = "__all__"


class LeaveSerializer(serializers.ModelSerializer):
    author = serializers.SerializerMethodField()
    approval_user = serializers.SerializerMethodField()
    leave_type = LeaveTypeSerializer()
    user = serializers.SerializerMethodField()
    observation = serializers.SerializerMethodField()
    user_job_name = serializers.CharField(source="user.userprofile.job_name")

    def get_user(self, obj):
        return format_username(obj.user)

    def get_approval_user(self, obj):
        return format_username(obj.approval_user)

    def get_observation(self, obj):
        return obj.observation

    def get_author(self, obj):
        return format_username(obj.author)

    class Meta:
        model = Leave
        fields = "__all__"
        depth = 1


class AbsenceSerializer(serializers.ModelSerializer):
    # Read Only Fields
    user_id = serializers.IntegerField(source="user.id")
    user = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = Absence
        fields = "__all__"
        extra_kwargs = {"absence_type": {"required": True}}
        depth = 1

    def get_user(self, obj):
        return format_username(obj.user)


class AbsenceTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = AbsenceType
        fields = "__all__"


class Serializer(serializers.Serializer):
    leaves = LeaveSerializer(many=True)
    absences = AbsenceSerializer(many=True)


# class LeaveAbsenceSerializer(serializers.ModelSerializer):
#     username=serializers.SerializerMethodField()

#     def get_username(self,obj):
#         return obj.user.first_name+" "+obj.user.last_name

#     class Meta:
#         model=LeaveAbsence
#         fields="__all__"
