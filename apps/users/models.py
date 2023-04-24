from django.db import models
from django.utils import timezone
from django.contrib.auth.models import BaseUserManager, AbstractBaseUser, PermissionsMixin
from django.utils.translation import gettext_lazy as _

class CustomUserManager(BaseUserManager):
    def create_user(self, email, name, password, **extra_fields):
        if not email:
            raise ValueError('Users must have an email address')
        if not name:
            raise ValueError('Users must have a name')

        user = self.model(
            email=email,
            name=name,
            **extra_fields
        )
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, name, email, password=None, **extra_fields):
        superuser = self.create_user(
            password=password,
            email=email,
            name=name,
            **extra_fields
        )
        superuser.is_staff = True
        superuser.is_active = True
        superuser.save(using=self._db)
        return superuser

class User(AbstractBaseUser, PermissionsMixin):

    GENDER_CHOICES = (('M', 'Male'), ('F', 'Female'))

    email = models.EmailField(
        max_length=40, 
        unique=True, 
        null=False, 
        blank=False
        )
    name = models.CharField(
        max_length=30,
        null=False,
        blank=False
        )
    gender = models.CharField(
        max_length=6, 
        choices=GENDER_CHOICES, 
        null=False, 
        blank=False
        )
    birth_date = models.DateField(
        verbose_name=_('Birth Date'),
        null=False,
        )
    is_active = models.BooleanField(
        verbose_name=_('Is active'),
        default=True
        )
    is_staff = models.BooleanField(
        verbose_name=_('Is staff'),
        default=False
        )
    date_joined = models.DateTimeField(
        verbose_name=_('Date joined'),
        default=timezone.now
        )
    updated_at = models.DateTimeField(auto_now=True)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['name', 'birth_date', 'gender']

    objects = CustomUserManager()

    class Meta:
        db_table = 'user'