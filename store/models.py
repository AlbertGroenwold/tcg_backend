from django.contrib.auth.models import AbstractUser
from django.db import models
from .managers import CustomUserManager  # Ensure this is implemented correctly

# Item Model
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


# Custom User Model
class CustomUser(AbstractUser):
    username = None  # Remove the username field
    email = models.EmailField(unique=True)  # Email will be the unique identifier

    USERNAME_FIELD = 'email'  # Use email as the unique field
    REQUIRED_FIELDS = []  # Remove other required fields

    objects = CustomUserManager()  # Assign the custom manager

    def __str__(self):
        return self.email


# UserProfile Model
class UserProfile(models.Model):
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE, related_name='profile')
    primary_address = models.TextField()
    secondary_address = models.TextField(blank=True, null=True)

    def __str__(self):
        return self.user.email  # Use email instead of username


# Orders Model
class Order(models.Model):
    id = models.AutoField(primary_key=True)
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='orders')
    date = models.DateTimeField(auto_now_add=True)
    payment_status = models.CharField(max_length=50, default="Pending")
    fulfillment_status = models.CharField(max_length=50, default="Processing")
    total = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)

    def save(self, *args, **kwargs):
        # Save the Order instance first to ensure it has a primary key
        super().save(*args, **kwargs)

        # Recalculate the total after saving the Order instance
        self.total = sum(
            detail.price for detail in self.order_details.all()
        )

        # Save again to update the total
        super().save(update_fields=['total'])

    def __str__(self):
        return f"Order #{self.id} - {self.user.email}"




# OrderDetails Model (Many-to-Many Link between Orders and Items)
class OrderDetail(models.Model):
    id = models.AutoField(primary_key=True)
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='order_details')
    item = models.ForeignKey(Item, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)
    price = models.DecimalField(max_digits=10, decimal_places=2)

    def save(self, *args, **kwargs):
        # Calculate price if not provided
        if not self.price:
            self.price = self.item.price * self.quantity
        super().save(*args, **kwargs)
        # Update the total for the related order
        self.order.save()

    def delete(self, *args, **kwargs):
        super().delete(*args, **kwargs)
        # Update the total for the related order
        self.order.save()

    def __str__(self):
        return f"Order #{self.order.id} - Item {self.item.name}"
