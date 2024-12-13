from django.contrib.auth.models import AbstractUser
from django.db import models
from .managers import CustomUserManager  # Ensure this is implemented correctly

class Item(models.Model):
    id = models.AutoField(primary_key=True)  # Automatically generated ID
    name = models.CharField(max_length=255)
    category = models.CharField(max_length=255, default="Unknown")
    description = models.TextField(blank=True, null=True)  # Optional description
    price = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)  # Price field
    stock = models.PositiveIntegerField(default=0)  # Stock field
    image = models.ImageField(upload_to='item_images/', blank=True, null=True)  # Image upload field
    release_date = models.DateField(blank=True, null=True)  # New release date field
    contains = models.TextField(blank=True, null=True)  # New contains field (e.g., items it contains)

    def __str__(self):
        return self.name


class CustomUser(AbstractUser):
    username = None  # Remove the username field
    email = models.EmailField(unique=True)  # Email will be the unique identifier

    USERNAME_FIELD = 'email'  # Use email as the unique field
    REQUIRED_FIELDS = []  # Remove other required fields

    objects = CustomUserManager()  # Assign the custom manager

    def __str__(self):
        return self.email


class UserProfile(models.Model):
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE, related_name='profile')
    primary_address = models.TextField()
    secondary_address = models.TextField(blank=True, null=True)
    order_ids = models.TextField(blank=True, null=True)  # Store as a comma-separated list

    def __str__(self):
        return self.user.email  # Use email instead of username
