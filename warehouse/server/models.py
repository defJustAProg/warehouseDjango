from django.db import models
import uuid

# Create your models here.

class Roll(models.Model):
    id = models.UUIDField(verbose_name="id", primary_key=True, default=uuid.uuid4)
    length = models.IntegerField(verbose_name="length")
    weight = models.IntegerField(verbose_name="weight")
    put_date = models.DateField(verbose_name="put_date")
    delete_date = models.DateField(verbose_name="delete_date")
    status = models.BooleanField(verbose_name="status", default=True)

    class Meta:
        verbose_name='Товар'

    def __str__(self):
        return f"Товар {self.id}"

    def to_dict(self):
        return {
            "id": self.id,
            "length": self.length,
            "weight": self.weight,
            "put_date": str(self.put_date),
            "delete_date": str(self.delete_date),
            "status": self.status,
        }