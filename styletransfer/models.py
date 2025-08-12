# from django.db import models

# class StylizedImage(models.Model):
#     original_image = models.ImageField(upload_to='input/')
#     styled_image = models.ImageField(upload_to='output/')
#     model_used = models.CharField(max_length=50)
#     created_at = models.DateTimeField(auto_now_add=True)

#     def __str__(self):
#         return f"{self.model_used} - {self.created_at.strftime('%Y-%m-%d %H:%M')}"

# styletransfer/models.py
from django.db import models

class StylizedImage(models.Model):
    original_image = models.ImageField(upload_to="input/",  max_length=255)   # ↑
    styled_image   = models.ImageField(upload_to="output/", max_length=255)   # ↑
    model_used     = models.CharField(max_length=50)
    created_at     = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.model_used} - {self.created_at:%Y-%m-%d %H:%M}"
