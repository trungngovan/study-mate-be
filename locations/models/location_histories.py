from django.db import models
from django.contrib.gis.db import models as gis_models
from django.utils import timezone


class LocationHistory(models.Model):
    """
    Location history model to track user's location changes over time.
    Stores location updates when the user moves more than 100m or after 15 minutes.
    """
    
    user = models.ForeignKey(
        "users.User",
        on_delete=models.CASCADE,
        related_name="location_history",
        db_column="user_id"
    )
    geom_point = gis_models.PointField(
        geography=True,
        srid=4326,
        help_text="Geographic location at the time of recording"
    )
    recorded_at = models.DateTimeField(
        default=timezone.now,
        db_index=True,
        help_text="Timestamp when the location was recorded"
    )
    accuracy = models.FloatField(
        null=True,
        blank=True,
        help_text="Location accuracy in meters (from GPS)"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = "location_history"
        indexes = [
            models.Index(fields=["user", "-recorded_at"], name="idx_location_user_time"),
            models.Index(fields=["recorded_at"], name="idx_location_recorded_at"),
            # GIST index for geom_point is created via migration
        ]
        ordering = ["-recorded_at"]
        verbose_name = "Location History"
        verbose_name_plural = "Location Histories"
    
    def __str__(self):
        return f"{self.user.email} - {self.recorded_at}"
