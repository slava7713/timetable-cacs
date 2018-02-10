# Setting up Raygun integration for email notifications for errors

from raygun4py import raygunprovider
import os

api_key = os.environ['RAYGUN_API_KEY']
client = raygunprovider.RaygunSender(api_key)
