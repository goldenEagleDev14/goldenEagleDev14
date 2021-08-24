# -*- coding: utf-8 -*-


from openerp import models, fields, api, _

class ProjectProject(models.Model):
    _inherit='hr.department'

    is_project_owner = fields.Boolean(string="Project Owner",default=False  )
