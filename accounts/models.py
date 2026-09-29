from django.db import models
from django.contrib.auth.models import AbstractUser
# Create your models here.
from .enums import UserRole, VerificationStatus


class User(AbstractUser):

    email = models.EmailField(unique=True)
    phone_number = models.CharField(max_length=15, blank=True)
    role = models.CharField(max_length=20,choices=[(role.value, role.name) for role in UserRole],default=UserRole.PATIENT.value,)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


class Patient(models.Model):
    user = models.OneToOneField(User,on_delete=models.CASCADE,related_name="patient_profile",)
    date_of_birth = models.DateField(null=True, blank=True)
    gender = models.CharField(max_length=20, blank=True)
    address = models.TextField(blank=True)
    city = models.CharField(max_length=100, blank=True)
    state = models.CharField(max_length=100, blank=True)
    pincode = models.CharField(max_length=10, blank=True)
    emergency_contact_name = models.CharField(max_length=100,blank=True)
    emergency_contact_phone = models.CharField(max_length=15,blank=True,)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)




class Physiotherapist(models.Model):
    
    user = models.OneToOneField(User,on_delete=models.CASCADE,related_name="physiotherapist_profile")
    license_number = models.CharField(max_length=100,unique=True)
    bio = models.TextField(blank=True)
    experience_years = models.PositiveIntegerField(default=0)
    consultation_fee = models.DecimalField(max_digits=10,decimal_places=2)
    verification_status = models.CharField(max_length=20,
        choices=[(status.value, status.name) for status in VerificationStatus],
        default=VerificationStatus.PENDING.value,
    )
    latitude = models.DecimalField(max_digits=9,decimal_places=6,null=True,blank=True)
    longitude = models.DecimalField(max_digits=9,decimal_places=6,null=True,blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


class PhysiotherapistVerification(models.Model):
    # One row per admin review decision; Physiotherapist.verification_status holds the current state

    physiotherapist = models.ForeignKey(Physiotherapist,on_delete=models.CASCADE,related_name="verification_history")
    status = models.CharField(max_length=20,choices=[(status.value, status.name) for status in VerificationStatus])
    reviewed_by = models.ForeignKey(User,on_delete=models.SET_NULL,null=True,related_name="physiotherapist_reviews")
    rejection_reason = models.TextField(blank=True)
    reviewed_at = models.DateTimeField(auto_now_add=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-reviewed_at", "-id"]

