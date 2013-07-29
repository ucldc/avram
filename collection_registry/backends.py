from django.contrib.auth.backends import RemoteUserBackend

class RegistryUserBackend(RemoteUserBackend):
    def configure_user(self, user):
        """
        Registry user setup
        """
        user.is_staff = True
        user.save()
        return user
