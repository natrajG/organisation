__author__ = 'qsslp231'

from bootstrap_datepicker.widgets import DatePicker

from django.utils.translation import ugettext_lazy as _
from django import forms
from .models import *
from django.contrib.auth.models import User
from django.contrib.admin.widgets import AdminDateWidget

from .models import Application


class UserForm(forms.ModelForm):

    class Meta:
        model = User
        fields = ('username', 'password')


class SignUpForm(forms.Form):

    date_of_birth = forms.DateField(label=_("date_of_birth"))
    mobile_no = forms.IntegerField(label=_("mobile_no"))

    # class Meta:
    #     model = SignUp
    #     fields = (_('date_of_birth'), _('mobile_no'))

    # def clean(self):
    #     print "CLeaning"
    #     raise forms.ValidationError("Testing")


class LoginForm(forms.Form):

    user_name = forms.CharField(label=_("user_name"), max_length=10)
    password = forms.CharField(label=_("password"), widget=forms.PasswordInput())

    # def clean(self):
    #     if self.errors:
    #         return
    #     try:
    #         data = self.cleaned_data
    #         username = data.get('user_name')
    #         password = data.get('password')
    #         us = User.objects.get(username=username)
    #         if us:
    #             us.password == password
    #             self.user_name = username
    #             return self.user_name
    #     except User.DoesNotExist:
    #         self.add_error('user_name', _('User Name or Password Invalid'))


class UserSearchForm(forms.Form):
    id_or_full_name = forms.CharField(label=_("id_or_full_name"), required=False, widget=forms.TextInput(
        attrs={'placeholder': 'Number/Name', 'type': 'char'}))

    def clean_id_or_full_name(self):
        return self.cleaned_data.get('id_or_full_name')

    def clean(self):
        if self.errors:
            return
        try:
            data = self.cleaned_data
            input_data = data.get('id_or_full_name')
            if input_data:
                if input_data.isdigit():
                    app1 = Application.objects.get(id=input_data)
                    user_account = SavingAccount.objects.filter(appid_id=app1.id).latest('id')
                    self.id_or_full_name = input_data
                else:
                    app1 = Application.objects.get(full_name=input_data)
                    user_account = SavingAccount.objects.filter(appid_id=app1.id).latest('id')
                    self.id_or_full_name = input_data
            else:
                self.add_error(
                    'id_or_full_name', _('Enter Application Number Or Full Name'))
            if app1 and user_account:
                return self.id_or_full_name

        except Application.DoesNotExist:
            self.add_error('id_or_full_name', _('No Application Records Found'))


class ApplicationForm(forms.Form):

        full_name = forms.CharField(label=_('full_name'))
        father_or_husband_name= forms.CharField(label=_('father_or_husband_name'))
        nominee_name = forms.CharField(label= _('nominee_name'))
        date_of_birth = forms.DateField(label=_('date_of_birth'),
                                        widget=forms.TextInput(attrs=
                                {
                                    'class':'datepicker'
                                }))
        job = forms.CharField(label=_('job'))
        address = forms.CharField(label=_('address'))
        mobile_no = forms.IntegerField(label=_('mobile_no'))


class LoanForm(forms.Form):
    loan_amount = forms.CharField(label=_("loan_amount"))
    installment_amount = forms.CharField(label=_("installment_amount"))
    number_of_emi = forms.CharField(label=_("number_of_emi"))
    rate_of_intrest = forms.IntegerField(label=_("rate_of_intrest"))


class SpecialLoanForm(forms.Form):
    special_loan_amount = forms.CharField(label=_("special_loan_amount"))
    special_rate_of_intrest = forms.IntegerField(label=_("special_rate_of_intrest"))
    special_intrest_amount = forms.CharField(label=_("special_intrest_amount"))


class BillSearchForm(forms.Form):
    id_or_full_name = forms.CharField(label=_("id_or_full_name"), required=False, widget=forms.TextInput(
        attrs={'placeholder': 'Number/Name', 'type': 'char'}))

    def clean_id_or_full_name(self):
        return self.cleaned_data.get('id_or_full_name')

    def clean(self):
        if self.errors:
            return
        try:
            data = self.cleaned_data
            input_data = data.get('id_or_full_name')
            if input_data:
                if input_data.isdigit():
                    try:
                        app1 = Application.objects.get(id=input_data)
                        self.id_or_full_name = app1.id
                        return self.id_or_full_name
                    except Application.DoesNotExist:
                            self.add_error(
                                'id_or_full_name', _('No Application with this Number')
                            )
                else:
                    try:
                        app1 = Application.objects.get(full_name=input_data)
                        self.id_or_full_name = app1.full_name
                        return self.id_or_full_name
                    except Application.DoesNotExist:
                        self.add_error(
                            'id_or_full_name', _('No Application with this Name')
                        )
            else:
                self.add_error(
                    'id_or_full_name', _('Enter Application Number Or Full Name'))

        except Exception as e:
            self.add_error('id_or_full_name', _('Something went Horribly Wrong'))


