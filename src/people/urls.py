

from .views import LoginView, HomeView, ApplicationView, UserSearchView, \
    UserSearchResultView, LoanView, BillSearchView, BillPayView, SuccessView
import views
from django.conf.urls import url


urlpatterns = [

    url(r'^$', LoginView.as_view(), name='login'),
    url(r'^signup$', views.signUpForm, name='signup'),
    url(r'^registered$', views.signUpSuccess, name='registered'),
    url(r'^login_success$', HomeView.as_view(), name='login_success'),
    url(r'^new_application$', ApplicationView.as_view(), name='new_application'),
    # url(r'^applicationSuccess$', views.applicationSuccess, name='applicationSuccess'),
    url(r'^user_search$', UserSearchView.as_view(), name='user_search'),

    url(r'^user_account/(?P<appid>\S*)$', UserSearchResultView.as_view(), name='user_account'),
    url(r'^logout/$', views.logout_view, name='logout'),

    url(r'^bill_pay/(?P<app_id>\S*)$', BillPayView.as_view(), name='bill_pay'),
    # url(r'^rateofintrest/$', views.submit, name='rate_of_intrest'),
    url(r'^loan$', LoanView.as_view(), name='loan'),
    url(r'^bill_search', BillSearchView.as_view(), name='bill_search'),
    # url(r'^monthbill$', views.monthbill, name='monthbill'),
    # url(r'^bill_paid/(?P<appid>\d+)/(?P<date>\S*)/(?P<samount>\d+)/(?P<total>\d+)/(?P<loanid>\d+)/(?P<rm_pp>\d+)/(?P<intrest>\d+)/(?P<eamount>\d+)/(?P<emi_no>\d+)/$',
    #     views.bill_paid, name='billpaid'),
    url(r'^test',views.test,name='test'),
    url(r'^success/(?P<app_id>\S*)', SuccessView.as_view(), name='success')
]
