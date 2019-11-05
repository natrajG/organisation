import csv
from django.shortcuts import render, HttpResponseRedirect
from .forms import (ApplicationForm, LoanForm, SpecialLoanForm, BillSearchForm,
                    LoginForm, SignUpForm, UserSearchForm, UserForm, AccountStatementForm,
                    ExpenditureForm, TotalProfitForm)
from .models import Application, Bills, SignUp, SavingAccount, OrganisationAccount,\
    Loan, SpecialLoan, ExpenditureModel
from datetime import datetime
from django.contrib.auth.models import User
from django.utils.translation import ugettext_lazy as _

from django.views.decorators.cache import cache_control
from django.contrib.auth import login, logout
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
        login(self.request, form.user_name)
        self.request.session.set_expiry(900)

        return HttpResponseRedirect('/people/login_success')


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
        'specialLoan_form': SpecialLoanForm,
        'account_statement_form': AccountStatementForm
    }

    def get_context_data(self, **kwargs):
        context = super(UserSearchResultView, self).get_context_data(**kwargs)
        if kwargs['appid'].isdigit():
            app1 = Application.objects.get(id=kwargs['appid'])
        else:
            app1 = Application.objects.get(full_name=kwargs['appid'])
        useraccount = SavingAccount.objects.filter(appid_id=app1.id).latest('id')
        try:
            loan = Loan.objects.filter(appid_id=app1.id)
            if loan and loan.latest('id').status:
                context['loan_amount'] = loan.latest('id').loan_amount
                context['loan_status'] = loan.latest('id').status
            else:
                context['loan_amount'] = 0.0
            special_loan = SpecialLoan.objects.filter(appid_id=app1.id)
            if special_loan and special_loan.latest('id').status:
                context['sp_loan_amount'] = special_loan.latest('id').special_loan_amount
                context['special_loan_status'] = special_loan.latest('id').status
            else:
                context['sp_loan_amount'] = 0.0

        except:
            pass
        context['application_id'] = app1.id
        context['name'] = app1.full_name
        context['balance'] = useraccount.balance
        from django.core.urlresolvers import reverse_lazy
        context['form_validation_url'] = reverse_lazy('loan_amount_validation')

        return context

    def post(self, request, *args, **kwargs):
        response = HttpResponse(content_type='text/csv')
        writer = csv.writer(response)
        response['Content-Disposition'] = (
            'attachment; filename='"%s_statement_List.xls"
            % self.kwargs['appid'])
        try:
            loan_amount = request.POST.get('loan_amount')
            special_loan_amount = request.POST.get('special_loan_amount')
            statement_type = request.POST.get('type')
            from_date = request.POST.get('from_date')
            to_date = request.POST.get('to_date')
            if not statement_type:
                org_account = OrganisationAccount.objects.latest('id')
            if loan_amount:
                if org_account.balance < float(loan_amount):
                    raise ValueError("OrganisationAccount Balance is only %s" % org_account.balance)
                installment_amount = request.POST.get('installment_amount')
                number_of_emi = request.POST.get('number_of_emi')
                rate_of_intrest = request.POST.get('rate_of_intrest')
                loan = Loan.objects.create(appid_id=self.kwargs['appid'], loan_amount=loan_amount,
                                           emi_amount=installment_amount, no_of_emis=number_of_emi,
                                           rate_of_intrest=rate_of_intrest, status=True,
                                           created_at=datetime.now().date())
                loan.save()
                org_account.balance = org_account.balance - float(loan_amount)
                org_account.save()
            elif special_loan_amount:
                if org_account.balance < float(special_loan_amount):
                    raise
                special_intrest_amount = request.POST.get('special_intrest_amount')
                special_intrest_rate = request.POST.get('special_rate_of_intrest')
                special_loan = SpecialLoan.objects.create(appid_id=self.kwargs['appid'],
                                                          special_loan_amount=special_loan_amount,
                                                          special_intrest_amount=special_intrest_amount,
                                                          special_intrest_rate=special_intrest_rate,
                                                          status=True,
                                                          created_at=datetime.now().date())
                special_loan.save()
                org_account.balance = org_account.balance - float(special_loan_amount)
                org_account.save()
            elif from_date and to_date:
                if statement_type == 'loan':
                    loan_details = Loan.objects.filter(appid_id=self.kwargs['appid'],
                                                       created_at__lte=to_date,
                                                       created_at__gte=from_date)
                    writer.writerow([_('Date'), _('Loan Amount'), _('emi amount'),
                                     _('total_emi_no'), _('Rate Of Intrest'), _('status')])
                    for loan in loan_details:
                        var = (loan.created_at, loan.loan_amount, loan.emi_amount,
                               loan.no_of_emis, loan.rate_of_intrest, loan.status)
                        writer.writerow(var)
                elif statement_type == 'short appu':
                    special_loan_details = SpecialLoan.objects.filter(appid_id=self.kwargs['appid'],
                                                              created_at__lte=to_date,
                                                              created_at__gte=from_date)
                    writer.writerow([_('Date'),_('specialloan'), _('special Rate Of Intrest'),
                                     _('special_money'), _('status')])

                    for special_loan in special_loan_details:
                        var = (special_loan.created_at, special_loan.special_loan_amount,
                               special_loan.special_intrest_rate, special_loan.special_intrest_amount,
                               special_loan.status)
                        writer.writerow(var)
                else:
                    writer.writerow([_('bill no'), _('bill date'), _('sharemoney'), _('emi amount'),
                                     _('intrest_mon'), _('specialloan'), _('special_money'),
                                     _('fine'), _('remaining debt'), _('full pay'), _('Total')])
                    try:
                        bills = Bills.objects.filter(appid=self.kwargs['appid'],
                                                     created_at__lte=to_date,
                                                     created_at__gte=request.POST.get('from_date'))
                        for bill in bills:
                            var = (bill.id, bill.created_at, bill.share_amount, bill.paid_emi, bill.interest_amount,
                                   bill.special_loan_amount, bill.special_intrest, bill.penality,
                                   bill.rm_amount, bill.full_paid, bill.total)
                            writer.writerow(var)
                    except Exception as e:
                        print e
                return response
            return HttpResponseRedirect('/people/login_success')
        except OrganisationAccount.DoesNotExist:
            raise ValueError("Poll does not exist")


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
        myForm = SignUpForm(request.POST)
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
            from django.urls import reverse
            if len(mobile_no) != 10:
                raise Exception('please enter 10 digit mobile number')

            app = Application(full_name=full_name, father_or_husband_name=father_or_husband_name,
                              nominee_name=nominee_name,
                              date_of_birth=date_of_birth, job=job, address=address, mobile_no=mobile_no)
            app.save()
            date = datetime.today().date()

            saving_account = SavingAccount(appid_id=app.id, date=date, balance=0)
            saving_account.save()
            return HttpResponseRedirect('/people/success/{app_id}'.format(app_id=app.id))
        except ValueError:
            return HttpResponse('<h1>please enter 10 digit mobile number</h1>')


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
                loan = Loan.objects.filter(appid_id=context['app_id']).latest('id')
                special_loan = SpecialLoan.objects.filter(appid_id=context['app_id'])
            else:
                app1 = Application.objects.get(full_name=context['app_id'])
                loan = Loan.objects.filter(appid_id=app1.id).latest('id')
                special_loan = SpecialLoan.objects.filter(appid_id=app1.id)

        except Loan.DoesNotExist:
            if context['app_id'].isdigit():
                context['name'] = Application.objects.get(id=context['app_id'])
            else:
                context['name'] = Application.objects.get(full_name=context['app_id'])
            if self.request.POST.get('share_amount'):
                context['share_amount'] = float(self.request.POST.get('share_amount'))
            else:
                context['share_amount'] = 200
            context['date'] = datetime.now().date()
            # context['total'] = context['share_amount']
            context['loan_id'] = None
            context['sp_loan_id'] = None
            return context
        if special_loan and special_loan.latest('id').status:
            context['special_loan_amount'] = special_loan.latest('id').special_loan_amount
            context['special_intrest'] = special_loan.latest('id').special_intrest_amount
            context['sp_loan_id'] = special_loan.latest('id').id
        else:
            context['sp_loan_id'] = None
        if loan and loan.status:
            try:
                bill = Bills.objects.filter(loanid=loan.id).latest('id')
                if bill:
                    I = (bill.rm_amount - bill.full_paid)/(1*100) # 1% interest
                    emi_no = (loan.no_of_emis-(bill.rm_amount/loan.emi_amount))+1
                    rm_pp_amount = (bill.rm_amount-loan.emi_amount) - bill.full_paid
                    context['intrest'] = I
                    context['total_emi_no'] = loan.no_of_emis
                    context['emi_no'] = emi_no
                    context['paid_loan_amount'] = (loan.loan_amount - bill.rm_amount) + bill.full_paid
                    context['remaining_debt'] = rm_pp_amount
                    # context['total'] = I + 200 + loan.emi_amount
            except Bills.DoesNotExist:
                I = loan.loan_amount/(1*100)
                context['intrest'] = I
                context['total_emi_no'] = loan.no_of_emis
                context['emi_no'] = 1
                context['remaining_debt'] = loan.loan_amount - loan.emi_amount
                context['paid_loan_amount'] = 0
                # context['total'] = I + 200 + loan.emi_amount

            context['emi_amount'] = loan.emi_amount
            context['loan_amount'] = loan.loan_amount
            context['rate'] = 1
            if self.request.POST.get('share_amount'):
                context['share_amount'] = float(self.request.POST.get('share_amount'))
            else:
                context['share_amount'] = 200
            context['name'] = Application.objects.get(id=loan.appid_id)
            context['date'] = datetime.now().date()
            context['loan_id'] = loan.id
        else:
            if context['app_id'].isdigit():
                context['name'] = Application.objects.get(id=context['app_id'])
            else:
                context['name'] = Application.objects.get(full_name=context['app_id'])
            if self.request.POST.get('share_amount'):
                context['share_amount'] = float(self.request.POST.get('share_amount'))
            else:
                context['share_amount'] = 200
            context['date'] = datetime.now().date()
            # context['total'] = context['share_amount']
            context['loan_id'] = None
        return context

    def post(self, request, *args, **kwargs):
        result = self.get_context_data(**kwargs)
        special_loan_amount = request.POST.get('special_loan_amount')
        special_intrest = request.POST.get('special_intrest')
        penality = request.POST.get('penality')
        if not result['app_id'].isdigit():
            result['app_id'] = Application.objects.get(full_name=result['app_id']).id
        full_paid = request.POST.get('full_paid')
        total_amount = request.POST.get('total_amount')
        if result['sp_loan_id'] is not  None:
            sp_loan = SpecialLoan.objects.get(id=result['sp_loan_id'])
            sp_loan.status = False
            sp_loan.save()
        if result['loan_id'] is not None:
            if result['remaining_debt'] == 0:
                loan = Loan.objects.get(id=result['loan_id'])
                loan.status = False
                loan.save()
            bill = Bills.objects.create(paid_emi=result['emi_amount'], total=total_amount,
                                        created_at=result['date'], emi_no=result['emi_no'],
                                        rm_amount=result['remaining_debt'],
                                        interest_amount=result['intrest'],
                                        loanid=result['loan_id'],
                                        appid_id=result['app_id'],
                                        special_loan_amount=special_loan_amount if special_loan_amount else 0,
                                        special_intrest=special_intrest if special_intrest else 0,
                                        penality=penality if penality else 0,
                                        full_paid=full_paid if full_paid else 0,
                                        share_amount=result['share_amount'])
        else:
            bill = Bills.objects.create(appid_id=result['app_id'], share_amount=result['share_amount'],created_at=result['date'], total=total_amount)
        if result['app_id'].isdigit():
            saving_account = SavingAccount.objects.get(appid_id=result['app_id'])
        else:
            app1 = Application.objects.get(full_name=result['app_id'])
            saving_account = SavingAccount.objects.get(appid_id=app1.id)
        saving_account.balance += float(result['share_amount'])
        saving_account.date = result['date']
        saving_account.save()
        try:
            org_acc = OrganisationAccount.objects.latest('id')
            orgacc = OrganisationAccount.objects.create(billid=bill,
                                                        bill_amount=total_amount,
                                                        balance=org_acc.balance + float(total_amount))
            orgacc.save()
        except OrganisationAccount.DoesNotExist:
            orgacc = OrganisationAccount.objects.create(billid=bill,
                                                        bill_amount=total_amount,
                                                        balance=float(total_amount))
            orgacc.save()
        bill.save()
        return HttpResponseRedirect('/people/login_success')


class SuccessView(TemplateView):
    template_name = 'success.html'

    def get_context_data(self, **kwargs):
        context = super(SuccessView, self).get_context_data(**kwargs)
        context['id'] = kwargs['app_id']
        return context


class GenerateStatementView(TemplateView,
                            MultiFormView):
    template_name = 'statement.html'
    form_classes = {
        'expenditure_form': ExpenditureForm,
        'account_statement_form': AccountStatementForm,
        'total_profit_form': TotalProfitForm
    }

    def get_context_data(self, **kwargs):
        context = super(GenerateStatementView, self).get_context_data(**kwargs)
        try:
            org_acc = OrganisationAccount.objects.latest('id')
            context['balance'] = org_acc.balance
        except OrganisationAccount.DoesNotExist:
            context['balance'] = 0.00
        return context

    def post(self, request, *args, **kwargs):
        response = HttpResponse(content_type='text/csv')
        writer = csv.writer(response)

        response['Content-Disposition'] = (
            'attachment; filename='"%s_%s_statement_List.xls"
            % (request.POST.get('from_date'), request.POST.get('to_date')))
        statement_type = request.POST.get('type')
        from_date = request.POST.get('from_date')
        to_date = request.POST.get('to_date')
        if from_date and to_date:
            if statement_type == 'loan':
                loan_details = Loan.objects.filter(created_at__lte=to_date,
                                                   created_at__gte=from_date)
                writer.writerow([_('Date'), _('App.No:'), _('Loan Amount'), _('emi amount'),
                                 _('total_emi_no'), _('Rate Of Intrest'), _('status')])
                for loan in loan_details:
                    var = (loan.created_at, loan.appid, loan.loan_amount, loan.emi_amount,
                           loan.no_of_emis, loan.rate_of_intrest, loan.status)
                    writer.writerow(var)

            elif statement_type == 'short appu':
                special_loan_details = SpecialLoan.objects.filter(created_at__lte=to_date,
                                                                  created_at__gte=from_date)
                writer.writerow([_('Date'), _('App.No:'), _('specialloan'), _('special Rate Of Intrest'),
                                 _('special_money'), _('status')])

                for special_loan in special_loan_details:
                    var = (special_loan.created_at, special_loan.appid, special_loan.special_loan_amount,
                           special_loan.special_intrest_rate, special_loan.special_intrest_amount,
                           special_loan.status)
                    writer.writerow(var)
            elif statement_type == 'karchulu':
                writer.writerow([_('Date'), _('karchulu'), _('Total')])
                exp_amount = ExpenditureModel.objects.filter(created_at__lte=request.POST.get('to_date'),
                                                             created_at__gte=request.POST.get('from_date'))
                for exp in exp_amount:
                    var = (exp.created_at,exp.name,exp.amount)
                    writer.writerow(var)
            elif statement_type == 'labam_vivaralu':
                writer.writerow([_('intrest_mon'), _('special_money'),
                                 _('fine')])
                bills = Bills.objects.filter(created_at__lte=request.POST.get('to_date'),
                                             created_at__gte=request.POST.get('from_date'))
                for bill in bills:
                    var = (bill.interest_amount,bill.special_intrest, bill.penality)
                    writer.writerow(var)
            else:
                writer.writerow([_('bill no'), _('bill date'), _('sharemoney'), _('emi amount'),
                                 _('intrest_mon'), _('specialloan'), _('special_money'),
                                 _('fine'), _('remaining debt'), _('full pay'), _('Total')])
                bills = Bills.objects.filter(created_at__lte=request.POST.get('to_date'),
                                            created_at__gte=request.POST.get('from_date'))
                for bill in bills:
                    var = (bill.id, bill.created_at, bill.share_amount, bill.paid_emi, bill.interest_amount,
                           bill.special_loan_amount, bill.special_intrest, bill.penality,
                           bill.rm_amount, bill.full_paid, bill.total)
                    writer.writerow(var)
        elif request.POST.get('date'):
            exp_amount = ExpenditureModel.objects.create(name=request.POST.get('purpose'),
                                                         amount=request.POST.get('amount'),
                                                         created_at=request.POST.get('date'))
            exp_amount.save()
            org_acc = OrganisationAccount.objects.latest('id')
            org_acc.balance = org_acc.balance - float(exp_amount.amount)
            org_acc.save()
        elif request.POST.get('total_profit_amount'):
            profit = request.POST.get('total_profit_amount')
            save_acc = SavingAccount.objects.all()
            for acc in save_acc:
                acc.balance += float(profit)
                acc.save()
            org_acc = OrganisationAccount.objects.latest('id')
            org_acc.balance = org_acc.balance - float(profit)
            org_acc.save()
        return response


def get_org_account_balance(request):
    data = {}
    loan_amount = request.GET.get('loan_amount', None)
    try:
        if loan_amount:
            org_account = OrganisationAccount.objects.latest('id')
            if org_account.balance < float(loan_amount):
                data = {
                    "message": _(
                        "Organisation Account Balance is only %s"
                        % org_account.balance)}
        return JsonResponse(data)

    except OrganisationAccount.DoesNotExist:
        data = {'message': _("No Balance in Organisation Account")}
        return JsonResponse(data)


