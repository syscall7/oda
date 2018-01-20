from django.conf.urls import url, include
from rest_framework import routers
from rest_framework.schemas import get_schema_view
from oda.apps.rest import views

router = routers.DefaultRouter()
router.register(r'usergroups', views.UserGroupViewSet, base_name="usergroup")
router.register(r'masters', views.OdaMasterViewSet, base_name='masters')
router.register(r'comments', views.CommentViewSet, base_name="comments")
router.register(r'sections', views.SectionsViewSet, base_name="sections")
router.register(r'parcels', views.ParcelsViewSet, base_name="parcels")
router.register(r'displayunits', views.DisplayUnitsViewSet, base_name="displayunits")
router.register(r'strings', views.StringsViewSet, base_name="strings")
router.register(r'symbols', views.SymbolsViewSet, base_name="symbols")
router.register(r'operations', views.OperationsViewSet, base_name="operations")
router.register(r'functions', views.FunctionViewSet, base_name="functions")
router.register(r'labels', views.LabelsViewSet, base_name='labels')
router.register(r'binarystrings', views.BinaryStringViewSet, base_name="binarystrings")
router.register(r'options', views.OptionsViewSet, base_name="options")
# router.register(r'odaoptions', views.OdaOptionsViewSet, base_name="odaoptions")
router.register(r'find', views.FindViewSet, base_name="find")
router.register(r'cstructs', views.CStructsViewSet, base_name='cstructs')
router.register(r'definedData', views.DefinedDataViewSet, base_name='definedData')
router.register(r'cstructfieldtypes', views.CStructFieldTypesViewSet,
                base_name='cstructfieldtypes')
router.register(r'sandbox', views.SandboxViewSet, base_name="sandbox")
router.register(r'disassembler', views.DisassemblerViewSet, base_name="disassembler")
router.register(r'user', views.UserViewSet, base_name="user")

#router.register(r'superchunks', views.SuperChunksViewSet, base_name="superchunks")

# Wire up our API using automatic URL routing.
# Additionally, we include login URLs for the browseable API.
urlpatterns = [
    url(r'^', include(router.urls)),
    url(r'^load', views.ODBLoadView.as_view(), name='odb_loader'),
    url(r'^share$', views.ShareView.as_view(), name='share_api'),
    url(r'^graph$', views.GraphView.as_view(), name='graphview'),
    url(r'^decompiler$', views.DecompilerView.as_view(), name='decompilerview'),
    url(r'^api-auth/', include('rest_framework.urls', namespace='rest_framework')),
]
