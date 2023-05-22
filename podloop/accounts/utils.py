from django.core.mail import EmailMessage,get_connection
from django.conf import settings
from django.contrib.auth.password_validation import MinimumLengthValidator,NumericPasswordValidator,UserAttributeSimilarityValidator,CommonPasswordValidator
from django.forms import ValidationError
from django.contrib.auth.password_validation import password_validators_help_texts

class Util:
    @staticmethod
    def send_email(data):
        with get_connection(  
            host=settings.EMAIL_HOST, 
            port=settings.EMAIL_PORT,  
            username=settings.EMAIL_HOST_USER, 
            password=settings.EMAIL_HOST_PASSWORD, 
            use_tls=settings.EMAIL_USE_TLS  
        ) as connection:  
            subject = data["subject"]  
            email_from = settings.EMAIL_HOST_USER  
            recipient_list = [data["to_email"], ]  
            message = data["body"]  
            EmailMessage(subject, message, email_from, recipient_list, connection=connection).send()

    
    @staticmethod
    def send_confirm_email(send_to,code):
        link = "http://127.0.0.1:8000/confirm-email/" + str(code)
        data = {
            'subject':'Confirm your PodLoop account',
            'body': '''
                Hello there!\n 
                You are receiving this email because you signed up to PodLoop.\n 
                Please click the link below to confirm your account.\n
                {}
                    '''.format(link),
            'to_email':send_to,
        }
        
        Util.send_email(data)
        
    @staticmethod
    def send_reset_email(send_to,code):
        link = "http://127.0.0.1:8000/reset-password/" + send_to + "/" + str(code)
        data = {
            'subject':'Reset your PodLoop account\'s password',
            'body': '''
                Hello there!\n 
                You are receiving this email because you you want to reset your password.\n 
                Please click the link below to reset it.\n
                {}\n
                If you haven't requested this reset, then please ignore this email.\n
                    '''.format(link),
            'to_email':send_to,
        }
        
        Util.send_email(data)
        
    @staticmethod
    def send_creator_email(send_to,code):
        link = "http://127.0.0.1:8000/confirm-email/" + str(code)
        data = {
            'subject':'Confirm your PodLoop account\'s email',
            'body': '''
                Hello there!\n 
                You are receiving this email because you want to become a creator for PodLoop.\n 
                Please click the link below to verify your email.\n
                {}\n
                '''.format(link),
            'to_email':send_to,
        }
        
        Util.send_email(data)
    
    @staticmethod    
    def validate_password(password):
        password_validators = [MinimumLengthValidator,NumericPasswordValidator,UserAttributeSimilarityValidator,CommonPasswordValidator]

        errors = []
        for validator in password_validators:
            try:
                validator().validate(password=password)
            except ValidationError:
                error_message = password_validators_help_texts([validator()])
                errors.append(error_message)
                
        return errors
