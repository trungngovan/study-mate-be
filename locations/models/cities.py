from django.db import models
from django.contrib.gis.db import models as gis_models


class City(models.Model):
    """
    City model for representing cities.
    """
    name = models.CharField(max_length=100)
    geom_point = gis_models.PointField(
        geography=True,
        srid=4326,
        null=True,
        blank=True,
        help_text="Geographic location of the city"
    )

    class Meta:
        db_table = "cities"
        indexes = [
            models.Index(fields=["name"], name="idx_cities_name"),
        ]
        verbose_name = "City"
        verbose_name_plural = "Cities"

    def __str__(self):
        return self.name
