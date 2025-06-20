
# Register your models here.
from django.contrib import admin
from .models import Product, Category , Order
from .models import ProductImage

# admin.site.register(Product)
admin.site.register(Category)
admin.site.register(Order)


class ProductImageInline(admin.TabularInline):
    model = ProductImage
    extra = 1

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    inlines = [ProductImageInline]
