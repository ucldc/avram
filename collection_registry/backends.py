from django.contrib.auth.backends import RemoteUserBackend
import os
import collection_registry.middleware
from django.contrib.auth.models import Group
from django.core.mail import send_mail, EmailMultiAlternatives

class RegistryUserBackend(RemoteUserBackend):
    def configure_user(self, user):
        """
        Registry user setup
        """
        user.is_active = False
        request = collection_registry.middleware.get_current_request()
        user.email = request.META['mail']
        user.save()
        # http://stackoverflow.com/a/6288863/1763984
        g = Group.objects.get(name=request.META['Shib-Identity-Provider']) 
        g.user_set.add(user)
        
        # https://docs.djangoproject.com/en/dev/topics/email/
        send_mail('New registry user {0}'.format(user.username), 'New registry user\n\teppn: {0}\n\temail:{1}'.format(user.username, user.email), user.email,
            ['ucldc@ucop.edu'], fail_silently=False)
        
        plaintext_content = "You have requested an account for the UC Libraries Digital Collection (UCLDC).\
         At this time, accounts are limited to UCLDC Implementation Project collaborators. If your request is\
         approved, you will receive an email with additional instructions on how to access the editing\
         interface for the Collection Registry and the Nuxeo digital asset management system (DAMS).\n\nFor\
         more information about the UCLDC Implementation Project, visit our wiki at bit.ly/UCLDC or contact ucldc@ucop.edu."
        
        html_content = "You have requested an account for the UC Libraries Digital Collection (UCLDC).\
         At this time, accounts are limited to UCLDC Implementation Project collaborators. If your request is\
         approved, you will receive an email with additional instructions on how to access the editing\
         interface for the Collection Registry and the Nuxeo digital asset management system (DAMS).<br><br>\
         For more information about the UCLDC Implementation Project, visit our\
         <a href='https://wiki.library.ucsf.edu/display/UCLDC/UCLDC+Implementation'>wiki</a> or contact\
          <a href='mailto:ucldc@ucop.edu'>ucldc@ucop.edu</a>."
        
        email_to_user = EmailMultiAlternatives('UCLDC account request', plaintext_content, 'ucldc@ucop.edu', [user.email], ['ucldc@ucop.edu'])
        email_to_user.attach_alternative(html_content, "text/html")
        email_to_user.send()
        
        return user


