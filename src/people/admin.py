from django.contrib import admin

# Register your models here.

from .models import *
admin.site.register(Application)
admin.site.register(Bills)
admin.site.register(SavingAccount)
admin.site.register(OrganisationAccount)
admin.site.register(Loan)
admin.site.register(SpecialLoan)