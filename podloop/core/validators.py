from django.core.exceptions import ValidationError

def validate_audio_file(value):
    file_extension = value.name.split('.')[-1].lower()
    allowed_extensions = ['mp3', 'wav', 'ogg']  # Add more audio file extensions as needed
    max_size = 250 * 1024 * 1024  # Maximum size in bytes (250MB)

    if file_extension not in allowed_extensions:
        raise ValidationError("Only audio files (MP3, WAV, OGG) are allowed.")

    if value.size > max_size:
        raise ValidationError("The audio file size should be less than 250MB.")
    
def validate_image_file(value):
    file_extension = value.name.split('.')[-1].lower()
    allowed_extensions = ['jpg', 'jpeg', 'png', 'gif']  # Add more image file extensions as needed
    max_size = 3 * 1024 * 1024  # Maximum size in bytes (3MB)

    if file_extension not in allowed_extensions:
        raise ValidationError("Only image files (JPG, JPEG, PNG, GIF) are allowed.")

    if value.size > max_size:
        raise ValidationError("The image file size should be less than 5MB.")