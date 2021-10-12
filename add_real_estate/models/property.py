# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import ValidationError,UserError
from datetime import date
from datetime import datetime

import logging
_logger = logging.getLogger(__name__)

class ProductTemplate(models.Model):
    _inherit = 'product.template'

    @api.model
    def _get_product_template_type(self):
        res = super(ProductTemplate, self)._get_product_template_type()
        if 'property' not in [item[0] for item in res]:
            res.append(('property', _('Property')))
        return res
    type = fields.Selection(selection_add=[('property', 'Property')], tracking=True)


class ProductProduct(models.Model):
    _inherit = 'product.product'
    _description = 'Real estate property'

    is_property = fields.Boolean(string="Is Property",  )
    property_code = fields.Char(string="Property Code", required=False, )
    is_name = fields.Boolean(string="",compute="_compute_name"  )

    @api.onchange('property_code')
    def onchange_method_property_code(self):
        self.name = self.property_code
    def _compute_name(self):
        for rec in self:
            rec.name = rec.property_code
    # @api.multi
    def available_property(self):
        for rec in self:
            if rec.state == 'blocked':
                rec.state = 'available'
            else:
                raise UserError('Please Check Selected Lines, Only Properties in Blocked Status Can be Available')

    property_no = fields.Integer(string="Property Number", copy=False)
    project_id = fields.Many2one('project.project', _('Project'))
    phase_id = fields.Many2one('project.phase', _('Phase'), store=True)
    @api.depends("project_id")
    @api.onchange('phase_id','project_id')
    def onchange_method_phase_id(self):
        for rec in self:
            _logger.info("self.project_id.id :: %s",rec.project_id.id)
            state = self.env['res.country.state'].search([('projects_ids', '=', rec.project_id.id),
                                                          ],limit=1)
            property_account_income_id = self.env['account.account'].search([('id', '=', rec.project_id.property_account_income_id.id),
                                                          ], limit=1)
            rec.state_id = state.id
            rec.country_id = state.country_id.id

            rec.property_account_income_id = property_account_income_id.id
            
            return {
                'domain': {'phase_id': [('project_id', '=', rec.project_id.id)]}
            }

    cate_id = fields.Many2one(comodel_name="property.category", string="Category",  )
    exception_id = fields.Many2one(comodel_name="property.exception", string="Exception" )

    state = fields.Selection([('draft', _('Draft')),('request_available', _('Request Available')),('approve', _('Approve')),('available', _('Available')),
                               ('reserved', _('Reserved')),('contracted', _('Contracted')),
                               ('blocked', _('Blocked')),
                              ('exception',_('Exception'))], string="Status", default='draft', copy=False)
    is_contracted = fields.Boolean(string="is Contracted", compute="_compute_is_contract" )
    def _compute_is_contract(self):
        for rec in self:
            rec.is_contracted = True
            account_move_line = self.env['account.move.line'].search([('product_id', '=', rec.id),
                                                          ], limit=1)
            if account_move_line.move_id.state == 'posted':
                rec.state = "contracted"

    type_of_property_id = fields.Many2one('property.type', _('Property Type'))

    @api.onchange('type_of_property_id')
    def onchange_method_type_of_property_id(self):
        for rec in self:
            if rec.type_of_property_id:
                rec.multi_image = rec.type_of_property_id.multi_image
                rec.images = rec.type_of_property_id.images_type
                rec.cate_id = rec.type_of_property_id.cate_id
                rec.sellable = rec.type_of_property_id.sellable
                # rec.name = rec.type_of_property_id.name
                # for line in rec.type_of_property_id.images_type:
    multi_image = fields.Boolean(string="Add  Multiple Images?")
    images = fields.One2many('biztech.product.images', 'product_tmpl_id',
                              string='Images')
    # part city country
    state_id = fields.Many2one("res.country.state", string='State')
    country_id = fields.Many2one('res.country', string='Country')
    @api.onchange('state_id')
    def _onchange_state(self):
        # self._onchange_compute_probability(optional_field_name='state_id')
        if self.state_id:
            self.country_id = self.state_id.country_id.id
    @api.onchange('country_id')
    def _onchange_country_id(self):
        # self._onchange_compute_probability(optional_field_name='country_id')
        # self.state_id = []
        res = {'domain': {'state_id': []}}
        if self.country_id:
            res['domain']['state_id'] = [('country_id', '=', self.country_id.id)]
        return res

    latlng_ids= fields.One2many('latlng.line', 'unit_id', string='LatLng List',copy=True)
    map= fields.Char('Map', digits=(9, 6))

    last_gps_latitude = fields.Float(string="",  required=False, )
    last_gps_longitude = fields.Float(string="",  required=False, )

    # part Area calculation part
    plot_area = fields.Float(string="Plot Area m²",  required=False, )
    sellable = fields.Float(string="Sellable BUA m²",  required=False, )
    price_m_a = fields.Float(string="Area Price m²",  required=False, )
    price_m = fields.Float(string="BUA Price m²",  required=False, )
    total_garden_area = fields.Float(string="Total Garden Area m²",  required=False, )
    price_garden_new = fields.Float(string="Garden Price m²", )
    price_garden_2 = fields.Float(string="Garden Price m²",compute="_compute_price_garden_2" )
    price_garden_3 = fields.Float(string="Garden Price m²", )
    def _compute_price_garden_2(self):
        for rec in self:
            rec.price_garden_2 = rec.price_garden_new
    # price_garden2 = fields.Float(string="Garden Price m²",  required=False, )

    is_garage = fields.Boolean(string="Is Garage ?", )
    price_garage_for_one = fields.Float(string="Price Per Garage", required=False, )
    number_of_garage = fields.Integer(string="Number Of Garage", required=False,default=1 )
    back_yard = fields.Float(string="Back Yard m²",  required=False, )
    front_yard = fields.Float(string="Front Yard m²",  required=False, )
    location_of_property_id = fields.Many2one('property.location', _('Property Location'))
    is_finish = fields.Boolean(string="Are you going to finish?",  )
    finish_of_property_id = fields.Many2one('property.finished.type', _('Finishing Type'))
    price_finishing_for_m = fields.Float(string="Price Finish For m²",  required=False, )
    design_of_property_id = fields.Many2one('property.design', _('Property Design'))
    is_pool = fields.Boolean(string="Is Pool ?",  )
    price_pool_for_one = fields.Float(string="Price Per Pool",  required=False, )
    number_of_pool = fields.Integer(string="Number Of Pool", required=False,default=1 )
    price_profile = fields.Char(string="Pricing Profile ", required=False, )
    history_unit_price_ids = fields.One2many(comodel_name="history.property.unit.price", inverse_name="product_id", string="History Unit Price", required=False, )
    history_finishing_price_ids = fields.One2many(comodel_name="history.property.finishing.price", inverse_name="product_id", string="History Finishing Price", required=False, )
    history_pool_price_ids = fields.One2many(comodel_name="history.property.pool.price", inverse_name="product_id", string="History Pool Price", required=False, )
    history_area_price_ids = fields.One2many(comodel_name="history.property.area.price", inverse_name="product_id", string="History Area Price", required=False, )
    history_garden_price_ids = fields.One2many(comodel_name="history.property.garden.price", inverse_name="product_id", string="History Garden Price", required=False, )
    history_garage_price_ids = fields.One2many(comodel_name="history.property.garage.price", inverse_name="product_id", string="History Garage Price", required=False, )
    # finish calculation
    unit_price = fields.Float(string="Unit Price ",  required=False, compute="_compute_unit_price")
    unit_price2 = fields.Float(string="Unit Price ",  required=False, )
    def _compute_unit_price(self):
        for rec in self:
            if rec.price_m > 0 :
                rec.unit_price = rec.price_m * rec.sellable
                if rec.unit_price != rec.unit_price2:
                    rec.update({
                        'unit_price2': rec.unit_price
                    })
                    rec.unit_price2 == rec.unit_price
            else:
                rec.unit_price = 0

    finishing_price = fields.Float(string="Finishing Price ",  required=False, compute="_compute_finishing_price")
    finishing_price2 = fields.Float(string="Finishing Price ",  required=False)
    def _compute_finishing_price(self):
        for rec in self:
            if rec.is_finish == True:
                if rec.price_finishing_for_m > 0 :
                    print('f1')
                    rec.finishing_price = rec.price_finishing_for_m * rec.sellable
                    if rec.finishing_price != rec.finishing_price2:
                        print('f2')
                        rec.update({
                            'finishing_price2' : rec.finishing_price
                        })
                        rec.finishing_price2 == rec.finishing_price
                else:
                    print('f3')
                    rec.finishing_price = 0
            else:
                print('f4')
                rec.finishing_price = 0

    pool_price = fields.Float(string="Pool Price ",  required=False, compute="_compute_pool_price")
    pool_price2 = fields.Float(string="Pool Price ",  required=False)
    def _compute_pool_price(self):
        for rec in self:
            if rec.is_pool == True:
                if rec.price_pool_for_one > 0 :
                    rec.pool_price = rec.price_pool_for_one * rec.number_of_pool
                    if rec.pool_price != rec.pool_price2:
                        rec.update({
                            'pool_price2': rec.pool_price
                        })
                        rec.pool_price2 == rec.pool_price
                else:
                    rec.pool_price = 0
            else:
                rec.pool_price = 0

    garage_price = fields.Float(string="Garage Price ", required=False, compute="_compute_garage_price")
    garage_price2 = fields.Float(string="Garage Price ", required=False)

    def _compute_garage_price(self):
        for rec in self:
            if rec.is_garage == True:
                if rec.price_garage_for_one > 0:
                    rec.garage_price = rec.price_garage_for_one * rec.number_of_garage
                    if rec.garage_price != rec.garage_price2:
                        rec.update({
                            'garage_price2': rec.garage_price
                        })
                        rec.garage_price2 == rec.garage_price
                else:
                    rec.garage_price = 0
            else:
                rec.garage_price = 0
    plot_price = fields.Float(string="Area Price ",  required=False, compute="_compute_area_price")
    plot_price2 = fields.Float(string="Area Price ",  required=False)
    def _compute_area_price(self):
        for rec in self:
                rec.plot_price = rec.plot_area * rec.price_m_a
                if rec.plot_price != rec.plot_price2:
                    rec.update({
                        'plot_price2': rec.plot_price
                    })
                    rec.plot_price2 == rec.plot_price

    @api.constrains('price_garage_for_one','is_garage')
    def validation_price_garage_for_one(self):
        print("self.is_garage :: %s",self.is_garage)
        if self.is_garage == True:
            if self.price_garage_for_one == 0.0:
                raise ValidationError(_(
                    "you must Enter Price For Garage!!"))
    @api.constrains('price_pool_for_one','is_pool')
    def validation_price_pool_for_one(self):
        if self.is_pool == True:
            if self.price_pool_for_one == 0.0:
                raise ValidationError(_(
                    "you must Enter Price For Pool!!"))
    @api.model
    def create(self, vals):

        vals['unit_price2'] = self.unit_price
        vals['finishing_price2'] = self.finishing_price
        vals['pool_price2'] = self.pool_price
        vals['plot_price2'] = self.plot_price
        vals['price_garden_3'] = self.price_garden_new
        vals['garage_price2'] = self.garage_price

        picking_type = super(ProductProduct, self).create(vals)
        return picking_type
    final_unit_price = fields.Float(string="Final Unit Price ",  required=False, compute="_compute_final_unit_price")
    def _compute_final_unit_price(self):
        for rec in self:
            rec.final_unit_price = rec.unit_price + rec.finishing_price + rec.pool_price + rec.plot_price + rec.price_garden_new
    def update_state_to_available(self):
        for rec in self:
            rec.sudo().write({'state': 'available','resp_user_id':False})

    def update_state_to_blocked(self):
        for rec in self:
            rec.write({'state': 'blocked'})

    # @api.
    def update_state_to_not_available(self):
        for rec in self:
            rec.sudo().write({'state': 'not_available'})


    def write(self, vals):
        rslt = super(ProductProduct, self).write(vals)
        if 'price_m' in vals:
            history_unit_price = self.env['history.property.unit.price'].create({
                'name': 'new',
                'date': date.today(),
                'unit_price': self.unit_price2,
                'product_id':self.id,
                'type_of_property_id': self.type_of_property_id.id,
                'project_id': self.project_id.id,
                'phase_id': self.phase_id.id,
                'state': self.state,
                'plot_area': self.plot_area,
                'sellable': self.sellable,
                'price_m': self.unit_price2 / self.sellable,
                'total_garden_area': self.total_garden_area,
                'back_yard': self.back_yard,
                'front_yard': self.front_yard,
                'location_of_property_id': self.location_of_property_id.id,
                'is_finish': self.is_finish,
                'finish_of_property_id': self.finish_of_property_id.id,
                'price_finishing_for_m': self.price_finishing_for_m,
                'design_of_property_id': self.design_of_property_id.id,
                'is_pool': self.is_pool,
                'price_pool_for_one': self.price_pool_for_one,
                'number_of_pool': self.number_of_pool,
                'price_profile': self.price_profile,
            })

            if history_unit_price:
                self.unit_price2 = self.unit_price
        if 'price_finishing_for_m' in vals:
            history_finishing_price = self.env['history.property.finishing.price'].create({
                'name': 'new',
                'date': date.today(),
                'finishing_price': self.finishing_price2,
                'product_id':self.id,
                'type_of_property_id': self.type_of_property_id.id,
                'project_id': self.project_id.id,
                'phase_id': self.phase_id.id,
                'state': self.state,
                'plot_area': self.plot_area,
                'sellable': self.sellable,
                'price_m': self.price_m,
                'total_garden_area': self.total_garden_area,
                'back_yard': self.back_yard,
                'front_yard': self.front_yard,
                'location_of_property_id': self.location_of_property_id.id,
                'is_finish': self.is_finish,
                'finish_of_property_id': self.finish_of_property_id.id,
                'price_finishing_for_m': self.finishing_price2 / self.sellable,
                'design_of_property_id': self.design_of_property_id.id,
                'is_pool': self.is_pool,
                'price_pool_for_one': self.price_pool_for_one,
                'number_of_pool': self.number_of_pool,
                'price_profile': self.price_profile,
            })

            if history_finishing_price:
                self.finishing_price2 = self.finishing_price
        if 'price_pool_for_one' in vals:
            price_pool_for_one = 0
            if self.number_of_pool > 0:
                price_pool_for_one =  self.pool_price2 / self.number_of_pool

            history_pool_price = self.env['history.property.pool.price'].create({
                'name': 'new',
                'date': date.today(),
                'pool_price': self.pool_price2,
                'product_id':self.id,
                'type_of_property_id': self.type_of_property_id.id,
                'project_id': self.project_id.id,
                'phase_id': self.phase_id.id,
                'state': self.state,
                'plot_area': self.plot_area,
                'sellable': self.sellable,
                'price_m': self.price_m,
                'total_garden_area': self.total_garden_area,
                'back_yard': self.back_yard,
                'front_yard': self.front_yard,
                'location_of_property_id': self.location_of_property_id.id,
                'is_finish': self.is_finish,
                'finish_of_property_id': self.finish_of_property_id.id,
                'price_finishing_for_m': self.finishing_price2/self.sellable,
                'design_of_property_id': self.design_of_property_id.id,
                'is_pool': self.is_pool,
                'price_pool_for_one': price_pool_for_one,
                'number_of_pool': self.number_of_pool,
                'price_profile': self.price_profile,
            })

            if history_pool_price:
                self.pool_price2 = self.pool_price
        if 'price_garage_for_one' in vals:
            history_garage_price = self.env['history.property.garage.price'].create({
                'name': 'new',
                'date': date.today(),
                'garage_price': self.garage_price2,
                'product_id':self.id,
                'type_of_property_id': self.type_of_property_id.id,
                'project_id': self.project_id.id,
                'phase_id': self.phase_id.id,
                'state': self.state,
                'plot_area': self.plot_area,
                'sellable': self.sellable,
                'price_m': self.price_m,
                'total_garden_area': self.total_garden_area,
                'back_yard': self.back_yard,
                'front_yard': self.front_yard,
                'location_of_property_id': self.location_of_property_id.id,
                'is_finish': self.is_finish,
                'finish_of_property_id': self.finish_of_property_id.id,
                'design_of_property_id': self.design_of_property_id.id,
                'is_pool': self.is_pool,
                'price_garage_for_one': self.garage_price2/self.number_of_garage,
                'number_of_pool': self.number_of_pool,
                'price_profile': self.price_profile,
            })

            if history_garage_price:
                self.garage_price2 = self.garage_price
        if 'price_garden_new' in vals:
            print("enter price_garden %s",self.price_garden_3)
            price_pool_for_one = 0
            if self.number_of_pool > 0:
                price_pool_for_one = self.pool_price2/self.number_of_pool
            history_garden_price = self.env['history.property.garden.price'].create({
                'name': 'new',
                'date': date.today(),
                'garden_price': self.price_garden_3,
                'product_id':self.id,
                'type_of_property_id': self.type_of_property_id.id,
                'project_id': self.project_id.id,
                'phase_id': self.phase_id.id,
                'state': self.state,
                'plot_area': self.plot_area,
                'sellable': self.sellable,
                'price_m': self.price_m,
                'total_garden_area': self.total_garden_area,
                'back_yard': self.back_yard,
                'front_yard': self.front_yard,
                'location_of_property_id': self.location_of_property_id.id,
                'is_finish': self.is_finish,
                'finish_of_property_id': self.finish_of_property_id.id,
                'price_finishing_for_m': self.finishing_price2/self.sellable,
                'design_of_property_id': self.design_of_property_id.id,
                'is_pool': self.is_pool,
                'price_pool_for_one': price_pool_for_one,
                'number_of_pool': self.number_of_pool,
                'price_profile': self.price_profile,
            })

            if history_garden_price:
                self.price_garden_3 = self.price_garden_new
        if 'price_m_a' in vals:
            price_pool_for_one = 0
            if self.number_of_pool > 0:
                price_pool_for_one = self.pool_price2/self.number_of_pool
            history_area_price = self.env['history.property.area.price'].create({
                'name': 'new',
                'date': date.today(),
                'price_m_a': self.plot_price2,
                'area_price': self.plot_price2/self.plot_area,
                'product_id':self.id,
                'type_of_property_id': self.type_of_property_id.id,
                'project_id': self.project_id.id,
                'phase_id': self.phase_id.id,
                'state': self.state,
                'plot_area': self.plot_area,
                'sellable': self.sellable,
                'total_garden_area': self.total_garden_area,
                'back_yard': self.back_yard,
                'front_yard': self.front_yard,
                'location_of_property_id': self.location_of_property_id.id,
                'is_finish': self.is_finish,
                'finish_of_property_id': self.finish_of_property_id.id,
                'price_finishing_for_m': self.finishing_price2/self.sellable,
                'design_of_property_id': self.design_of_property_id.id,
                'is_pool': self.is_pool,
                'price_pool_for_one': price_pool_for_one,
                'number_of_pool': self.number_of_pool,
                'price_profile': self.price_profile,
            })

            if history_area_price:
                self.plot_price2 = self.plot_price

        return rslt

    analytic_account_id = fields.Many2one(comodel_name="account.analytic.account", string="Analytic Account", required=False,readonly=True )

    def set_to_draft(self):
        for rec in self:
                rec.state = 'draft'
    def convert_to_available(self):
        for rec in self:
            # if rec.state in ['draft']:
                rec.state = 'available'
                req_id = self.env['account.analytic.account'].create({
                    'name': self.name,
                })
                rec.analytic_account_id = req_id.id

    def convert_to_block(self):
        for rec in self:
            if rec.state in ['available','draft']:
                rec.state = 'blocked'

    def convert_to_draft(self):
        for rec in self:
            if rec.state in ['available']:
                rec.state = 'draft'

    def exception_do(self):
        for rec in self:
                rec.state = 'exception'

    def request_to_available(self):
        for rec in self:
                rec.state = 'request_available'

    def approved_to_available(self):
        for rec in self:
                rec.state = 'approve'

    def create_request_reservation(self):
        _logger.info("create_request_reservation")

        req_id = self.env['request.reservation'].create({
            'date': datetime.now(),
            'project_id': self.project_id.id,
            'phase_id': self.phase_id.id,
            'property_id': self.id,
        })

        return {'name': (
                            'Request Reservation'),
                        'type': 'ir.actions.act_window',
                        'res_model': 'request.reservation',
                        'res_id': req_id.id,
                        'view_type': 'form',
                        'view_mode': 'form',
                    }

    def create_reservation(self):
        _logger.info("create_reservation")
        res_res = self.env['res.reservation'].search([('property_id', '=', self.id),
             ('state', 'in', ['reserved'])])
        if len(res_res) != 0:
            raise ValidationError(_(
                "Sorry .. you must Create One Reservation Form For Request Reservation for This Property  %s!!") % self.property_id.name)

        req_id = self.env['res.reservation'].create({
            'date': datetime.now(),
            'project_id': self.project_id.id,
            'phase_id': self.phase_id.id,
            'property_id': self.id,
            'custom_type': 'Reservation',
            'state': 'draft',
        })
        req_id.onchange_method_state()

        return {'name': (
                            'Reservation'),
                        'type': 'ir.actions.act_window',
                        'res_model': 'res.reservation',
                        'res_id': req_id.id,
                        'view_type': 'form',
                        'view_mode': 'form',
                    }


    counter_reservation = fields.Integer(string="", required=False,compute="_compute_counter_reservation" )

    def _compute_counter_reservation(self):
        for rec in self:
            res = self.env['res.reservation'].search(
                [('property_id', '=', rec.id)])
            rec.counter_reservation = len(res)
    def action_view_partner_reservation(self):
        self.ensure_one()
        action = self.env.ref('add_real_estate.reservation_list_action').read()[0]
        action['domain'] = [
            ('property_id', '=', self.id),
        ]
        print("action %s",action)
        return action



    propert_account_id = fields.Many2one(comodel_name="account.account", string="Income Account", required=False, )

    is_req_res = fields.Boolean(string="Is Request Resveration",compute="_compute_view_button_create"  )
    is_res = fields.Boolean(string="Is Request Resveration", compute="_compute_view_button_create" )
    def _compute_view_button_create(self):
        for rec in self:
            req = self.env['request.reservation'].search(
                [('property_id', '=', rec.id),("state",'!=','blocked')
                                                          ], limit=1)
            res = self.env['res.reservation'].search(
                [('property_id', '=', rec.id),("state",'!=','blocked')
                                                          ], limit=1)
            if len(req) > 0:
                rec.is_req_res = True
            else:
                rec.is_req_res = False

            if len(res) > 0 :
                rec.is_res = True
            else:
                rec.is_res = False
            print("rec.is_res :: %s",rec.is_res)

