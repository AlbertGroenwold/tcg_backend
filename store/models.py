from django.contrib.auth.models import AbstractUser
from django.db import models
from .managers import CustomUserManager  # Ensure this is implemented correctly


# Category Model
class Category(models.Model):
    name = models.CharField(max_length=255, unique=True)
    parent = models.ForeignKey(
        'self',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='children'
    )

    class Meta:
        db_table = 'categories'
        verbose_name_plural = 'categories'

    def __str__(self):
        # Display the full hierarchy (e.g., "Grandparent > Parent > Child")
        ancestors = [self.name]
        parent = self.parent
        while parent:
            ancestors.append(parent.name)
            parent = parent.parent
        return " > ".join(reversed(ancestors))

class Tag(models.Model):
    id = models.AutoField(primary_key=True)  # Auto-generated ID
    name = models.CharField(max_length=255, unique=True)  # Unique name for the tag
    description = models.TextField(blank=True, null=True)  # Optional description of the tag
    date_created = models.DateTimeField(auto_now_add=True)  # Automatically populated when tag is created

    def __str__(self):
        return self.name


class Supplier(models.Model):
    id = models.AutoField(primary_key=True)  # Auto-generated ID
    name = models.CharField(max_length=255, unique=True)  # Supplier name
    contact_email = models.EmailField(blank=True, null=True)  # Optional contact email
    contact_phone = models.CharField(max_length=20, blank=True, null=True)  # Optional contact phone number
    address = models.TextField(blank=True, null=True)  # Optional address
    website = models.URLField(blank=True, null=True)  # Optional website URL
    date_added = models.DateTimeField(auto_now_add=True)  # Automatically populate with current timestamp

    def __str__(self):
        return self.name

# Item Model
class Item(models.Model):
    id = models.AutoField(primary_key=True)  # Automatically generated ID
    name = models.CharField(max_length=255, unique=True)  # Ensure names are unique
    categories = models.ManyToManyField(Category, related_name='items', blank=True)  # Many-to-many relationship with Category
    description = models.TextField(blank=True, null=True)  # Optional description
    price = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)  # Price field
    stock = models.PositiveIntegerField(default=0)  # Stock field
    image = models.ImageField(upload_to='item_images/', blank=True, null=True)  # Image upload field
    release_date = models.DateField(blank=True, null=True)  # New release date field
    contains = models.TextField(blank=True, null=True)  # New contains field (e.g., items it contains)
    date_added = models.DateTimeField(auto_now_add=True)  # Automatically populated with the current timestamp when added
    discount_price = models.DecimalField(max_digits=10, decimal_places=2, blank=True,null=True)  # Optional discount price
    sku = models.CharField(max_length=100, unique=True)  # Unique Stock Keeping Unit
    tags = models.ManyToManyField(Tag, related_name='items', blank=True)  # Related tags
    is_active = models.BooleanField(default=True)  # Indicates if the item is active or inactive
    views = models.PositiveIntegerField(default=0)  # Count of item views
    rating = models.DecimalField(max_digits=3, decimal_places=2, default=0.0)  # Average rating
    reviews_count = models.PositiveIntegerField(default=0)  # Number of reviews
    weight = models.DecimalField(max_digits=6, decimal_places=2, blank=True, null=True)  # Weight in kilograms
    dimensions = models.CharField(max_length=255, blank=True, null=True)  # Dimensions in format 'LxWxH'
    supplier = models.ForeignKey(Supplier, on_delete=models.SET_NULL, null=True, blank=True,related_name='items')  # Supplier relationship

    def __str__(self):
        return self.name

# Address Model
class Address(models.Model):
    PROVINCE_CHOICES = [
        ("Eastern Cape", "Eastern Cape"),
        ("Free State", "Free State"),
        ("Gauteng", "Gauteng"),
        ("KwaZulu-Natal", "KwaZulu-Natal"),
        ("Limpopo", "Limpopo"),
        ("Mpumalanga", "Mpumalanga"),
        ("North West", "North West"),
        ("Northern Cape", "Northern Cape"),
        ("Western Cape", "Western Cape"),
    ]

    user = models.ForeignKey(
        'CustomUser', on_delete=models.CASCADE, related_name='addresses'
    )
    address_type = models.CharField(
        max_length=20, choices=(("primary", "Primary"), ("secondary", "Secondary"))
    )
    address = models.TextField()
    city = models.CharField(max_length=255)
    province = models.CharField(max_length=255, choices=PROVINCE_CHOICES)
    postal_code = models.CharField(max_length=10)
    country = models.CharField(max_length=255, default="South Africa")

    class Meta:
        db_table = 'addresses'

    def __str__(self):
        return f"{self.address_type.capitalize()} Address for {self.user.email}"


# Custom User Model
class CustomUser(AbstractUser):
    username = None  # Remove the username field
    email = models.EmailField(unique=True)  # Email will be the unique identifier

    USERNAME_FIELD = 'email'  # Use email as the unique field
    REQUIRED_FIELDS = []  # Remove other required fields

    objects = CustomUserManager()  # Assign the custom manager

    def __str__(self):
        return self.email


# Orders Model
class Order(models.Model):
    id = models.AutoField(primary_key=True)
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='orders')
    date = models.DateTimeField(auto_now_add=True)
    payment_status = models.CharField(max_length=50, default="Pending")
    fulfillment_status = models.CharField(max_length=50, default="Processing")
    total = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    address = models.TextField(max_length=255, default="UNKNOWN")  # New field to store selected address

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        self.total = sum(detail.price for detail in self.order_details.all())
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
