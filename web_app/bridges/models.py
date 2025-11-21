from django.db import models

class Bridge(models.Model):
    state_code = models.CharField(max_length=10)
    county_code = models.CharField(max_length=10)
    structure_number = models.CharField(max_length=50)
    location = models.CharField(max_length=255, null=True, blank=True)
    features_desc = models.CharField(max_length=255, null=True, blank=True)
    facility_carried = models.CharField(max_length=255, null=True, blank=True)
    latitude = models.FloatField(null=True, blank=True)
    longitude = models.FloatField(null=True, blank=True)
    year_built = models.IntegerField(null=True, blank=True)
    structure_kind = models.CharField(max_length=10, null=True, blank=True)
    structure_type = models.CharField(max_length=10, null=True, blank=True)
    deck_structure_type = models.CharField(max_length=10, null=True, blank=True)
    main_unit_spans = models.IntegerField(null=True, blank=True)
    max_span_len_mt = models.FloatField(null=True, blank=True)
    structure_len_mt = models.FloatField(null=True, blank=True)
    adt = models.IntegerField(null=True, blank=True)
    year_adt = models.IntegerField(null=True, blank=True)
    deck_cond = models.CharField(max_length=10, null=True, blank=True)
    superstructure_cond = models.CharField(max_length=10, null=True, blank=True)
    substructure_cond = models.CharField(max_length=10, null=True, blank=True)
    operating_rating = models.FloatField(null=True, blank=True)
    inventory_rating = models.FloatField(null=True, blank=True)
    structural_eval = models.CharField(max_length=10, null=True, blank=True)
    data_year = models.IntegerField()

    class Meta:
        unique_together = ('structure_number', 'data_year')
        ordering = ['-data_year']

    def __str__(self):
        return f"{self.structure_number} ({self.data_year})"

class Feedback(models.Model):
    bridge = models.ForeignKey(Bridge, on_delete=models.CASCADE, related_name='feedbacks')
    name = models.CharField(max_length=100)
    email = models.EmailField()
    rating = models.IntegerField(choices=[(i, i) for i in range(1, 6)])
    comment = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Feedback for {self.bridge} by {self.name}"
