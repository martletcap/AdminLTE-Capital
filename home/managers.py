from django.db import models

class SharePriceManager(models.Manager):
    def last_price(self, **kwargs):
        """
        Args:
            kwargs: All filters.
        Returns:
            int: Last price ordered by date or 0.
        """
        last_price = self.filter(**kwargs).order_by('-date')[:1].first()
        if last_price:
            return last_price.price
        return 0
