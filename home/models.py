from django.db import models


# Create your models here.
class Sector(models.Model):

  class Meta:
        db_table = 'sector'
        ordering = ['name']

  id = models.AutoField(primary_key=True)
  name = models.CharField(max_length=128)

  def __str__(self) -> str:
      return self.name


class Location(models.Model):

  class Meta:
        db_table = 'location'
        ordering = ['city']

  id = models.AutoField(primary_key=True)
  city = models.CharField(max_length=128)

  def __str__(self) -> str:
      return self.city


class Share(models.Model):

  class Meta:
        db_table = 'share'
        ordering = ['name']

  id = models.AutoField(primary_key=True)
  name = models.CharField(max_length=256)

  def __str__(self) -> str:
      return self.name

class Company(models.Model):

  class Meta:
        db_table = 'company'
        ordering = ['name']

  id = models.AutoField(primary_key=True)
  name = models.CharField(max_length=256)
  desctiption = models.TextField()
  location = models.ForeignKey(Location, on_delete=models.PROTECT)
  sector = models.ForeignKey(Sector, on_delete=models.PROTECT)

  def __str__(self) -> str:
      return self.name

class OurTransaction(models.Model):

  class Meta:
        db_table = 'our_transaction'
        ordering = ['-date']

  id = models.AutoField(primary_key=True)
  company = models.ForeignKey(Company, on_delete=models.PROTECT)
  date = models.DateField()
  amount = models.IntegerField()
  price = models.DecimalField(max_digits=15, decimal_places=3)
  total = models.IntegerField()
  share = models.ForeignKey(Share, on_delete=models.PROTECT)

  def __str__(self) -> str:
      return str(self.date)