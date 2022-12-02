from rest_framework import serializers

from users.serializers import UserDetailSerializer
from .models import Feedback, ACTION_CHOICES


class FeedbackSerializer(serializers.ModelSerializer):
    """
    the list feed backs and also get the detail
    """
    staff = UserDetailSerializer(read_only=True)

    class Meta:
        model = Feedback
        fields = [
            "id",
            "staff",
            "next_schedule",
            "feedback",
            "action",
            "timestamp",
        ]
        read_only_fields = [
            "id", "staff", "timestamp",
        ]


class FeedbackCreateSerializer(serializers.Serializer):
    """
    the enables creating a feedback . YOu will notice i use different name for the field . that is because i need to
    prevent duplicate field since the serializer is used in other api views
    """
    feedback_content = serializers.CharField(max_length=20000)
    feedback_action = serializers.ChoiceField(choices=ACTION_CHOICES)
    feedback_next_schedule = serializers.DateField()
