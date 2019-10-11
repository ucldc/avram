from django.contrib.auth.backends import AllowAllUsersRemoteUserBackend
import os
import collection_registry.middleware
from django.contrib.auth.models import Group
from django.core.mail import send_mail, EmailMultiAlternatives

class RegistryUserBackend(AllowAllUsersRemoteUserBackend):
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
        plaintext_content = "Welcome {0}. You have requested an account for the UC Libraries Digital Collection (UCLDC).\n\n\
         At this time, accounts are limited to UCLDC Implementation Project collaborators (SAG2 and Product Stakeholder\
         Group members and their designees). If your request is approved, you will receive an email within 72 hours with\
         additional instructions on how to edit the Collection Registry and access the Nuxeo DAMS.\n\nFor\
         more information about UCLDC Implementation, visit our project wiki at bit.ly/UCLDC or contact oacops@cdlib.org.".format(user.email)
        
        html_content = "<p>Welcome {0}. You have requested an account for the UC Libraries Digital\
         Collection (UCLDC).</p><p>At this time, accounts are limited to UCLDC Implementation Project\
         collaborators (SAG2 and Product Stakeholder Group members and their designees). If your request\
         is approved, you will receive an email within 72 hours with additional instructions on how to\
         edit the Collection Registry and access the Nuxeo DAMS.</p><p>For more information about UCLDC\
         Implementation, visit our <a href='https://wiki.library.ucsf.edu/display/UCLDC/UCLDC+Implementation'>\
         project wiki</a> or contact <a href='mailto:oacops@cdlib.org'>oacops@cdlib.org</a>.</p>".format(user.email)
        
        email_to_user = EmailMultiAlternatives('UCLDC account request: {0}'.format(user.email), plaintext_content, 'oacops@cdlib.org', [user.email])
        email_to_oacops = EmailMultiAlternatives('UCLDC account request: {0}'.format(user.email), plaintext_content, 'ucldc@ucop.org', ['oacops@cdlib.org'])
        email_to_user.attach_alternative(html_content, "text/html")
        email_to_oacops.attach_alternative(html_content, "text/html")
        email_to_user.send()
        email_to_oacops.send()
        
        return user


