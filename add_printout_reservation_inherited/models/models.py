from odoo import api, fields, models
class res_company_inherited(models.Model):
    _inherit = 'res.company'
    company_details = fields.Text('بيانات الشركه')
