# Create your views here.
from dataviews.forms import ModeForm, DataViewsWizard

def wizard_view(request, *args, **kwargs):
    return DataViewsWizard([ModeForm for i in range(4)])(request, *args, **kwargs)
