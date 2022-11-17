from rest_framework import serializers

from careers.models import Job, Applicant, JobType, APPLICANT_STATUS_CHOICES
from django.core.validators import FileExtensionValidator

from users.validators import MaxSizeValidator


class JobCreateUpdateSerializer(serializers.ModelSerializer):
    """
    this serializers is meant to create job .
    Note before  creating a job it needs the company id and the user creating the job
    must be an admin or the owner
    """

    class Meta:
        model = Job
        fields = [
            "id",
            "job_category",
            "job_experience_level",
            "job_types",
            "applicants",
            "title",
            "description",
            "application_deadline",
            "timestamp",
        ]
        read_only_fields = ["timestamp", "id"]

    def create(self, validated_data):
        # the job_types are in this form job_types=[<job_types instance>, ...] which are the instances
        # of a category
        job_types = validated_data.pop('job_types')
        instance = Job.objects.create(**validated_data)
        for item in job_types:
            try:
                instance.job_types.add(item)
            except Exception as a:
                print(a)
        return instance


class JobTypeSerializer(serializers.ModelSerializer):
    """list of job """

    class Meta:
        model = JobType
        fields = "__all__"
        read_only_fields = ["id", "timestamp"]


class ApplicantSerializer(serializers.ModelSerializer):
    """
    this contains list of the applicants in a serialized format on a job detail
    I actually set the maximum file size for pdf to be 10
    """
    resume = serializers.FileField(validators=[FileExtensionValidator(['pdf'], MaxSizeValidator(10))])
    position = serializers.SerializerMethodField(read_only=True)
    job_id = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = Applicant
        fields = [
            "id",
            "job_id",
            "first_name",
            "last_name",
            "email",
            "status",
            "image",
            "nationality",
            "country_of_residence",
            "phone_number",
            "home_address",
            "position",
            "experience",
            "education",
            "linkedin",
            "website",
            "facebook",
            "twitter",
            "resume",
            "message",
            "timestamp",
        ]
        read_only_fields = ["status", "id", "timestamp", "job_id"]

    def get_position(self, obj):
        return str(obj.job_position)

    def get_job_id(self, obj):
        return str(obj.job_id)


class JobListDetailSerializer(serializers.ModelSerializer):
    """This contains list of jobs available"""
    applicants = ApplicantSerializer(read_only=True, many=True)
    applicants_counts = serializers.SerializerMethodField(read_only=True)
    job_types = JobTypeSerializer(read_only=True, many=True)

    class Meta:
        model = Job
        fields = [
            "id",
            "company_id",
            "title",
            "description",
            "application_deadline",
            "applicants",
            "applicants_counts",
            "job_category",
            "job_experience_level",
            "job_types",
            "timestamp",
        ]

    def get_applicants_counts(self, obj: Job):
        """return the total numbers of applicants"""
        return obj.applicant_counts


class ApplicantActionSerializer(serializers.Serializer):
    """This serializer is used to accept a job applications"""
    application_id = serializers.UUIDField()
    status = serializers.ChoiceField(choices=APPLICANT_STATUS_CHOICES)
