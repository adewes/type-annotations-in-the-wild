import os
ACCESS_TOKEN=None

#you can also pass your access token as an environment variable (safer)
if os.environ.get('GITHUB_ACCESS_TOKEN'):
    ACCESS_TOKEN = os.environ['GITHUB_ACCESS_TOKEN']