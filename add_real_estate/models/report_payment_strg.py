# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.
import logging
from datetime import timedelta
from functools import partial

import psycopg2
import pytz

from odoo import api, fields, models, tools, _
from odoo.tools import float_is_zero
from odoo.exceptions import UserError
from odoo.http import request
from odoo.osv.expression import AND
import base64

_logger = logging.getLogger(__name__)


class Payment_strg_request(models.AbstractModel):
    _name = 'report.add_real_estate.report_saledetails_test'

    @api.model
    def _get_report_values(self, docids, data=None):
        # data = dict(data or {})
        # data.update(data)

        print("data :: %s",data)
        return data
