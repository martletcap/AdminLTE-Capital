from django.db import models
from django.contrib.auth import get_user_model


User = get_user_model()

class ContactType(models.Model):

    class Meta:
        db_table = 'contact_type'

    id = models.AutoField(primary_key=True)
    type = models.CharField(max_length=128)

    def __str__(self)->str:
        return self.type


class Contact(models.Model):
    
    class Meta:
        db_table = 'contact'

    name = models.CharField(max_length=256)
    email = models.EmailField(blank=True)
    phone = models.CharField(max_length=128, blank=True)
    comment = models.TextField(max_length=1024, blank=True)
    website = models.CharField(max_length=256, blank=True)
    type = models.ForeignKey(ContactType, on_delete=models.PROTECT)

    def __str__(self)->str:
        return self.name
    

class Sector(models.Model):

    class Meta:
        db_table = 'sector'
        ordering = ['name']

    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=256)

    def __str__(self) -> str:
        return self.name


class Location(models.Model):

    class Meta:
        db_table = 'location'

    id = models.AutoField(primary_key=True)
    city = models.CharField(max_length=128)
    country = models.CharField(max_length=128)

    def __str__(self) -> str:
        return self.city
    

class CompanyStatus(models.Model):

    class Meta:
        db_table = 'company_status'
        verbose_name_plural = "Company statuses"
        ordering = ['status']

    id = models.AutoField(primary_key=True)
    status = models.CharField(max_length=256)

    def __str__(self) -> str:
        return self.status
    

class CategoryOfCompany(models.Model):

    class Meta:
        db_table = 'category_of_company'
        ordering = ['category']

    id = models.AutoField(primary_key=True)
    category = models.CharField(max_length=256)

    def __str__(self) -> str:
        return self.category
    

class Company(models.Model):

    class Meta:
        db_table = 'company'
        ordering = ['name']

    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=256)
    short_name = models.CharField(max_length=256, blank=True)
    comment = models.TextField(max_length=1024, blank=True)
    staff = models.ForeignKey(User, on_delete=models.PROTECT)
    contact = models.ForeignKey(Contact, on_delete=models.PROTECT)
    location = models.ForeignKey(Location, on_delete=models.PROTECT)
    sector = models.ForeignKey(Sector, on_delete=models.PROTECT)
    status = models.ForeignKey(CompanyStatus, on_delete=models.PROTECT)
    link = models.CharField(max_length=256, blank=True)
    category = models.ForeignKey(CategoryOfCompany, on_delete=models.PROTECT)

    def __str__(self) -> str:
        return self.short_name


class SeedStep(models.Model):
    
    class Meta:
        db_table = 'seed_step'
        ordering = ['-end_term']

    id = models.AutoField(primary_key=True)
    company = models.ForeignKey(Company, on_delete=models.PROTECT)
    start_term = models.DateField()
    end_term = models.DateField()


class ShareType(models.Model):

    class Meta:
        db_table = 'share_type'
        ordering = ['type']

    id = models.AutoField(primary_key=True)
    type = models.CharField(max_length=256)

    def __str__(self)->str:
        return self.type


class Share(models.Model):

    class Meta:
        db_table = 'share'

    id = models.AutoField(primary_key=True)
    type = models.ForeignKey(ShareType, on_delete=models.PROTECT)
    add_by = models.ForeignKey(User, on_delete=models.PROTECT)
    company = models.ForeignKey(Company, on_delete=models.PROTECT)
    comment = models.TextField(max_length=1024, blank=True)

    def __str__(self) -> str:
        return f'{self.company}-{self.type}'
    

class Shareholder(models.Model):

    class Meta:
        db_table = 'shareholder'

    id = models.AutoField(primary_key=True)
    date = models.DateField()
    amount = models.IntegerField()
    owner = models.ForeignKey(Contact, on_delete=models.PROTECT)
    complite = models.BooleanField(default=True)
    add_by = models.ForeignKey(
        User, on_delete=models.PROTECT,
        related_name='shareholder_add',
    )
    add_datetime = models.DateTimeField(auto_now_add=True)
    last_edit_by = models.ForeignKey(
        User, on_delete=models.PROTECT,
        related_name='shareholder_edit',
    )
    last_edit_datetime = models.DateTimeField(auto_now=True)
    share = models.ForeignKey(Share, on_delete=models.PROTECT)
    comment = models.TextField(max_length=1024, blank=True)


class OurTransaction(models.Model):

    class Meta:
        db_table = 'our_transaction'
        ordering = ['-date']

    id = models.AutoField(primary_key=True)
    share = models.ForeignKey(Share, on_delete=models.PROTECT)
    date = models.DateField()
    amount = models.IntegerField()
    price = models.DecimalField(max_digits=12, decimal_places=4)
    add_by = models.ForeignKey(
        User, on_delete=models.PROTECT,
        related_name='our_transaction_add',
    )
    add_datetime = models.DateTimeField(auto_now_add=True)
    last_edit_by = models.ForeignKey(
        User, on_delete=models.PROTECT,
        related_name='our_transaction_edit',
    )
    last_edit_datetime = models.DateTimeField(auto_now=True)
    comment = models.TextField(max_length=1024, blank=True)

    def __str__(self) -> str:
        return str(self.date)
    

class SharePrice(models.Model):

    class Meta:
        db_table = 'share_price'

    id = models.AutoField(primary_key=True)
    share = models.ForeignKey(Share, on_delete=models.PROTECT)
    price = models.DecimalField(max_digits=16, decimal_places=8)
    date = models.DateField()