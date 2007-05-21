from django.db.models import ForeignKey, Field
from django.conf import settings
from esp.db.forms import AjaxForeignKeyFormField


class AjaxForeignKey(ForeignKey):

    def __init__(self, *args, **kwargs):
        kwargs['raw_id_admin'] = False
        ForeignKey.__init__(self, *args, **kwargs)


    def get_manipulator_fields(self, *args, **kwargs):
        return [AjaxForeignKeyFormField(field_name = self.name,
                                        field      = self)]
