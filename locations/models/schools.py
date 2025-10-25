from django.db import models
from django.contrib.gis.db import models as gis_models


class School(models.Model):
    """
    School/Institution model for educational institutions.
    """
    
    # Basic Information
    name = models.CharField(max_length=255)
    short_name = models.CharField(max_length=100, blank=True, default="")
    
    # Location
    address = models.TextField()
    city = models.ForeignKey(
        "locations.City",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="schools",
        db_column="city_id"
    )
    geom_point = gis_models.PointField(
        geography=True,
        srid=4326,
        null=True,
        blank=True,
        help_text="Geographic location of the school"
    )
    
    # Metadata
    website = models.URLField(max_length=500, null=True, blank=True)
    email = models.EmailField(null=True, blank=True)
    phone = models.CharField(max_length=20, null=True, blank=True)
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = "schools"
        indexes = [
            models.Index(fields=["name"], name="idx_schools_name"),
            models.Index(fields=["city"], name="idx_schools_city"),
            # GIST index for geom_point is created via migration
        ]
        verbose_name = "School"
        verbose_name_plural = "Schools"
    
    def __str__(self):
        return self.short_name if self.short_name else self.name
