from django.core.cache import cache
from django.db import models

# Create your models here.

GENDER_CHOICES = (
    ("MALE", "MALE"),
    ("FEMALE", "FEMALE"),
)


class EasyTaxUSSDState(models.Model):
    """list of state available"""
    name = models.CharField(max_length=250)
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.name}--{self.timestamp}"


class EasyTaxUSSDLGA(models.Model):
    """list of local government"""
    state = models.ForeignKey(EasyTaxUSSDState, on_delete=models.CASCADE)
    name = models.CharField(max_length=250)
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.name}--{self.timestamp}"


class EasyTaxUSSD(models.Model):
    """

    """
    lga = models.ForeignKey(EasyTaxUSSDLGA, on_delete=models.CASCADE, blank=True, null=True, )
    state = models.ForeignKey(EasyTaxUSSDState, on_delete=models.CASCADE, blank=True, null=True, )
    full_name = models.CharField(max_length=250, blank=True, null=True, )
    # Only the phone number us not blank true
    phone_number = models.CharField(max_length=50, unique=True)
    tax_payer_identification = models.CharField(max_length=250)
    balance = models.DecimalField(max_digits=100, decimal_places=2, blank=True, null=True, default=0)
    year_of_birth = models.CharField(blank=True, null=True, max_length=250)
    gender = models.CharField(max_length=10, blank=True, null=True, choices=GENDER_CHOICES)
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.full_name}"

    def get_last_command(self):
        """
        this get the last command made by the phone number on the api
        the command is like a step which tells us which process the user is currently on
        """
        last_command = cache.get(f"{self.phone_number}")
        return last_command

    def set_command(self, command):
        """
        this set the command and also a deadline for each phone_number and also deletes it if the
        command passes a deadline
        """
        #  set the cache to be deleted in 10 minutes from our cache system
        cache.set(f'{self.phone_number}', command, 600)
        return command

    def delete_command(self):
        delete_command = cache.delete(f"{self.phone_number}")
        return True

    def set_lga_range(self, from_range, to_range):
        """
        this is used to set the range from and to which the user uses in the local government last
        """
        #  set the cache to be deleted in 10 minutes from our cache system
        cache.set(f'{self.phone_number}_lga_range', f"{from_range}_{to_range}", 600)
        return [from_range, to_range]

    def get_lga_range(self):
        """
        this is used to get the lga range of the user which is he currently on
        """
        lga_range = cache.get(f"{self.phone_number}_lga_range")
        if lga_range:
            return lga_range.split("_")
        return None

    def set_state_range(self, from_range, to_range):
        """
        this is used to set the range from and to which the user uses in the local government last
        """
        #  set the cache to be deleted in 10 minutes from our cache system
        cache.set(f'{self.phone_number}_state_range', f"{from_range}_{to_range}", 600)
        return [from_range, to_range]

    def get_state_range(self):
        """
        this is used to get the lga range of the user which is he currently on
        """
        lga_range = cache.get(f"{self.phone_number}_state_range")
        if lga_range:
            return lga_range.split("_")
        return None
