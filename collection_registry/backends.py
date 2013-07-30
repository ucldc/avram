from django.contrib.auth.backends import RemoteUserBackend
import os
import collection_registry.middleware

class RegistryUserBackend(RemoteUserBackend):
    def configure_user(self, user):
        """
        Registry user setup
        """
        user.is_staff = True
        request = collection_registry.middleware.get_current_request()
        user.email = request.META['mail']
        user.save()
        return user
