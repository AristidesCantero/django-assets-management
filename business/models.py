from django.db import models



DEFAULT_SYSTEM_SEGREGATIONS = ["Electrico","Hidráulico","Neumático","Mecánico","Magnético"]

class SystemSegregation(models.Model):
    type = models.CharField(max_length=100)
    description = models.CharField(max_length=200)

class Asset(models.Model):
    name = models.CharField(max_length=100)
    manufacturer = models.CharField(max_length=255)
    family_model = models.CharField(max_length=255)
    part_number = models.CharField(max_length=255)
    serial_number = models.CharField(max_length=255)
    op_capability = models.CharField(max_length=255)
    height = models.DecimalField(max_digits=10, decimal_places=2)
    width = models.DecimalField(max_digits=10, decimal_places=2)
    depth = models.DecimalField(max_digits=10, decimal_places=2)
    weight = models.DecimalField(max_digits=10, decimal_places=2)
    fuel_energy_type = models.CharField(max_length=100)
    technical_data = models.TextField()
    system_segregation = models.ForeignKey(SystemSegregation, null=True, on_delete=models.SET_NULL)
    additional_info = models.TextField()
    creation_date = models.DateField(auto_now_add=True, blank=True, null=True)
    update_date = models.DateField(auto_now=True, blank=True, null=True)

    def __str__(self):
        return self.name

 

# class Business(models.Model):
#     name = models.CharField(max_length=100)
#     society = models.CharField(max_length=100)
#     logo_picture = models.ImageField(default='default/business.png', null=True, blank=True)
#     email = models.EmailField()
#     alternative_email = models.EmailField(null=True, blank=True)
#     address = models.TextField()
#     city = models.CharField(max_length=100)
#     state = models.CharField(max_length=100)
#     phone = models.CharField(max_length=100)
#     owner = models.ForeignKey(User, on_delete=models.CASCADE)
#     created_at = models.DateTimeField(auto_now_add=True)
#     updated_at = models.DateTimeField(auto_now=True)

#     def __str__(self):
#         return self.name

#     class Meta:
#         verbose_name_plural = 'Businesses'

#     def __str__(self):
#         return self.name





# Create your models here.
