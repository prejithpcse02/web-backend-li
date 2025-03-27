from django.db import models
from users.models import User
from django.utils.text import slugify
import uuid

class Listing(models.Model):
    CONDITION_CHOICES = [
        ('new', 'New'),
        ('like_new', 'Like New'),
        ('lightly_used', 'Lightly Used'),
        ('well_used', 'Well Used'),
        ('heavily_used', 'Heavily Used'),
    ]

    product_id = models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True)
    seller = models.ForeignKey(User, on_delete=models.CASCADE, related_name="listings")
    title = models.CharField(max_length=255)
    slug = models.SlugField(max_length=25, blank=True)
    description = models.TextField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    condition = models.CharField(max_length=20, choices=CONDITION_CHOICES, default='new')
    location = models.CharField(max_length=100)
    status = models.CharField(max_length=20, choices=[
        ('available', 'Available'),
        ('pending', 'Pending'),
        ('sold', 'Sold'),
    ], default='available')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)  # Allows editing

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.title} - {self.seller.nickname}"

    @property
    def like_count(self):
        return self.likes.count()

    def is_liked_by(self, user):
        if user.is_authenticated:
            return self.likes.filter(user=user).exists()
        return False

class ListingImage(models.Model):
    listing = models.ForeignKey(Listing, on_delete=models.CASCADE, related_name="images")
    image = models.ImageField(upload_to='listing_images/')

    def __str__(self):
        return f"Image for {self.listing.title}"
    
#For Search
class RecentSearch(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='recent_searches')
    query = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']
        unique_together = ['user', 'query']

class Like(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='likes')
    listing = models.ForeignKey(Listing, on_delete=models.CASCADE, related_name='likes')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ['user', 'listing']  # Prevent duplicate likes