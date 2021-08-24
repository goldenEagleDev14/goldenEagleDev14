from odoo import models, fields, api

class project_phase_inherit(models.Model):
    _inherit = 'project.phase'

    company = fields.Many2one('res.company',default=lambda self: self.env.company)
class property_exception_inherit(models.Model):
    _inherit = 'property.exception'

    company = fields.Many2one('res.company',default=lambda self: self.env.company)
class property_category_inherit(models.Model):
    _inherit = 'property.category'

    company = fields.Many2one('res.company',default=lambda self: self.env.company)
class property_type_inherit(models.Model):
    _inherit = 'property.type'

    company = fields.Many2one('res.company',default=lambda self: self.env.company)
class property_location_inherit(models.Model):
    _inherit = 'property.location'

    company = fields.Many2one('res.company',default=lambda self: self.env.company)
class property_finished_inherit(models.Model):
    _inherit = 'property.finished.type'

    company = fields.Many2one('res.company',default=lambda self: self.env.company)
class property_design_inherit(models.Model):
    _inherit = 'property.design'

    company = fields.Many2one('res.company',default=lambda self: self.env.company)
