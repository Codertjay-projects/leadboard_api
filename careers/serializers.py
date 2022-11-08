from rest_framework import serializers

from careers.models import Job, Applicant, JobSchedule
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
            "job_schedules",
            "job_type",
            "title",
            "description",
            "timestamp",
        ]

    def create(self, validated_data):
        # the job_schedules are in this form job_schedules=[<job_schedules instance>, ...] which are the instances
        # of a category
        job_schedules = validated_data.pop('job_schedules')
        instance = Job.objects.create(**validated_data)
        for item in job_schedules:
            try:
                instance.job_schedules.add(item)
            except Exception as a:
                print(a)
        return instance


class JobScheduleSerializer(serializers.ModelSerializer):
    """list of job """

    class Meta:
        model = JobSchedule
        fields = "__all__"
        read_only_fields = ["id", "timestamp"]


class ApplicantSerializer(serializers.ModelSerializer):
    """
    this contains list of the applicants in a serialized format on a job detail
    I actually set the maximum file size for pdf to be 10
    """
    resume = serializers.FileField(validators=[FileExtensionValidator(['pdf'], MaxSizeValidator(10))])

    class Meta:
        model = Applicant
        fields = [
            "id",
            "first_name",
            "last_name",
            "email",
            "image",
            "nationality",
            "country_of_residence",
            "phone_number",
            "home_address",
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


class JobListDetailSerializer(serializers.ModelSerializer):
    """This contains list of jobs available"""
    applicants = ApplicantSerializer(read_only=True, many=True)
    applicants_counts = serializers.SerializerMethodField(read_only=True)
    job_schedules = JobScheduleSerializer(read_only=True, many=True)

    class Meta:
        model = Job
        fields = [
            "id",
            "company_id",
            "job_schedules",
            "job_type",
            "applicants_counts",
            "applicants",
            "title",
            "description",
            "timestamp",
        ]

    def get_applicants_counts(self, obj: Job):
        """return the total numbers of applicants"""
        return obj.applicant_counts


{
    "education": {
        "1": {
            "institution": "National open university",
            "institution_location": "Lagos nigeria",
            "mayor": "BSC",
            "degree": "BSC",
            "description": "the descript bla bla bla",
            "start_date": "3000-12-2",
            "end_date": "3000-12-6",
            "year": "3000-3004",
            "currently_school_here": "true"
        },
        "2": {
            "institution": "National open university",
            "institution_location": "Lagos nigeria",
            "mayor": "BSC",
            "degree": "BSC",
            "description": "the descript bla bla bla",
            "start_date": "3000-12-2",
            "end_date": "3000-12-6",
            "year": "3000-3004",
            "currently_school_here": "true"
        }
    },
    "experience": {
        "1": {
            "company_name": "Tech one",
            "company_location": "Tech one",
            "job_title": "Tech one",
            "description": "I implemented this that and those",
            "start_date": "3000-12-2",
            "end_date": "3000-12-6",
            "currently_work_here": "false"
        },
        "2": {
            "company_name": "Tech one",
            "company_location": "Tech one",
            "job_title": "Tech one",
            "description": "I implemented this that and those",
            "start_date": "3000-12-2",
            "end_date": "3000-12-6",
            "currently_work_here": "true"
        }
    }

}
