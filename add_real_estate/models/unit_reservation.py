# -*- coding: utf-8 -*-
from odoo import api, fields, models
import datetime
from datetime import datetime, date,timedelta
from odoo.tools.translate import _
import calendar
from odoo.exceptions import UserError, AccessError
import xlrd
import tempfile
import binascii
from operator import attrgetter
import logging

LOGGER = logging.getLogger(__name__)

class unit_reservation(models.Model):
    _name = 'unit.reservation'
    _description = "Property Reservation"
    _inherit = ['mail.thread', 'mail.activity.mixin']

