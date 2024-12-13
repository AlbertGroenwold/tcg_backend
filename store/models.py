from django.db import models

class Item(models.Model):
    id = models.AutoField(primary_key=True)  # Automatically generated ID
    name = models.CharField(max_length=255)
    category = models.CharField(max_length=255, default="Unknown")
    description = models.TextField(blank=True, null=True)  # Optional description
    price = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)  # Price field
    stock = models.PositiveIntegerField(default=0)  # Stock field
    image = models.ImageField(upload_to='item_images/', blank=True, null=True)  # Image upload field

    def __str__(self):
        return self.name
