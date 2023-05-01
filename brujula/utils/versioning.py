from rest_framework.versioning import URLPathVersioning


class AppVersioning(URLPathVersioning):
    default_version = "v1"
    allowed_versions = ["v1","v1.1","v1.2","2"]
    version_param = "version"