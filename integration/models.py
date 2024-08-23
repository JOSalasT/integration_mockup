from django.db import models


class IntegrationScenario(models.Model):
    ontology = models.TextField()
    user = models.CharField(max_length=255)
    source_data = models.TextField()

class MaterialisationResults(models.Model):
    name = models.CharField(max_length=255)

