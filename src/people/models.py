from django.db import models
from django.contrib.auth.models import User
from django.utils.translation import ugettext as _


# Create your models here.

class SignUp(models.Model):
    user = models.OneToOneField(User)
    date_of_birth = models.DateField()
    mobile_no = models.CharField(max_length=10)

    def __unicode__(self):
        return self.user.name


class Application(models.Model):
    full_name = models.CharField(max_length=40, verbose_name=_('full_name'))
    father_or_husband_name = models.CharField(max_length=20)
    nominee_name = models.CharField(max_length=20)
    date_of_birth = models.DateField()
    job = models.CharField(max_length=20)
    address = models.CharField(max_length=20)
    mobile_no = models.CharField(max_length=10)

    def __unicode__(self):
        return self.full_name


class Loan(models.Model):
    appid = models.ForeignKey(Application, related_name='apploan')
    loan_amount = models.IntegerField(default=0)
    emi_amount = models.IntegerField(default=0)
    no_of_emis = models.IntegerField(default=0)
    rate_of_intrest = models.FloatField(default=0.0)
    status = models.BooleanField(default=False)
    created_at = models.DateField(default=None)


class SpecialLoan(models.Model):
    appid = models.ForeignKey(Application, related_query_name='appsploan')
    special_loan_amount = models.IntegerField(default=0)
    special_intrest_amount = models.IntegerField(default=0)
    special_intrest_rate = models.FloatField(default=0.0)
    status = models.BooleanField(default=False)
    created_at = models.DateField(default=None)


class Bills(models.Model):
    loanid = models.IntegerField(default=0)
    created_at = models.DateField(default=None)
    total = models.CharField(max_length=20)
    paid_emi = models.IntegerField(default=0)
    emi_no = models.IntegerField(default=0)
    rm_amount = models.IntegerField(default=0)
    interest_amount = models.FloatField(default=0.0)


class SavingAccount(models.Model):
    appid = models.ForeignKey(Application, related_name='appacount')
    date = models.DateField()
    balance = models.FloatField(default=0.0)


class OrganisationAccount(models.Model):
    billid = models.ForeignKey(Bills, related_name='bill')
    bill_amount = models.FloatField(default=0.0)
    balance = models.FloatField(default=0.0)