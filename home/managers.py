from django.db import models
from django.db.models import F

class SharePriceManager(models.Manager):
    def last_price(self, **kwargs):
        """
        Args:
            kwargs: All filters.
        Returns:
            Last price ordered by date or 0.
        """
        last_price = self.filter(**kwargs).order_by('-date')[:1].first()
        if last_price:
            return last_price.price
        return 0


class SplitManager(models.Manager):
    def cof(self, **kwargs):
        """
        Args:
            kwargs: All filters.
        Returns:
            Coefficient of all splits.    
        """
        cof = 1
        splits = self.filter(**kwargs).annotate(
            cof = F('after')/F('before'),
        ).values_list('cof')
        for split in splits:
            cof *= split[0]
        return cof