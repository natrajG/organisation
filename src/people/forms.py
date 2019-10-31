__author__ = 'qsslp231'

from bootstrap_datepicker.widgets import DatePicker

from django.utils.translation import ugettext_lazy as _
from django import forms
from .models import *
from django.contrib.auth.models import User
from django.contrib.admin.widgets import AdminDateWidget
from django.contrib.auth import authenticate

from .models import Application


class UserForm(forms.ModelForm):

    class Meta:
        model = User
        fields = ('username', 'password')


class SignUpForm(forms.Form):

    date_of_birth = forms.DateField(label=_("Date Of Birth"))
    mobile_no = forms.IntegerField(label=_("Mobile No"))

    # class Meta:
    #     model = SignUp
    #     fields = (_('date_of_birth'), _('mobile_no'))

    # def clean(self):
    #     print "CLeaning"
    #     raise forms.ValidationError("Testing")


class LoginForm(forms.Form):

    user_name = forms.CharField(label=_("User Name"), max_length=10)
    password = forms.CharField(label=_("Password"), widget=forms.PasswordInput())

    def __init__(self, *args, **kwargs):
        super(LoginForm, self).__init__(*args, **kwargs)

    def clean(self):
        if self.errors:
            return
        username = self.cleaned_data.get('user_name')
        password = self.cleaned_data.get('password')

        if username and password:
            user = authenticate(username=username, password=password)
            if not user:
                raise forms.ValidationError(_('Invalid Username or Password'))
            self.user_name = user
            return self.user_name


class UserSearchForm(forms.Form):
    id_or_full_name = forms.CharField(
        label=_("ID/Full Name"),
        required=False,
        widget=forms.TextInput(
            attrs={'placeholder': 'Number/Name', 'type': 'char'})
    )

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
                return
            if app1 and user_account:
                return self.id_or_full_name

        except Application.DoesNotExist:
            self.add_error('id_or_full_name', _('No Application Records Found'))


class DateInput(forms.DateInput):
    input_type = 'date'


class ApplicationForm(forms.Form):

        full_name = forms.CharField(label=_('Full name'))
        father_or_husband_name= forms.CharField(label=_('Father or Husband Name'))
        nominee_name = forms.CharField(label= _('Nominee Name'))
        date_of_birth = forms.DateField(label=_('Date of Birth'), widget=DateInput)
        job = forms.CharField(label=_('Job'))
        address = forms.CharField(label=_('Address'))
        mobile_no = forms.CharField(label=_('Mobile No'))


class LoanForm(forms.Form):
    loan_amount = forms.CharField(label=_("Loan Amount"))
    installment_amount = forms.CharField(label=_("Installment Amount"))
    number_of_emi = forms.CharField(label=_("Number Of Emi"))
    rate_of_intrest = forms.IntegerField(label=_("Rate Of Intrest"))


class SpecialLoanForm(forms.Form):
    special_loan_amount = forms.CharField(label=_("Special Loan Amount"))
    special_rate_of_intrest = forms.IntegerField(label=_("special Rate Of Intrest"))
    special_intrest_amount = forms.CharField(label=_("Special Intrest Amount"))


class AccountStatementForm(forms.Form):
    type = forms.ChoiceField(label=_('type'),
                             choices=[('loan', _('loan')),
                                      ('short appu', _('short appu')),
                                      ('monthly/yearly', _('monthly/yearly')),
                                      ('karchulu', _('karchulu')),
                                      ('labam_vivaralu', _('labam_vivaralu'))])
    from_date = forms.DateField(label=_('From Date'), widget=DateInput)
    to_date = forms.DateField(label=_('To Date'), widget=DateInput)


class ExpenditureForm(forms.Form):
    purpose = forms.CharField(label=_('purpose'))
    amount = forms.CharField(label=_('expense'))
    date = forms.DateField(label=_('Date'), widget=DateInput)


class TotalProfitForm(forms.Form):
    total_profit_amount = forms.CharField(label=_('expense'))


class BillSearchForm(forms.Form):
    id_or_full_name = forms.CharField(label=_("ID/Full Name"), required=False, widget=forms.TextInput(
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


