from django.shortcuts import render, HttpResponseRedirect
from .forms import ApplicationForm, LoanForm, SpecialLoanForm, BillSearchForm, LoginForm, SignUpForm, UserSearchForm, UserForm
from .models import Application, Bills, SignUp, SavingAccount, OrganisationAccount, Loan, SpecialLoan
from datetime import datetime
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.views.decorators.cache import cache_control
from django.contrib import auth
from django.contrib.auth import logout
from django.http import *
from django.views.generic import FormView, TemplateView
from multi_form_view import MultiFormView
from django.db import connection

# Create your views here.


def test(request):
    return render(request, "header.html")


class LoginView(FormView):
    template_name = 'login.html'
    form_class = LoginForm

    def form_valid(self, form):
        if form.user_name:
            return HttpResponseRedirect('/people/login_success')
    # def post(self, request, *args, **kwargs):
    #     username = request.POST.get('user_name')
    #     password = request.POST.get('password')
    #
    #     user = User.objects.get(username=username)
    #     if user:
    #         return HttpResponseRedirect('/people/login_success')


class HomeView(LoginView):
    template_name = 'login_success.html'


def logout_view(request):
    logout(request)
    request.session = {}
    return HttpResponseRedirect('/people/')


class UserSearchView(FormView):
    template_name = 'usersearch.html'

    form_class = UserSearchForm

    def form_valid(self, form):
        if form.id_or_full_name:
            return HttpResponseRedirect('/people/user_account/{full}'.format(full=form.id_or_full_name))


class UserSearchResultView(TemplateView,
                           MultiFormView):
    template_name = 'useraccount.html'
    form_classes = {
        'loan_form': LoanForm,
        'specialLoan_form': SpecialLoanForm
    }

    def get_context_data(self, **kwargs):
        context = super(UserSearchResultView, self).get_context_data(**kwargs)
        if kwargs['appid'].isdigit():
            app1 = Application.objects.get(id=kwargs['appid'])
        else:
            app1 = Application.objects.get(full_name=kwargs['appid'])
        useraccount = SavingAccount.objects.filter(appid_id=app1.id).latest('id')
        try:
            loan = Loan.objects.filter(appid_id=app1.id).latest('id')
            context['loan_status'] = loan.status
            special_loan = SpecialLoan.objects.filter(appid_id=app1.id).latest('id')
            context['special_loan_status'] = special_loan.status

        except:
            pass
        context['application_id'] = app1.id
        context['name'] = app1.full_name
        context['balance'] = useraccount.balance

        return context

    def post(self, request, *args, **kwargs):
        try:
            loan_amount = request.POST.get('loan_amount')
            if loan_amount:
                installment_amount = request.POST.get('installment_amount')
                number_of_emi = request.POST.get('number_of_emi')
                rate_of_intrest = request.POST.get('rate_of_intrest')
                loan = Loan.objects.create(appid_id=self.kwargs['appid'], loan_amount=loan_amount,
                                           emi_amount=installment_amount, no_of_emis=number_of_emi,
                                           rate_of_intrest=rate_of_intrest, status=True,
                                           created_at=datetime.now().date())
                loan.save()
            else:
                special_loan_amount = request.POST.get('special_loan_amount')
                special_intrest_amount = request.POST.get('special_intrest_amount')
                special_intrest_rate = request.POST.get('special_rate_of_intrest')
                special_loan = SpecialLoan.objects.create(appid_id=self.kwargs['appid'],
                                                          special_loan_amount=special_loan_amount,
                                                          special_intrest_amount=special_intrest_amount,
                                                          special_intrest_rate=special_intrest_rate,
                                                          status=True,
                                                          created_at=datetime.now().date())
                special_loan.save()
            return HttpResponseRedirect('/people/login_success')
        except Exception as e:
            print e


def signUpForm(request):

    user_form = UserForm()
    form = SignUpForm()
    title = "SignUP"

    context = {
        "title": title,
        "form": form,
        "user_form": user_form
    }

    return render(request, "SignUP.html", context)


def signUpSuccess(request):
    if request.method == 'POST':

        name = request.POST.get('username', '')
        date_of_birth = request.POST.get('date_of_birth', '')
        password = request.POST.get('password', '')
        mobile_no = request.POST.get('mobile_no', '')

        user = User(username=name, password=password)
        user.set_password(password)
        myForm = SignUpForm(request.POST, instance=user)
        if myForm.is_valid():
            user.save()
            signup = SignUp(user_id=user.id, date_of_birth=date_of_birth, mobile_no=mobile_no)
            signup.clean()
            signup.save()
            return render(request, "registered.html", {})

    return signUpForm(request)


class ApplicationView(FormView):
    template_name = 'application.html'
    form_class = ApplicationForm

    def post(self, request, *args, **kwargs):
        try:
            full_name = request.POST.get('full_name', '')
            father_or_husband_name = request.POST.get('father_or_husband_name', '')
            nominee_name = request.POST.get('nominee_name', '')
            date_of_birth = request.POST.get('date_of_birth', '')
            job = request.POST.get('job', '')
            address = request.POST.get('address', '')
            mobile_no = request.POST.get('mobile_no', '')

            app = Application(full_name=full_name, father_or_husband_name=father_or_husband_name,
                              nominee_name=nominee_name,
                              date_of_birth=date_of_birth, job=job, address=address, mobile_no=mobile_no)
            app.save()
            date = datetime.today().date()

            saving_account = SavingAccount(appid_id=app.id, date=date, balance=0)
            saving_account.save()
            return HttpResponseRedirect('/people/success/{app_id}'.format(app_id=app.id))
        except Exception, e:
            print e


class LoanView(FormView):
    template_name = 'loan.html'
    form_class = LoanForm

    def get(self, request, *args, **kwargs):
        return HttpResponseRedirect('/people/loan')


class BillSearchView(FormView):
    template_name = 'bill.html'
    form_class = BillSearchForm

    def form_valid(self, form):
        if form.id_or_full_name:
            return HttpResponseRedirect('/people/bill_pay/{loan_id}'.format(loan_id=form.id_or_full_name))


class BillPayView(TemplateView):
    template_name = 'monthbill.html'

    def get_context_data(self, **kwargs):
        context = super(BillPayView, self).get_context_data(**kwargs)
        try:
            if context['app_id'].isdigit():
                loan = Loan.objects.get(appid_id=context['app_id'])
            else:
                app1 = Application.objects.get(full_name=context['app_id'])
                loan = Loan.objects.get(appid_id=app1.id)
        except Loan.DoesNotExist:
            if context['app_id'].isdigit():
                context['name'] = Application.objects.get(id=context['app_id'])
            else:
                context['name'] = Application.objects.get(full_name=context['app_id'])
            context['share_amount'] = 100
            context['date'] = datetime.now().date()
            context['total'] = context['share_amount']
            context['loan_id'] = None
            return context
        if loan and loan.status:
            try:
                bill = Bills.objects.filter(loanid=loan.id).latest('id')
                if bill:
                    I = bill.rm_amount/(1*100) # 1% interest
                    emi_no = (loan.no_of_emis-(bill.rm_amount/loan.emi_amount))+1
                    rm_pp_amount = bill.rm_amount-loan.emi_amount
                    context['intrest'] = I
                    context['total_emi_no'] = loan.no_of_emis
                    context['emi_no'] = emi_no
                    context['balance_amount'] = rm_pp_amount
                    context['total'] = I + 100 + loan.emi_amount
            except Bills.DoesNotExist:
                I = loan.loan_amount/(1*100)
                context['intrest'] = I
                context['total_emi_no'] = loan.no_of_emis
                context['emi_no'] = 1
                context['balance_amount'] = loan.loan_amount
                context['total'] = I + 100 + loan.emi_amount

            context['emi_amount'] = loan.emi_amount
            context['loan_amount'] = loan.loan_amount
            context['rate'] = 1
            context['share_amount'] = 100
            context['name'] = Application.objects.get(id=loan.appid_id)
            context['date'] = datetime.now().date()
            context['loan_id'] = loan.id
        else:
            if context['app_id'].isdigit():
                context['name'] = Application.objects.get(id=context['app_id'])
            else:
                context['name'] = Application.objects.get(full_name=context['app_id'])
            context['share_amount'] = 100
            context['date'] = datetime.now().date()
            context['total'] = context['share_amount']
            context['loan_id'] = None
        return context

    def post(self, request, *args, **kwargs):
        result = self.get_context_data(**kwargs)
        if result['loan_id'] is not None:
            if result['balance_amount'] == 0:
                loan = Loan.objects.get(id=result['loan_id'])
                loan.status = False
                loan.save()
            bill = Bills.objects.create(paid_emi=result['emi_amount'], total=result['total'],
                                        created_at=result['date'], emi_no=result['emi_no'],
                                        rm_amount=result['balance_amount'],
                                        interest_amount=result['intrest'],
                                        loanid=result['loan_id'])
            bill.save()
        else:
            bill = Bills.objects.create(created_at=result['date'], total=result['total'])
            bill.save()
        if result['app_id'].isdigit():
            saving_account = SavingAccount.objects.get(appid_id=result['app_id'])
        else:
            app1 = Application.objects.get(full_name=result['app_id'])
            saving_account = SavingAccount.objects.get(appid_id=app1.id)
        saving_account.balance += result['share_amount']
        saving_account.date = result['date']
        saving_account.save()
        return HttpResponseRedirect('/people/login_success')


class SuccessView(TemplateView):
    template_name = 'success.html'

    def get_context_data(self, **kwargs):
        context = super(SuccessView, self).get_context_data(**kwargs)
        context['id'] = kwargs['app_id']
        return context