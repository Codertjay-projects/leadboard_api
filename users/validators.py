from django.core.exceptions import ValidationError
from django.core.validators import MaxValueValidator
from django.utils.translation import gettext_lazy as _


class MaxSizeValidator(MaxValueValidator):
    message = _('The file exceed the maximum size of %(limit_value)s MB.')

    def __call__(self, value):
        # get the file size as cleaned value
        cleaned = self.clean(value.size)
        params = {'limit_value': self.limit_value, 'show_value': cleaned, 'value': value}
        if self.compare(cleaned, self.limit_value * 1024 * 1024):  # convert limit_value from MB to Bytes
            raise ValidationError(self.message, code=self.code, params=params)
