import re
from django.core.exceptions import ValidationError
from django.utils.translation import gettext as _


class StrongPasswordValidator:
    def validate(self, password, user=None):
        if len(password) < 8:
            raise ValidationError(
                _("Password must be at least 8 characters long.")
            )

        if not re.fullmatch(r"[!-~]+", password):
            raise ValidationError(
                _("Password can only contain letters, numbers, and symbols (no spaces or emojis).")
            )

    def get_help_text(self):
        return _(
            "Your password must be at least 8 characters long and contain only letters, numbers, and symbols."
        )
