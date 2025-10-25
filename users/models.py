from django.db import models
from django.contrib.gis.db import models as gis_models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.utils import timezone


class UserManager(BaseUserManager):
    """
    Custom manager for User model.
    """
    def create_user(self, email, password=None, **extra_fields):
        """
        Create and return a regular user with email and password.
        """
        if not email:
            raise ValueError('The Email field must be set')
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        if password:
            user.set_password(password)
        user.save(using=self._db)
        return user
    
    def create_superuser(self, email, password=None, **extra_fields):
        """
        Create and return a superuser with email and password.
        """
        extra_fields.setdefault('status', User.STATUS_ACTIVE)
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        
        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True.')
        
        return self.create_user(email, password, **extra_fields)


class User(AbstractBaseUser, PermissionsMixin):
    """
    User model for Study Mate application.
    Stores user profile information, location data, and privacy settings.
    """
    
    # Privacy Level Choices
    PRIVACY_OPEN = "open"
    PRIVACY_FRIENDS_OF_FRIENDS = "friends_of_friends"
    PRIVACY_PRIVATE = "private"
    
    PRIVACY_CHOICES = [
        (PRIVACY_OPEN, "Open"),
        (PRIVACY_FRIENDS_OF_FRIENDS, "Friends of Friends"),
        (PRIVACY_PRIVATE, "Private"),
    ]
    
    # Status Choices
    STATUS_ACTIVE = "active"
    STATUS_BANNED = "banned"
    STATUS_DELETED = "deleted"
    
    STATUS_CHOICES = [
        (STATUS_ACTIVE, "Active"),
        (STATUS_BANNED, "Banned"),
        (STATUS_DELETED, "Deleted"),
    ]
    
    # Basic Information
    email = models.EmailField(unique=True, db_index=True)
    phone = models.CharField(max_length=20, unique=True, null=True, blank=True)
    full_name = models.CharField(max_length=255)
    
    # Django admin fields
    is_staff = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    
    # Academic Information
    school = models.ForeignKey(
        "locations.School",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="students",
        db_column="school_id"
    )
    major = models.CharField(max_length=255, null=True, blank=True)
    year = models.IntegerField(null=True, blank=True)  # Academic year
    
    # Profile Information
    bio = models.TextField(blank=True, default="")
    avatar_url = models.URLField(max_length=500, null=True, blank=True)
    
    # Location & Preferences
    learning_radius_km = models.FloatField(default=5.0)
    geom_last_point = gis_models.PointField(
        geography=True,
        srid=4326,
        null=True,
        blank=True,
        help_text="Last known geographic location of the user"
    )
    
    # Privacy & Status
    privacy_level = models.CharField(
        max_length=20,
        choices=PRIVACY_CHOICES,
        default=PRIVACY_OPEN
    )
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default=STATUS_ACTIVE
    )
    
    # Timestamps
    last_active_at = models.DateTimeField(null=True, blank=True, db_index=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    # Custom User Model fields
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['full_name']
    
    objects = UserManager()
    
    class Meta:
        db_table = "users"
        indexes = [
            models.Index(fields=["email"], name="idx_users_email"),
            models.Index(fields=["last_active_at"], name="idx_users_last_active"),
            models.Index(fields=["school", "year"], name="idx_users_school_year"),
            # GIST index for geom_last_point is created via migration
        ]
        verbose_name = "User"
        verbose_name_plural = "Users"
    
    def __str__(self):
        return f"{self.full_name} ({self.email})"
    
    def get_full_name(self):
        """Return the full name of the user."""
        return self.full_name
    
    def get_short_name(self):
        """Return the short name (email) of the user."""
        return self.email
    
    def update_last_active(self):
        """Update the last_active_at timestamp to current time."""
        self.last_active_at = timezone.now()
        self.save(update_fields=["last_active_at"])
    
    def is_user_active(self):
        """Check if user status is active."""
        return self.status == self.STATUS_ACTIVE
    
    def is_banned(self):
        """Check if user is banned."""
        return self.status == self.STATUS_BANNED
    
    def is_deleted(self):
        """Check if user is deleted."""
        return self.status == self.STATUS_DELETED
