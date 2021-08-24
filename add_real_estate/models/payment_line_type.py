# -*- coding: utf-8 -*-

from babel.dates import format_date
from datetime import date, datetime
from dateutil.relativedelta import relativedelta
import json

from odoo import api, fields, models, _
from odoo.exceptions import AccessError, UserError
from odoo.release import version
from odoo.tools import DEFAULT_SERVER_DATE_FORMAT as DF

class PaymentLineType(models.Model):
    _name = "payment.line.type"

    name = fields.Char(string="", required=True, )