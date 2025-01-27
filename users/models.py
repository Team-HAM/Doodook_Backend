from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.db import models





# Custom User Manager
class UserManager(BaseUserManager):
    def create_user(self, email, password, **extra_fields):
        if not email:
            raise ValueError('The Email must be set')
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)

        if not extra_fields.get('is_staff'):
            raise ValueError('Superuser must have is_staff=True.')
        if not extra_fields.get('is_superuser'):
            raise ValueError('Superuser must have is_superuser=True.')

        return self.create_user(email, password, **extra_fields)

# Custom User Model
class User(AbstractBaseUser, PermissionsMixin):
    """Custom User Model"""
    username = None
    email = models.EmailField(unique=True, max_length=255)
    gender = models.CharField(choices=[
        ("male", "Male"),
        ("female", "Female"),
        ("other", "Other")
    ], max_length=10, blank=True)
    nickname = models.CharField(max_length=20, blank=True)
    birthdate = models.DateField(null=True, blank=True)
    address = models.CharField(max_length=100, blank=True)

    is_staff = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []
    objects = UserManager()

    def __str__(self):
        return self.email


# models.py
from django.db import models

class StockPortfolio(models.Model):
    stock_code = models.CharField(max_length=10)  # 주식 코드
    quantity = models.IntegerField(default=0)     # 보유 수량
    price = models.IntegerField(default=0)        # 주식 가격 (가상 시뮬레이션)
    
    def __str__(self):
        return f"{self.stock_code} - {self.quantity}주"




