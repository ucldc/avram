from django.contrib.auth.backends import RemoteUserBackend
import os
import collection_registry.middleware
from django.contrib.auth.models import Group
from django.core.mail import send_mail

class RegistryUserBackend(RemoteUserBackend):
    def configure_user(self, user):
        """
        Registry user setup
        """
        user.is_staff = True
        request = collection_registry.middleware.get_current_request()
        user.email = request.META['mail']
        user.save()
        # http://stackoverflow.com/a/6288863/1763984
        g = Group.objects.get(name=request.META['Shib-Identity-Provider']) 
        g.user_set.add(user)

        # https://docs.djangoproject.com/en/dev/topics/email/
        send_mail('New registry user {0}'.format(user.username), 'New registry user\n\teppn: {0}\n\temail:{1}'.format(user.username, user.email), user.email,
            ['oacops@cdlib.org'], fail_silently=False)

        return user


