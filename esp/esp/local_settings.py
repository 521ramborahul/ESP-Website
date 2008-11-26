""" Local system-specific settings. """
__author__    = "MIT ESP"
__date__      = "$DATE$"
__rev__       = "$REV$"
__license__   = "GPL v.2"
__copyright__ = """
This file is part of the ESP Web Site
Copyright (c) 2008 MIT ESP

The ESP Web Site is free software; you can redistribute it and/or
modify it under the terms of the GNU General Public License
as published by the Free Software Foundation; either version 2
of the License, or (at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program; if not, write to the Free Software
Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA  02110-1301, USA.

Contact Us:
ESP Web Group
MIT Educational Studies Program,
84 Massachusetts Ave W20-467, Cambridge, MA 02139
Phone: 617-253-4882
Email: web@esp.mit.edu
"""

################################################################################
#                                                                              #
#                    Edit this file to override settings in                    #
#                              django_settings.py                              #
#                                                                              #
################################################################################


###########################
# Site identification     #
###########################

SITE_INFO = (1, 'esp.mit.edu', 'Main ESP Site')

# Must be unique for every site hosted
CACHE_PREFIX="ESP"


######################
# File Locations     #
######################

# root directory
PROJECT_ROOT = '/esp/web_git/mit/esp/'

# log directory
LOG_FILE = "/var/log/django/esp_errlog"


###################
# Debug settings  #
###################
DEBUG = False
DISPLAYSQL = False
TEMPLATE_DEBUG = DEBUG
SHOW_TEMPLATE_ERRORS = DEBUG

INTERNAL_IPS = (
    '18.208.0.164',
    '18.187.7.102',
    '71.126.253.25',
    '72.93.219.106',
    '127.0.0.1',
)

################
# Database     #
################

DATABASE_ENGINE = 'postgresql'
DATABASE_NAME = 'django'
DATABASE_HOST = 'localhost'
DATABASE_PORT = '5432'

# Import db username and password
from database_settings import *

##############
# Middleware #
##############

MIDDLEWARE_LOCAL = [
    #(1250, 'esp.middleware.StatsMiddleware'),
]
