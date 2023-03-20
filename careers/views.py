import uuid
import ast
from django.http import Http404
from django.utils import timezone
from rest_framework.filters import SearchFilter, OrderingFilter
from rest_framework.generics import CreateAPIView, ListAPIView
from rest_framework.generics import ListCreateAPIView, RetrieveUpdateDestroyAPIView
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.viewsets import ModelViewSet

from companies.models import Company
from companies.utils import check_admin_access_company
from email_logs.models import EmailLog
from users.permissions import NotLoggedInPermission, IsAuthenticatedOrReadOnly, LoggedInPermission
from users.utils import date_filter_queryset, is_valid_uuid
from .models import Job, Applicant
from .serializers import JobCreateUpdateSerializer, JobListDetailSerializer, ApplicantSerializer, \
    ApplicantActionSerializer, ApplicantEducationSerializer, ApplicantExperienceSerializer


class JobListCreateAPIView(ListCreateAPIView):
    """create a job post needs you to be authenticated and also be the owner or admin of the company"""
    permission_classes = [NotLoggedInPermission]
    serializer_class = JobListDetailSerializer
    queryset = Job.objects.all()
    filter_backends = [SearchFilter, OrderingFilter]
    search_fields = [
        "job_types",
        "title",
        "description",
    ]

    def get_queryset(self):
        # get the company we need
        company = self.get_company()
        job_category = self.request.query_params.get("job_category")
        if company and job_category:
            # if the company exists and also the job_category was passed
            queryset = self.filter_queryset(self.queryset.filter(company=company, job_category__icontains=job_category))
        elif job_category:
            # if only the job_category was passed
            queryset = self.filter_queryset(self.queryset.filter(job_category__icontains=job_category))
        elif company:
            # if only the company was passed
            queryset = self.filter_queryset(self.queryset.filter(company=company))
        else:
            queryset = self.filter_queryset(self.queryset.all())
        # Filter the date if it is passed in the params like
        # ?from_date=2222-12-12&to_date=2223-11-11 or the word ?seven_days=true or ...
        # You will get more from the documentation
        if queryset:
            queryset = date_filter_queryset(request=self.request, queryset=queryset)
        return queryset

    def get_company(self, *args, **kwargs):
        # the company id
        company_id = self.request.query_params.get("company_id")
        #  this filter base on the company id  provided
        if not company_id:
            return None
        company = Company.objects.filter(id=company_id).first()
        if not company:
            return None
        return company

    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = JobListDetailSerializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        serializer = JobListDetailSerializer(queryset, many=True)
        return Response(serializer.data)

    def create(self, request, *args, **kwargs):
        if not self.get_company():
            return Response({"error": "Company id required on params"}, status=400)
        if not self.request.user.is_authenticated:
            return Response({"error": "You are currently not authenticated"}, status=400)
        if not check_admin_access_company(self):
            return Response({"error": "You dont have permission to create a job under the company "}, status=401)
        serializer = JobCreateUpdateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save(company=self.get_company())
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=201, headers=headers)


class JobRetrieveUpdateDestroyAPIView(RetrieveUpdateDestroyAPIView):
    serializer_class = JobListDetailSerializer
    permission_classes = [NotLoggedInPermission]
    queryset = Job.objects.all()
    lookup_field = "id"

    def update(self, request, *args, **kwargs):
        instance = self.get_object()
        if not self.request.user.is_authenticated:
            return Response({"error": "You are currently not authenticated"}, status=401)
        if not check_admin_access_company(self):
            return Response({"error": "You dont have permission to create a job under the company "}, status=401)
        serializer = JobCreateUpdateSerializer(instance, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)
        return Response(serializer.data)

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        if not self.request.user.is_authenticated:
            return Response({"error": "You are currently not authenticated"}, status=401)
        if not check_admin_access_company(self):
            return Response({"error": "You dont have permission to delete a job under the company "}, status=401)
        instance.applicants.all().delete()
        instance.delete()
        return Response(status=204)


class JobApplyAPIView(CreateAPIView):
    """
    this view enables users to apply to a job post.
    it requires the id of the job post the user is applying to
    """
    serializer_class = ApplicantSerializer
    permission_classes = [NotLoggedInPermission]

    def get_job(self):
        """
        the job_id needs to be passed in the params and if it wasn't the user wont be added to the job applicants,
        but it just raises a 404 page
        :return:
        """
        job_id = self.request.query_params.get("job_id")
        if not job_id:
            raise Http404
        job = Job.objects.filter(id=job_id).first()
        if not job:
            raise Http404
        return job

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        if self.get_job().applicants.filter(email=serializer.validated_data.get("email")).exists():
            return Response(status=400, data={"error": "Already applied to this job post."})
        # Once saved it returns the applicants
        applicant = serializer.save(company=self.get_job().company, job=self.get_job())

        # Make sure the list is not stringify
        education_data = ast.literal_eval(self.request.data.get("education"))
        if isinstance(education_data,list):
            # Check if the instance is a list and also check the length below
            if len(education_data) >0:
                education_serializer = ApplicantEducationSerializer(data=education_data, many=True)
                education_serializer.is_valid(raise_exception=True)
                education_serializer.save(applicant=applicant, job=self.get_job())

        # Make sure the list is not stringify
        if isinstance(education_data,list):
            # Check if the instance is a list and also check the length below
            if len(education_data) >0:
                experience_data = ast.literal_eval(self.request.data.get("experience"))
                experience_serializer = ApplicantExperienceSerializer(data=experience_data, many=True)
                experience_serializer.is_valid(raise_exception=True)
                experience_serializer.save(applicant=applicant, job=self.get_job())
        return Response({"message": "Successfully applied to this job"}, status=200)


class JobApplicantListAPIView(ListAPIView):
    """
    this returns all applicants on a job posts using the job post id
    """
    queryset = Applicant.objects.all()
    serializer_class = ApplicantSerializer
    permission_classes = [LoggedInPermission]
    filter_backends = [SearchFilter, OrderingFilter]
    search_fields = [
        "first_name",
        "last_name",
        "status",
        "nationality",
        "home_address",
        "experience",
        "education",
        "message",
    ]

    def get_queryset(self):
        
        company_id = is_valid_uuid(self.request.query_params.get("company_id"))
        
        if company_id:
            # Check if the user has access
            if not check_admin_access_company(self):
                return Response({"error": "You dont have permission to delete a job under the company "}, status=401)
            else:
                return super().get_queryset().filter(company__id=company_id)
                
                # queryset = self.paginate_queryset(applicants)
                # serializer = self.serializer_class(applicants, many=True)
                # print(serializer)
                # return serializer.data
            
        else: raise Http404

    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)


class JobAcceptAPIView(APIView):
    """
    the is used to accept job applications or ignore decline job applications which was created by the organisation
    """
    permission_classes = [LoggedInPermission]

    def get_company(self):
        # the company id
        company_id = is_valid_uuid(self.request.headers["company_id"])
        #  this filter base on the company id  provided
        if not company_id:
            return None
        company = Company.objects.filter(id=company_id).first()
        if not company:
            return None
        return company

    def post(self, request, *args, **kwargs):
        serializer = ApplicantActionSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        # Check if the applicant
        
        application_id = is_valid_uuid(serializer.data['application_id'])
        applicant = Applicant.objects.filter(company=self.get_company(), id=application_id).first()

        if not applicant:
            return Response({"error": "Applicant does not exists"}, status=400)
        if applicant.status == serializer.validated_data.get("status"):
            return Response({"error": f"Applicant current status is {applicant.status}"}, status=400)
        if serializer.validated_data.get("status") == "INVITED":
            applicant.status = "INVITED"
            applicant.save()
            # Send accepted mail
            email_Log = EmailLog.objects.create(
                company=applicant.company,
                message_id=uuid.uuid4(),
                message_type="CAREER",
                email_from=applicant.company.name,
                email_to=applicant.email,
                reply_to=applicant.company.reply_to_email,
                email_subject=f"Accepted by {applicant.company.name}",
                description=f"""<h2>Hi {applicant.first_name} - {applicant.last_name}</h2>
                     <p> You have been accepted come for interview.""",
                scheduled_date=timezone.now()
            )

            return Response({"message": "Successfully sent invite to the applicant"}, status=200)
        elif serializer.validated_data.get("status") == "REJECTED":
            applicant.status = "REJECTED"
            applicant.save()
            # Send rejected mail
            email_Log = EmailLog.objects.create(
                company=applicant.company,
                message_id=uuid.uuid4(),
                message_type="CAREER",
                email_from=applicant.company.name,
                email_to=applicant.email,
                reply_to=applicant.company.reply_to_email,
                email_subject=f"Rejected by {applicant.company.name}",
                description=f"""<h2>Hi {applicant.first_name} - {applicant.last_name}</h2>
                                 <p> You have been Rejected dont  come for interview.""",
                scheduled_date=timezone.now()
            )
            return Response({"message": "Successfully sent rejection mail to the applicant"}, status=200)
        return Response({"error": "An unknown error occurred"}, status=400)
