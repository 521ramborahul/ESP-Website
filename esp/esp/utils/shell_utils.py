'''Things that will be useful to have in shell_plus, which it will auto-import.'''

from django.db.models import F, Q, Count, Avg, Min, Max, Sum

import datetime
import numpy

from esp.utils.query_utils import nest_Q

from esp.program.modules.base import CoreModule, ProgramModuleObj

from esp.accounting.controllers import BaseAccountingController, GlobalAccountingController, IndividualAccountingController
from esp.customforms.DynamicForm import BaseCustomForm, CustomFormHandler, FormStorage, ComboForm, FormHandler
from esp.customforms.DynamicModel import DynamicModelHandler, DMH
from esp.customforms.linkfields import CustomFormsLinkModel, CustomFormsCache
from esp.program.controllers.classchange import ClassChangeController
from esp.program.controllers.classreg import ClassCreationController
from esp.program.controllers.confirmation import ConfirmationEmailController
from esp.program.controllers.consistency import ConsistencyChecker
from esp.program.controllers.lottery import LotteryAssignmentController
from esp.program.controllers.lunch_constraints import LunchConstraintGenerator
from esp.program.controllers.resources import ResourceController
from esp.program.controllers.studentclassregmodule import RegistrationTypeController
from esp.program.controllers.studentregsanity import StudentRegSanityController
from esp.themes.controllers import ThemeController
from esp.users.controllers.usersearch import UserSearchController

# Until accounting_core.models is removed, some of the models we really want
# can get shadowed.
from esp.accounting.models import *
