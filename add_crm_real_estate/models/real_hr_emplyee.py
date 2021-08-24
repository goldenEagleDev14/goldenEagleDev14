# -*- coding: utf-8 -*-


from openerp import models, fields, api, _

class ProjectProject(models.Model):
    _inherit='hr.employee'

    is_project_owner = fields.Boolean(related="department_id.is_project_owner",string="Project Owner",default=False  )
