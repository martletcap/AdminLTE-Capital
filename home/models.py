from django.db import models
from django.contrib.auth import get_user_model
from simple_history.models import HistoricalRecords

from .managers import SharePriceManager, SplitManager

User = get_user_model()

class ContactType(models.Model):

    class Meta:
        app_label = 'base_info'
        db_table = 'contact_type'

    id = models.AutoField(primary_key=True)
    type = models.CharField(max_length=128, unique=True)
    history = HistoricalRecords()

    def __str__(self)->str:
        return self.type


class Contact(models.Model):
    
    class Meta:
        db_table = 'contact'
        verbose_name_plural = '01. Contacts'

    name = models.CharField(max_length=255, unique=True)
    email = models.EmailField(blank=True)
    phone = models.CharField(max_length=128, blank=True)
    comment = models.TextField(max_length=10240, blank=True)
    website = models.CharField(max_length=256, blank=True)
    type = models.ForeignKey(ContactType, on_delete=models.PROTECT)
    history = HistoricalRecords()

    def __str__(self)->str:
        return self.name
    

class Sector(models.Model):

    class Meta:
        app_label = 'base_info'
        db_table = 'sector'
        ordering = ['name']

    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=255, unique=True)
    history = HistoricalRecords()

    def __str__(self) -> str:
        return self.name


class Location(models.Model):

    class Meta:
        app_label = 'base_info'
        db_table = 'location'
        unique_together = ('city', 'country',)

    id = models.AutoField(primary_key=True)
    city = models.CharField(max_length=128)
    country = models.CharField(max_length=128)
    history = HistoricalRecords()

    def __str__(self) -> str:
        return self.city
    

class CompanyStatus(models.Model):

    class Meta:
        app_label = 'base_info'
        db_table = 'company_status'
        verbose_name_plural = "Company statuses"
        ordering = ['status']

    id = models.AutoField(primary_key=True)
    status = models.CharField(max_length=255, unique=True)
    history = HistoricalRecords()

    def __str__(self) -> str:
        return self.status
    

class CategoryOfCompany(models.Model):

    class Meta:
        app_label = 'base_info'
        db_table = 'category_of_company'
        ordering = ['category']

    id = models.AutoField(primary_key=True)
    category = models.CharField(max_length=255, unique=True,)
    history = HistoricalRecords()

    def __str__(self) -> str:
        return self.category
    

class Company(models.Model):

    class Meta:
        db_table = 'company'
        ordering = ['name']
        verbose_name_plural = '02. Companys'

    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=255)
    short_name = models.CharField(max_length=256, blank=True)
    comment = models.TextField(max_length=10240, blank=True)
    staff = models.ForeignKey(User, on_delete=models.PROTECT)
    contact = models.ForeignKey(
        Contact,
        on_delete=models.PROTECT,
        null=True,
        blank=True,
    )
    location = models.ForeignKey(Location, on_delete=models.PROTECT)
    sector = models.ForeignKey(Sector, on_delete=models.PROTECT)
    status = models.ForeignKey(CompanyStatus, on_delete=models.PROTECT)
    number = models.IntegerField(blank=True, null=True)
    category = models.ForeignKey(CategoryOfCompany, on_delete=models.PROTECT)
    history = HistoricalRecords()

    def __str__(self) -> str:
        return self.name


class SeedStep(models.Model):
    
    class Meta:
        db_table = 'seed_step'
        ordering = ['-end_term']
        verbose_name_plural = '10. Seed Steps'

    id = models.AutoField(primary_key=True)
    company = models.ForeignKey(Company, on_delete=models.PROTECT)
    start_term = models.DateField()
    end_term = models.DateField()
    history = HistoricalRecords()


class ShareType(models.Model):

    class Meta:
        app_label = 'base_info'
        db_table = 'share_type'
        ordering = ['type']

    id = models.AutoField(primary_key=True)
    type = models.CharField(max_length=255, unique=True)
    history = HistoricalRecords()

    def __str__(self)->str:
        return self.type


class Share(models.Model):

    class Meta:
        db_table = 'share'
        unique_together = ('company', 'type')
        verbose_name_plural = '03. Shares'

    id = models.AutoField(primary_key=True)
    type = models.ForeignKey(ShareType, on_delete=models.PROTECT)
    company = models.ForeignKey(Company, on_delete=models.PROTECT)
    comment = models.TextField(max_length=10240, blank=True)
    history = HistoricalRecords()

    def __str__(self) -> str:
        return f'{self.company}-{self.type}'

class Split(models.Model):
    
    class Meta:
        db_table = 'split'
        verbose_name_plural = '09. Splits'

    id = models.AutoField(primary_key=True)
    date = models.DateField()
    share = models.ForeignKey(Share, on_delete=models.PROTECT)
    comment = models.TextField(max_length=10240, blank=True)
    before = models.IntegerField(default=1)
    after = models.IntegerField(default=1)

    objects = SplitManager()
    


class SharePrice(models.Model):

    class Meta:
        db_table = 'share_price'
        verbose_name_plural = '06. Share Price'

    id = models.AutoField(primary_key=True)
    share = models.ForeignKey(Share, on_delete=models.PROTECT)
    price = models.DecimalField(
        max_digits=16,
        decimal_places=8,
        verbose_name='Cost per share',
    )
    date = models.DateField()
    history = HistoricalRecords()

    objects = SharePriceManager()


class TransactionType(models.Model):

    class Meta:
        app_label = 'base_info'
        db_table = 'transaction_type'
        
    id = models.AutoField(primary_key=True)
    title = models.CharField(max_length=255, unique=True)

    def __str__(self):
        return self.title


class Portfolio(models.Model):

    class Meta:
        app_label = 'base_info'
        db_table = 'portfolio'

    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=255, unique=True)

    def __str__(self):
        return self.name


class MoneyTransaction(models.Model):

    class Meta:
        db_table = 'money_transaction'
        ordering = ['-date']
        verbose_name_plural = '04. Money Transactions'
        
    id = models.AutoField(primary_key=True)
    date = models.DateField()
    price = models.DecimalField(
        max_digits=13,
        decimal_places=2,
        verbose_name='Cost',
    )
    company = models.ForeignKey(Company, on_delete=models.PROTECT)
    transaction_type = models.ForeignKey(TransactionType, on_delete=models.PROTECT)
    portfolio = models.ForeignKey(Portfolio, on_delete=models.PROTECT)
    comment = models.TextField(max_length=10240, blank=True)
    history = HistoricalRecords()

    def __str__(self):
        return f'{self.company}|{self.date} - {self.price}'

class ShareTransaction(models.Model):
    
    class Meta:
         db_table = 'share_transaction'
         verbose_name_plural = '05. Share Transaction'

    id = models.AutoField(primary_key=True)
    money_transaction = models.ForeignKey(MoneyTransaction, on_delete=models.PROTECT)
    date = models.DateField()
    share = models.ForeignKey(Share, on_delete=models.PROTECT)
    amount = models.IntegerField()
    comment = models.TextField(max_length=10240, blank=True)
    history = HistoricalRecords()

class FairValueMethod(models.Model):

    class Meta:
        db_table = 'fair_value_method'
        verbose_name_plural = '11. Fair Value Method'

    id = models.AutoField(primary_key=True)
    company = models.ForeignKey(Company, on_delete=models.PROTECT)
    name = models.CharField(max_length=255)
    percent = models.IntegerField()
    date = models.DateField()
    history = HistoricalRecords()


class ShareholderList(models.Model):

    class Meta:
        db_table = 'shareholder_list'
        verbose_name_plural = '07. Shareholder List'

    id = models.AutoField(primary_key=True)
    company = models.ForeignKey(Company, on_delete=models.PROTECT)
    date = models.DateField()
    comment = models.TextField(max_length=10240, blank=True)
    history = HistoricalRecords()

    def __str__(self):
        return f"{self.company}|{self.date}"


class Shareholder(models.Model):

    class Meta:
        db_table = 'shareholder'
        verbose_name_plural = '08. Shareholders'
    
    id = models.AutoField(primary_key=True)
    shareholder_list = models.ForeignKey(ShareholderList, on_delete=models.CASCADE)
    contact = models.ForeignKey(Contact, on_delete=models.PROTECT)
    share = models.ForeignKey(Share, on_delete=models.PROTECT)
    amount = models.IntegerField()
    comment = models.TextField(max_length=10240, blank=True)
    option = models.BooleanField(default=True)
    history = HistoricalRecords()

    def __self__(self):
        return f"{self.shareholder_list} - {self.contact}"
