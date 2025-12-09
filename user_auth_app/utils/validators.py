from django.core.exceptions import ValidationError

def validate_file_size(value):
    max_mb = 5
    if value.size > max_mb * 1024 * 1024:
        raise ValidationError(f"File too large. Size should not exceed {max_mb} MB.")