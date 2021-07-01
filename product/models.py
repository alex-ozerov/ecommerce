import base64
from django.utils.text import slugify
from django.contrib.auth.models import User
from django.db import models

# Create your models here.


class Image(models.Model):
    title = models.CharField(max_length=50, blank=True)
    image = models.ImageField(blank=False, upload_to='images/')
    base_64 = models.CharField(max_length=500000, default="", blank=True)
    slug = models.SlugField(null=False, unique=True, blank=True)

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        self.slug = slugify(self.title)
        self.base_64 = base64.b64encode(self.image.read()).decode('utf-8')
        super(Image, self).save(*args, **kwargs)


class Category(models.Model):
    title = models.CharField(max_length=50)
    description = models.TextField(max_length=255)
    image = models.ForeignKey(Image, blank=True, on_delete=models.SET_NULL, null=True)
    slug = models.SlugField(null=False, unique=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        self.slug = slugify(self.title)
        super(Category, self).save(*args, **kwargs)


class Product(models.Model):
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    title = models.CharField(max_length=150)
    description = models.TextField(max_length=255)
    image = models.ForeignKey(Image, blank=True, on_delete=models.SET_NULL, null=True)
    price = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    status = models.BooleanField(default=False, blank=False)
    amount = models.IntegerField(default=0)
    slug = models.SlugField(null=False, unique=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        self.slug = slugify(self.title)
        super(Product, self).save(*args, **kwargs)

    @property
    def get_description_as_list(self):
        return [sentence.split(': ') for sentence in self.description.split('\n')]


class Comment(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    subject = models.CharField(max_length=50, blank=True)
    comment = models.CharField(max_length=250, blank=True)
    rate = models.IntegerField(default=1)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.subject
