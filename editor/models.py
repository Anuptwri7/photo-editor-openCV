from django.db import models
class Photo(models.Model):
    original = models.ImageField(upload_to='photos/originals/')
    edited = models.ImageField(upload_to='photos/edited/', null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    def __str__(self):
        return f'Photo {self.id}'
