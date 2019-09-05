from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db.models import Sum, Avg
from datetime import date, datetime
# Main products - type (FESX SEP19, EURUSD, OESX SEP19)


class Product(models.Model):

    PRODUCT_TYPE = (
        ('F', 'Future'),
        ('O', 'Option'),
        ('S', 'Spot')
    )

    name = models.CharField(max_length=10)
    productType = models.CharField(max_length=1, choices=PRODUCT_TYPE)
    hedgeSubProductId = models.IntegerField(default=None)
    expiryDisplay = models.CharField(max_length=5, default=None)
    expiryTime = models.DateTimeField(max_length=5, default=None)
    contractSize = models.FloatField()

# Subproducts - components (EURUSD SPOT, OESX SEP19 3200 C, OESX SEP19 3225 P)


class SubProduct(models.Model):

    CALL_PUT = (
        ('C', 'Call'),
        ('P', 'Put')
    )
    EXPIRY_TYPE = (
        ('A', 'American'),
        ('E', 'European')
    )
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    name = models.CharField(max_length=25)
    strike = models.IntegerField(default=None)
    callPut = models.CharField(max_length=1, choices=CALL_PUT, default=None)
    expiryType = models.CharField(max_length=1, choices=EXPIRY_TYPE)


# Price

class StreamPrice(models.Model):
    subProduct = models.OneToOneField(
        SubProduct, on_delete=models.CASCADE, primary_key=True)
    bid = models.FloatField()
    offer = models.FloatField()
    ts = models.FloatField()

# Net position per user and per subproduct


class Greeks(models.Model):
    subProduct = models.OneToOneField(
        SubProduct, on_delete=models.CASCADE, primary_key=True)
    iv = models.FloatField(default=0)
    delta = models.FloatField(default=0)
    gamma = models.FloatField(default=0)
    vega = models.FloatField(default=0)
    theta = models.FloatField(default=0)
    rho = models.FloatField(default=0)
    ts = models.DateTimeField(auto_now_add=True)


class Position(models.Model):
    subProduct = models.ForeignKey(SubProduct, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    buy = models.BooleanField(default=True)
    size = models.IntegerField()
    avgPrice = models.FloatField()
    lastTradeTs = models.DateField(auto_now_add=True)

    class Meta:
        unique_together = (('subProduct', 'user'))
        index_together = (('subProduct', 'user'))


class Pnl(models.Model):
    PRODUCT_TYPE = (
        ('F', 'Future'),
        ('O', 'Option'),
        ('S', 'Spot')
    )

    subProduct = models.ForeignKey(SubProduct, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    ts = models.DateTimeField(auto_now_add=True)
    value = models.FloatField(default=0)
    productType = models.CharField(
        max_length=1, choices=PRODUCT_TYPE)

    # def dailyPnl(self):

    #     dailyPnl = Pnl.objects.filter(user=user).aggregate(Sum('value'))
    #     print(dailyPnl)
    #     return dailyPnl


class Trade(models.Model):
    position = models.ForeignKey(Position, on_delete=models.CASCADE)
    subProduct = models.ForeignKey(SubProduct, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    buy = models.BooleanField(default=True)
    size = models.IntegerField()
    sizeLeft = models.IntegerField()
    price = models.FloatField()
    ts = models.DateTimeField(auto_now_add=True)
    closed = models.BooleanField(default=False)


class Static(models.Model):
    rate = models.FloatField()

    # class Movie(models.Model):
    #     title = models.CharField(max_length=32)
    #     description = models.TextField(max_length=360)

    #     def nbr_ratings(self):
    #         ratings = Rating.objects.filter(movie=self)
    #         return len(ratings)

    #     def avg_rating(self):
    #         sum = 0
    #         ratings = Rating.objects.filter(movie=self)

    #         avg_rating = Rating.objects.filter(movie=self).aggregate(Avg('stars'))
    #         return avg_rating['stars__avg']

    #         # for rating in ratings:
    #         #     sum += rating.stars
    #         # if len(ratings) > 0:
    #         #     return sum / len(ratings)
    #         # else:
    #         #     return 0

    # class Rating(models.Model):
    #     movie = models.ForeignKey(Movie, on_delete=models.CASCADE)
    #     user = models.ForeignKey(User, on_delete=models.CASCADE)
    #     stars = models.IntegerField(
    #         validators=[MinValueValidator(1), MaxValueValidator(5)])

    #     class Meta:
    #         unique_together = (('user', 'movie'))
    #         index_together = (('user', 'movie'))
