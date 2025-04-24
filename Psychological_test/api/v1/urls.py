from django.urls import include, path
from podcast.api.v1.views import PodcastCreateViews
from rest_framework.routers import DefaultRouter
from .views import (
    TestViewSet, CategoryViewSet, QuestionViewSet,
    ChoiceViewSet, UserResponseViewSet, MBTIResultViewSet, CalculateMBTIResult, TestCategoryCreateView,
    TestCategoryListView, TestCategoryUpdateView, TestCategoryDetailView, TestResultUserCreateView,
    TestResultUserListView, TestResultUserDetailView, TestResultByUserListView, TypeTestCreateView, TypeTestListView,
    TypeTestDetailView, TypeTestUpdateView, TypeTestByTitleView, TypeTestByCatView, FinalResultsCreateView,
    FinalResultsListView, FinalResultsDetailView, FinalResultsUpdateView, FinalResultsCatidView ,FinalTestPurchaseView
)
# URL patterns
router = DefaultRouter()
# router.register(r'tests', TestViewSet)
# router.register(r'categories', CategoryViewSet)
# router.register(r'questions', QuestionViewSet)
# router.register(r'choices', ChoiceViewSet)
# router.register(r'user-responses', UserResponseViewSet)
# router.register(r'mbti-results', MBTIResultViewSet)
#

urlpatterns = [
    path('', include(router.urls)),
    path('calculate-mbti/', CalculateMBTIResult.as_view(), name='calculate-mbti'),
    path('category/create', TestCategoryCreateView.as_view(), name='test-category-create'),
    path('category/list', TestCategoryListView.as_view(), name='test-category-list'),
    path('category/detail/<slug>', TestCategoryDetailView.as_view(), name='test-category-detail'),
    path('category/create/update/<slug>', TestCategoryUpdateView.as_view(), name='test-category-update'),
    #test result user
    path('result/create', TestResultUserCreateView.as_view(), name='test-resultuser-create'),
    path('result/list/', TestResultUserListView.as_view(), name='test-resultuser-list'),
    path('result/listuser/<int:user_id>', TestResultByUserListView.as_view(), name='test-resultbyuser-list'),
    path('result/detail/<int:pk>', TestResultUserDetailView.as_view(), name='test-resultuser-detail'),
    #short result
    path('shortresult/create', TypeTestCreateView.as_view(), name='test-shortresult-create'),
    path('shortresult/list', TypeTestListView.as_view(), name='test-shortresultuser-list'),
    path('shortresult/title-list/<title>', TypeTestByTitleView.as_view(), name='test-shorttitle-list'),
    path('shortresult/categoryid-list/<int:category_id>', TypeTestByCatView.as_view(), name='test-title-category_id'),
    path('shortresult/detail/<int:pk>', TypeTestDetailView.as_view(), name='test-shortresultuser-detail'),
    path('shortresult/update/<int:pk>', TypeTestUpdateView.as_view(), name='test-shortresultuser-update'),
    #long result
    path('longresult/create', FinalResultsCreateView.as_view(), name='test-longresult-create'),
    path('longresult/list', FinalResultsListView.as_view(), name='test-longresult-list'),
    path('longresult/detail/<int:pk>', FinalResultsDetailView.as_view(), name='test-longresult-detail'),
    path('longresult/detail-catid/<int:category_id>', FinalResultsCatidView.as_view(), name='test-longresult-catid-detail'),
    path('longresult/update/<int:pk>', FinalResultsUpdateView.as_view(), name='test-longresult-update'),
    #finaly
    path('final-test-purchase/<int:test_category_id>/', FinalTestPurchaseView.as_view(), name='final-test-purchase'),

]