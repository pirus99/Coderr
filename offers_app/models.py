import os
from django.core.validators import FileExtensionValidator
from django.core.validators import MinValueValidator
from django.core.files.storage import default_storage
from django.db.models.signals import post_delete
from django.db import models
from django.dispatch import receiver
from user_auth_app.models import UserProfile

# Create your models here.

class Offer(models.Model):
    title = models.CharField(max_length=200)
    image = models.FileField(upload_to='offer_images/', blank=True, null=True, validators=[FileExtensionValidator(allowed_extensions=['jpg', 'jpeg', 'png'])])
    description = models.TextField(blank=True)
    user = models.ForeignKey(UserProfile, related_name='offers', on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def update_image(self):
        ext = self.image.name.split('.')[-1]
        new_image_name = f"user_{self.user.id}_{self.user.username}_offer_{self.id}.{ext}"
        self.image.name = new_image_name

    def save(self, *args, **kwargs):
        if self.image:
            self.update_image()
        if self.id:
            original = Offer.objects.get(pk=self.id)
            if original.image:
                old_image_path = original.image.path
                if os.path.exists(old_image_path):
                    default_storage.delete(old_image_path)
                self.update_image()
        super(Offer, self).save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        if self.image:
            image_path = self.image.path
            if os.path.exists(image_path):
                default_storage.delete(image_path)
        super().delete(*args, **kwargs)

    def __str__(self):
        return f"Business User: {self.user.first_name} {self.user.last_name}, Offer: {self.id}"


@receiver(post_delete, sender=Offer)
def delete_offer_image(sender, instance, **kwargs):
    if instance.image:
        image_path = instance.image.path
        if os.path.exists(image_path):
            default_storage.delete(image_path)

class OfferDetails(models.Model):
    offer = models.ForeignKey(Offer, related_name='details', on_delete=models.CASCADE)
    title = models.CharField(max_length=200)
    revisions = models.PositiveIntegerField(default=0)
    delivery_time_in_days = models.PositiveSmallIntegerField(blank=True, null=True)
    price = models.PositiveIntegerField(blank=True, null=True)
    features = models.JSONField(blank=True, null=True, default=list)
    offer_type = models.CharField(max_length=20, choices=[('basic', 'Basic'), ('standard', 'Standard'), ('premium', 'Premium')])

    class Meta:
        verbose_name = 'Offer Detail'