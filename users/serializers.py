from allauth.account.adapter import get_adapter
from users.models import User, UserProfile
from dj_rest_auth.registration.serializers import RegisterSerializer
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework import serializers
from rest_framework.authtoken.models import Token
from users.tasks import login_notification_email
from companies.models import CompanyInvite, Company, CompanyEmployee

ORGANISATION_CHOICES = (
    ("JOIN", "JOIN"),
    ("CREATE", "CREATE"),
)


class CustomRegisterSerializer(RegisterSerializer):
    """
    Custom registration for the instasew user serializer
    this adds extra fields to the django default RegisterSerializer
    """

    first_name = serializers.CharField(max_length=150)
    last_name = serializers.CharField(max_length=150)
    mobile = serializers.CharField(max_length=150, required=False)
    company_name = serializers.CharField(max_length=150, required=False)
    organisation_choice = serializers.ChoiceField(choices=ORGANISATION_CHOICES)

    company_id = serializers.UUIDField(required=False)
    email = serializers.EmailField()
    password1 = serializers.CharField(write_only=True)
    password2 = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = (
            'first_name',
            'last_name',
            'email',
            'mobile',
            'company_name',
            'organisation_choice',
            'company_id',
            'password1',
            'password2',
        )

    def validate(self, attrs):
        if attrs.get('organisation_choice') == "JOIN":
            if not attrs.get('company_id'):
                raise serializers.ValidationError("You can't join an Organisation without the company_id ")
            if not CompanyInvite.objects.filter(company__id=attrs.get('company_id'), email=attrs.get("email")).exists():
                # Check if the user was sent an Invitation
                raise serializers.ValidationError(
                    "You were not sent an invite please request invite from company owner.")
        if attrs.get('organisation_choice') == "CREATE":
            if not attrs.get("company_name"):
                raise serializers.ValidationError("You need the company name if creating a company")
        return attrs

    def get_cleaned_data(self):
        """
        the default RegisterSerializer uses password1 and password2
        so  just get the data from password and  confirm_password and add it to the field for verification
        and also this enables us to pass extra data
        """
        super(CustomRegisterSerializer, self).get_cleaned_data()
        return {
            'first_name': self.validated_data.get('first_name', ''),
            'last_name': self.validated_data.get('last_name', ''),
            'email': self.validated_data.get('email', ''),
            'company_name': self.validated_data.get('company_name', ''),
            'organisation_choice': self.validated_data.get('organisation_choice', ''),
            'company_id': self.validated_data.get('company_id', ''),
            'mobile': self.validated_data.get('mobile', ''),
            'password1': self.validated_data.get('password1', ''),
            'password2': self.validated_data.get('password2', ''),
        }

    def save(self, request):
        """
        Due to adding extra fields to the user model we created an adapter
        in the users app to save the  user extra field
        """
        # using the custom adapter I created on the adapters.py in the users app
        adapter = get_adapter()
        user = adapter.new_user(request)
        self.cleaned_data = self.get_cleaned_data()
        adapter.save_user(request, user, self)
        ##############################
        # Create a company for the user or Join an Organisation base on what the user chose
        if self.cleaned_data.get("organisation_choice") == "JOIN":
            # Get the company invite through that we get company
            company_invite = CompanyInvite.objects.filter(
                email=self.cleaned_data.get("email"),
                company__id=self.cleaned_data.get("company_id")
            ).first()
            if not company_invite:
                # means an error might have occurred because we checked the above but i just have to delete the user
                user.delete()
                raise serializers.ValidationError("An error occurred please try signing in with the right values")
            company = company_invite.company
            if company_invite.role == "ADMIN":
                # Add the user to the admins
                CompanyEmployee.objects.create(user=user, company=company, status="ACTIVE", role="ADMIN")
                company_invite.status = "ACTIVE"
                company_invite.save()
            elif company_invite.role == "MARKETER":
                # Add the user to the marketer
                CompanyEmployee.objects.create(user=user, company=company, status="ACTIVE", role="MARKETER")
                company_invite.status = "ACTIVE"
                company_invite.save()
        if self.cleaned_data.get("organisation_choice") == "CREATE":
            company = Company.objects.create(
                owner=user,
                name=self.cleaned_data.get("company_name"))
        return user


class TokenSerializer(serializers.ModelSerializer):
    """
    In here I am checking if the user email has been verified before
    sending him his details
    """
    user = serializers.SerializerMethodField(read_only=True)
    access = serializers.SerializerMethodField(read_only=True)
    refresh = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = Token
        fields = ('access', 'refresh', 'user',)

    def get_access(self, obj):
        """
        This access token is a jwt token that get expired after a particular time given which could either be 1 hour
        """
        refresh = RefreshToken.for_user(obj.user)
        return str(refresh.access_token)

    def get_refresh(self, obj):
        """
        The refresh token gotten from  rest_framework_simplejwt.tokens
        :param obj: instance
        """
        refresh = RefreshToken.for_user(obj.user)
        return str(refresh)

    def get_user(self, obj):
        """
        it uses the custom serializer i created for authentication only so i just need this
        serializer method field to pass extra datas
        """
        try:
            print("the obj", obj)
            if obj.user.verified:
                #  send a mail to the user once he is authenticated to prevent issues if he isnt he owner of an accout
                #  using celery task to make it faster
                login_notification_email.delay(
                    obj.user.first_name, obj.user.email)

            return UserDetailSerializer(obj.user, read_only=True).data
        except Exception as a:
            # just for debugging purposes
            print('====================', a)
            return 'error'


class UserDetailSerializer(serializers.ModelSerializer):
    """
    This returns more detail about a user, and it is only used when the user
    logs in or register, and also in other serializers as user,freelancer and customer
    It is also used  when users login or register to get information
    """

    class Meta:
        model = User
        fields = [
            'id',
            'first_name',
            'last_name',
            'email',
            'verified',
            'is_staff',
            'last_login',
        ]
        extra_kwargs = {'password': {'write_only': True,
                                     'min_length': 4}}


class UserUpdateSerializer(serializers.ModelSerializer):
    """
    This serializer is meant to update a user which exists
    """
    first_name = serializers.CharField(max_length=250, required=False, allow_blank=False)
    last_name = serializers.CharField(max_length=250, required=False, allow_blank=False)
    email = serializers.EmailField(required=False, allow_blank=False)

    class Meta:
        model = User
        fields = [
            'first_name',
            'last_name',
            'email',
        ]

    def validate_email(self, obj):
        """This checks if the email has been used before and if it already exists by another user it raises an error
        and also the request is passed from the view to access the current user
        """
        logged_in_user = self.context['request'].user
        user = User.objects.filter(email=obj).first()
        if user:
            if logged_in_user.email != user.email:
                raise serializers.ValidationError(
                    'Please use a valid email that has not been used before')
        return obj


class VerifyEmailSerializer(serializers.Serializer):
    """
    This is used to verify the email address with otp of a user
    """
    otp = serializers.CharField(max_length=4)
    email = serializers.EmailField()


class UserProfileUpdateSerializer(serializers.ModelSerializer):
    """
    Used for updating a user profile
    """

    class Meta:
        model = UserProfile
        fields = [
            "gender",
            "date_of_birth",
            "profile_image",
            "address",
            "mobile",
            "description",
            "nationality",
            "country",
            "city",
        ]


class UserProfileDetailSerializer(serializers.ModelSerializer):
    """
    Used to returning more details of a user profile , and also with the image of the
    profile image we are also able to return that
    """
    user = UserDetailSerializer(read_only=True)

    class Meta:
        model = UserProfile
        fields = [
            "user",
            "gender",
            "date_of_birth",
            "profile_image",
            "address",
            "mobile",
            "description",
            "nationality",
            "country",
            "city",
        ]


class UserSerializer(serializers.ModelSerializer):
    """
    This returns little detail of the user which is currently used in blog post
    """

    class Meta:
        model = User
        fields = [
            'id',
            'first_name',
            'last_name',
        ]


class UserProfileSerializer(serializers.ModelSerializer):
    """
    Used to return minimum  detail of a user profile , and also with the image of the
    profile image we are also able to return that
    currently used in blog post and comments
    """
    user = UserSerializer(read_only=True)

    class Meta:
        model = UserProfile
        fields = [
            "user",
            "gender",
            "profile_image",
        ]

class ForgotPasswordOTPSerializer(serializers.Serializer):
    """
    Changing user password with otp only when user is not logged in  this means the user has forgotten his/her password
    so he would have request otp to his mail before sending the otp his new password and hs email
    used when user forgot password
    """
    otp = serializers.CharField(max_length=4)
    email = serializers.EmailField()
    password = serializers.CharField(max_length=100)


class ChangePasswordSerializer(serializers.Serializer):
    """
    changing user password when user is logged
    """
    old_password = serializers.CharField(max_length=100)
    new_password = serializers.CharField(max_length=100)
