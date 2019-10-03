

from .views import LoginView, HomeView, ApplicationView, UserSearchView, \
    UserSearchResultView, BillSearchView, BillPayView, SuccessView, GenerateStatementView
import views
from django.conf.urls import url, include
from django.contrib.auth import views as auth_views

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
    url(r'^bill_search', BillSearchView.as_view(), name='bill_search'),
    url(r'^get_statements', GenerateStatementView.as_view(), name='get_statements'),
    # url(r'^monthbill$', views.monthbill, name='monthbill'),
    # url(r'^bill_paid/(?P<appid>\d+)/(?P<date>\S*)/(?P<samount>\d+)/(?P<total>\d+)/(?P<loanid>\d+)/(?P<rm_pp>\d+)/(?P<intrest>\d+)/(?P<eamount>\d+)/(?P<emi_no>\d+)/$',
    #     views.bill_paid, name='billpaid'),
    url(r'^test',views.test,name='test'),
    url(r'^success/(?P<app_id>\S*)', SuccessView.as_view(), name='success'),
    url(r'^login/$', auth_views.login, name='login'),
    url(r'^logout/$', auth_views.logout, name='logout'),
    url(r'^oauth/', include('social_django.urls', namespace='social')),
]
