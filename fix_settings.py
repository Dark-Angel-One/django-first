import os

with open('config/settings.py', 'r') as f:
    content = f.read()

# Add WhiteNoise
if 'whitenoise.middleware.WhiteNoiseMiddleware' not in content:
    content = content.replace(
        "'django.middleware.security.SecurityMiddleware',",
        "'django.middleware.security.SecurityMiddleware',\n    'whitenoise.middleware.WhiteNoiseMiddleware',"
    )

# Add STATIC_ROOT
if "STATIC_ROOT" not in content:
    content += "\nSTATIC_ROOT = BASE_DIR / 'staticfiles'\n"

# Add Whitenoise storage
if "STATICFILES_STORAGE" not in content and "STORAGES" not in content:
    content += "\nSTORAGES = {\n    'default': {\n        'BACKEND': 'django.core.files.storage.FileSystemStorage',\n    },\n    'staticfiles': {\n        'BACKEND': 'whitenoise.storage.CompressedManifestStaticFilesStorage',\n    },\n}\n"

with open('config/settings.py', 'w') as f:
    f.write(content)
