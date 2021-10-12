# -*- coding: utf-8 -*-
from odoo import models, fields, api, _, exceptions
import datetime
from odoo.exceptions import ValidationError
TYPE_SELECTION = [('sale', _('Sale')),
                  ('sale_refund', _('Sale Refund')),
                  ('purchase', _('Purchase')),
                  ('purchase_refund', _('Purchase Refund')),
                  ('cash', _('Cash')),
                  ('bank', _('Bank and Checks')),
                  ('general', _('General')),
                  ('situation', _('Opening/Closing Situation'))]

class AccountPaymentTermLine(models.Model):
    _inherit = "account.payment.term.line"

    @api.model
    def create(self, vals):
        obj = super(AccountPaymentTermLine, self).create(vals)
        return obj

    journal_id = fields.Many2one('account.journal', _('Journal'))
    payment_description = fields.Char(string="Description")
    deposit = fields.Boolean('Deposit')
    is_garage = fields.Boolean('Is Garage')
    is_garage_main = fields.Boolean('Is Garage & Maintnance')
    add_extension = fields.Boolean('Extension')
    value_amount = fields.Float(string='Value', digits=(20, 15), help="For percent enter a ratio between 0-100.")
    percentage = fields.Float(string="Percentage",  required=False,compute="_compute_percentage" )
    def _compute_percentage(self):
        for rec in self:
            rec.percentage = rec.value_amount * 100.00

class AccountPaymentTerm(models.Model):
    _inherit = "account.payment.term"

    payment_detail_ids = fields.One2many('rs.payment_strategy_details', 'payment_strategy_id', ondelete='cascade',
                                         string="Details", copy=True)
    total_percentage = fields.Float(compute="_total_percentage", string="Total Percentage", store=True)
    virtual = fields.Boolean(_("Virtual"))
    computed = fields.Boolean(_("Computed"))
    payment_term_discount = fields.Float(string='Discount', digits=(16, 6))
    state = fields.Selection([('draft', 'Draft'), ('approved', 'Approved')], string='State', copy=False)

    @api.constrains('payment_term_discount')
    def check_payment_term_discount(self):
        for rec in self:
            if rec.payment_term_discount > 100.0 or rec.payment_term_discount < 0.0:
                raise ValidationError(_('Discount should less than 100.0 and greater than 0.0'))

    @api.constrains('line_ids')
    def _check_lines(self):
        return True

    def approved_payment(self):
        for rec in self:
            rec.state = 'approved'

    def copy_payment(self):
        for rec in self:
            copied_obj = self.copy(default={
                'virtual': True,
                'name': 'Copy' + ' ' + rec.name,
            })
            view_id = self.env.ref('account.view_payment_term_form')
            return {
                'type': 'ir.actions.act_window',
                'name': _('Payment Term'),
                'res_model': 'account.payment.term',
                'res_id': copied_obj.id,
                'view_type': 'form',
                'view_mode': 'form',
                'view_id': view_id.id,
                'target': 'current',
                'nodestroy': True,
            }

    """
    there are some cases:
        1- biannual >>  6 months incremental
        2- quarterly >> 3 months   ,,
        3- Annual >> 12 month incremental
        4- Monthly >> month incremental
    # in the above four cases the day=0.
        5- BY Month >> amount of months incremental
    """

    ## TOTAL NUMBER OF INSTALLMENTS = TOTAL NUMBER OF COMPUTATIONS
    ## THE ALGORITHM GOES LIKE THIS >>>
    """
        1- retrieve all the detail object.
        2- for every object, get the case (x), percentage(y), number of installments(z).
        3- (z) number of computations will be created.
        4- for any computation, the percentage(of computation) will be the amount(y/z).
        5- the computation will be chosen as percent. [[CONSTANT]]
        6- amount will be the new percent.
        7- the days will be incremental by time. 
    """

    def cr_computation(self):
        for rec in self:
            # Prevent computation if The total Percentage of payment Strategy Not Equal 100.00
            if rec.total_percentage != 100.0:
                raise exceptions.ValidationError(
                    "The total Percentage of payment Strategy Not Equal 100.00 : %s" % rec.total_percentage)

            # check on line_ids field
            # then Delete old payment term lines
            rec.line_ids.unlink() if rec.line_ids else None
            # step1: retrieve all the details objects, initial version
            # step2: retrieve all the information needed from the objects.
            details_list = []
            for payment in self.payment_detail_ids:
                tmp = {}
                tmp['id'] = payment.id
                tmp['percentage'] = (payment.inst_percentage / 100.0) / payment.number_of_inst
                tmp['no_inst'] = payment.number_of_inst
                tmp['name'] = payment.name

                # calculate shifting days
                if payment.shift_by == "2":  # by months
                    tmp['shifting_days'] = payment.shifting_months * 30
                else:
                    tmp['shifting_days'] = payment.shifting_days

                if payment.inst_range == 1:
                    tmp['increment'] = payment.by_days
                    tmp['days'] = 0
                    tmp['journal_id'] = payment.journal_id.id
                    tmp['payment_description'] = payment.name
                    tmp['deposit'] = payment.deposit
                    tmp['add_extension'] = payment.add_extension
                    tmp['is_garage'] = payment.is_garage
                    tmp['is_garage_main'] = payment.is_garage_main
                else:
                    tmp['journal_id'] = payment.journal_id.id
                    tmp['payment_description'] = payment.name
                    tmp['deposit'] = payment.deposit
                    tmp['add_extension'] = payment.add_extension
                    tmp['is_garage'] = payment.is_garage
                    tmp['is_garage_main'] = payment.is_garage_main
                    tmp['days'] = 0
                    selection = payment.by_period
                    if selection == "1":
                        tmp['increment'] = 30
                    elif selection == "2":
                        tmp['increment'] = 90
                    elif selection == "3":
                        tmp['increment'] = 180
                    elif selection == "4":
                        tmp['increment'] = 360
                    elif selection == "5":
                        tmp['increment'] = 0
                details_list.append(tmp)
            computations_list = []

            f_days_count = 0  # days no. of the first payment term line resulted from last payment strategy
            for detail_obj in details_list:
                lines_count = len(range(0, detail_obj['no_inst']))
                l_index = 1
                for installment in range(0, detail_obj['no_inst']):
                    tmp = {}
                    tmp['payment_id'] = rec.id
                    tmp['value'] = 'percent'
                    tmp['value_amount'] = detail_obj['percentage']

                    if detail_obj['shifting_days']:
                        tmp['days'] = detail_obj['increment'] * (installment + 1) + detail_obj['shifting_days']

                        if detail_obj['shifting_days'] < 0 and l_index == 1 and tmp['days'] < f_days_count:
                            max_allowed_days = (detail_obj['increment'] * (installment + 1)) - f_days_count
                            if max_allowed_days <= 0:
                                raise ValidationError(
                                    _('Number of shifting days/months in %s should be greater than or equal 0') % (
                                        detail_obj['name'],))
                            else:
                                max_allowed_months = max_allowed_days / 30
                                raise ValidationError(_(
                                    'Number of shifting days/months %s should be greater than or equal (-%s days) or (-%s months)') % (
                                                          detail_obj['name'], max_allowed_days, max_allowed_months))
                    else:
                        print("detail_obj['increment'] :: %s",detail_obj['increment'])
                        tmp['days'] = detail_obj['increment'] * (installment + 1)

                    # set f_days_count on the first iteration
                    if l_index == 1:
                        f_days_count = tmp['days']

                    l_index += 1

                    tmp['journal_id'] = detail_obj['journal_id']
                    tmp['payment_description'] = detail_obj['payment_description']
                    tmp['deposit'] = detail_obj['deposit']
                    tmp['add_extension'] = detail_obj['add_extension']
                    tmp['is_garage'] = detail_obj['is_garage']
                    tmp['is_garage_main'] = detail_obj['is_garage_main']
                    computations_list.append(tmp)
            for computation in computations_list:
                obj = self.env['account.payment.term.line'].sudo().create(computation)
            if rec.total_percentage == 100.0:
                rec.sudo().write(({'computed': True}))

    @api.depends('payment_detail_ids', 'payment_detail_ids.inst_percentage')
    def _total_percentage(self):
        for rec in self:
            inst_percents = self.env['rs.payment_strategy_details'].search([('payment_strategy_id', '=', rec.id),
                                                                            ('add_extension', '=', False)])
            total = 0.0
            for installment in inst_percents:
                total += installment.inst_percentage
            rec.total_percentage = total


class RsPaymentStrategyDetails(models.Model):
    _name = 'rs.payment_strategy_details'

    payment_line_type_id = fields.Many2one(comodel_name="payment.line.type", string="Payment Lines type", required=False, )

    @api.onchange('payment_line_type_id')
    def onchange_method_payment_line_type_id(self):
        self.name = self.payment_line_type_id.name
    name = fields.Char(ondelete='cascade', string="Name")
    payment_strategy_id = fields.Many2one('account.payment.term', ondelete='cascade', string="Payment Strategy")
    inst_percentage = fields.Float(string="Installment Percentage")
    number_of_inst = fields.Integer(string="Number of Installments", default=1)
    # simple calculator
    calculate_by = fields.Selection([('percentage', _('Percentage')),
                                     ('value', _('Value'))], 'Calculate By',
                                    default='percentage')

    unit_price = fields.Float(string="Unit Price")
    amount = fields.Float(string="Amount")
    inst_value = fields.Float(string="Installment Value")
    calc_no_inst = fields.Integer(string="Number of Installments")
    # installment range
    inst_range = fields.Selection([("1", _('By Days')),
                                   ("2", _('By Period'))], 'Installment Range', default="2",
                                  required=True)
    by_days = fields.Integer(string="By Days")
    by_period = fields.Selection([("5", _('Once')),
                                  ("1", _('Monthly')),
                                  ("2", _('Quarterly')),
                                  ("3", _('Semiannual')),
                                  ("4", _('Annual'))])
    date = fields.Date(string="Date")
    # date of the first installment
    date_select = fields.Selection([("1", _("Fixed Date")),
                                    ("2", _("By Contract Date"))], 'Date', default="2", required=False)
    contract_date = fields.Date(string="Contract Date", required=False)
    first_inst_date = fields.Date(string="First Date Installment")
    payment_type = fields.Selection([('cash', _('Cash')), ('bank', _('Bank'))], _('Payment Type'))
    journal_id = fields.Many2one('account.journal', _('Journal'))
    deposit = fields.Boolean('Deposit')
    is_garage = fields.Boolean('Is Garage')
    is_garage_main = fields.Boolean('Is Garage & Maintnance')
    add_extension = fields.Boolean('Maintenance & Insurance')

    shift_by = fields.Selection([("1", _('Days')),
                                 ("2", _('Months'))], string='Shift by', default="1")
    shifting_days = fields.Integer(string='Shift Days')
    shifting_months = fields.Integer(string='Shift Months')

    #
    # @api.constrains('shifting_days')
    # def check_shifting_days(self):
    #     for record in self:
    #         if record.shifting_days and record.shifting_days < 1:
    #             raise ValidationError('Please insert positive value in shift days')

    @api.onchange('unit_price', 'inst_percentage', 'number_of_inst', 'calculate_by', 'amount', 'calc_no_inst')
    def calc_total_price(self):
        for rec in self:
            if rec.calculate_by == 'percentage':
                amount = (rec.inst_percentage / 100.0) * rec.unit_price
                rec.amount = amount
                if rec.number_of_inst != 0:
                    rec.inst_value = amount / rec.number_of_inst
                rec.calc_no_inst = rec.number_of_inst
            if rec.calculate_by == 'value':
                if rec.unit_price != 0:
                    rec.inst_percentage = (rec.amount / rec.unit_price) * 100.0
                rec.number_of_inst = rec.calc_no_inst
                if rec.calc_no_inst != 0:
                    rec.inst_value = rec.amount / rec.calc_no_inst

class PaymentBank(models.Model):
    _name = "payment.bank"

    name = fields.Char(_('Bank Name'), required=True)
    bank_account_id = fields.Many2one('account.account', _('Account'), required=False)


class PaymentBankCustomer(models.Model):
    _name = "payment.bank.cus"

    name = fields.Char(_('Bank Name'), required=True)


class PaymentStrgRequest(models.Model):
    _name = 'payment.strg.request'
    _order = "id asc"
    _rec_name = 'description'


    is_create_payment = fields.Boolean(string=" Create Payment",  )
    state = fields.Selection([('draft', 'Draft'), ('posted', 'Posted'), ('deliver', 'Deliver'),
                              ('under_coll', 'Under collection'),
                              ('collected', 'Withdrawal'),
                              ('sent', 'Sent'), ('reconciled', 'Reconciled'),
                              ('cancelled', 'Cancelled'),
                              ('discount', 'Discount'),
                              ('loan', 'Loan'),
                              ('refund_from_discount', "Refund From Discount"),
                              ('refunded_from_notes', 'Refund Notes Receivable'),
                              ('refunded_under_collection', 'Refund Under collection'),
                              ('check_refund', 'Refunded')],
                             readonly=True, default='draft', copy=False, string="Status")

    is_selected_to_action = fields.Boolean(string="Is Selected",default=False  )
    is_receive = fields.Boolean(string="Is Receive",default=False  )
    name = fields.Char(string='Name')
    reserve_id = fields.Many2one('request.reservation', _('Request Reservation'))
    sale_order_id = fields.Many2one('sale.order', string='Sale Order')
    payment_code = fields.Char(_('Code'))
    partner_id = fields.Many2one('res.partner', string='Customer', related='reserve_id.customer_id')
    customer_id = fields.Many2one('res.partner', string='Customer', related='reserve_id.customer_id', store=True)
    project_id = fields.Many2one('project.project', string='Project', related='reserve_id.project_id')
    property_ids = fields.Many2many('product.product', string='Properties')
    payment_date = fields.Date(_('Date'))
    base_amount = fields.Float(_('Amount'), digits=(16, 4))
    amount = fields.Float(_('Amount'), digits=(16, 4))
    amount_due = fields.Float(_('Amount Due'), digits=(16, 4),compute="_compute_amount_due")
    amount_pay = fields.Float(_('Amount Pay'), digits=(16, 4))
    is_part = fields.Boolean(string="part",  )
    is_pay = fields.Boolean(string="Is Paid", cmmpute="_compute_amount_due" )
    def _compute_amount_due(self):
        for rec in self:
            # print("rec.base_amount :: %s",rec.base_amount)
            # print("rec.amount_pay :: %s",rec.amount_pay)
            rec.amount_due = rec.base_amount - rec.amount_pay
            # print("rec.amount_due :: %s",rec.amount_due)
            if rec.amount_due == 0.0:
                rec.is_pay = True
            else:
                rec.is_pay =False



    penalty_fees = fields.Float(_('Penalty Fees'))
    deduction_amount = fields.Float(_('Deduction Amount'))
    penalty_date = fields.Date(_('Deduction Payment Date'))
    penalty_journal_id = fields.Many2one('account.journal', _('Deduction Journal'))
    apply_penalty = fields.Boolean(string='Apply Penalty')
    old_value = fields.Float(_('Old Value'), digits=(16, 2))
    penalty_journal_entry_id = fields.Many2one('account.move', _('Penalty Fees Journal Entry'))
    description = fields.Char(_('Description'))
    move_check = fields.Boolean(string='Paid')
    journal_id = fields.Many2one('account.journal', _('Journal'))
    under_collected_journal_entry_id = fields.Many2one('account.move', _('Under Collected Journal Entry'))
    collected_journal_entry_id = fields.Many2one('account.move', _('Collected Journal Entry'))
    type = fields.Selection(selection=TYPE_SELECTION, related='journal_id.type',  string='Payment Type')
    cus_bank = fields.Many2one('payment.bank.cus', _("Customer Bank Name"))
    bank_name = fields.Many2one('payment.bank', _("Bank Name"))
    cheque = fields.Char(_("Cheque Number"))
    is_bank_transfer = fields.Boolean(string='Is Bank Transfer', related='journal_id.show_checks')
    cheque_status = fields.Selection([('draft', _("Draft")),
                                      ('received', _("Received")),
                                      ('under_collection', _("Under Collection")),
                                      ('collection', _("Collection")),
                                      ('rejected', _("Rejected"))], _('Check Status'),
                                     default='draft')
    deposite = fields.Boolean(string='Deposit')
    maintainance_fees = fields.Float(string='Fees', digits=(16, 2))
    add_extension = fields.Boolean(string='Maintenance & Insurance')
    use_unearned_revenu_account = fields.Boolean(string='Unearned Account')
    rejected = fields.Boolean(string='Rejected')
    # days_diff = fields.Integer(compute='_compute_days_diff', string='Days Diff')
    cancelled = fields.Boolean(string='Cancelled')
    payment_id = fields.Many2one('account.payment', _("Payment"))
    move_id = fields.Many2one('account.move', _("Move"))
    maintaince_id = fields.Many2one('account.payment', _("Maintenance"))
    is_bank_transfer = fields.Boolean(string='Bank Transfer', related='journal_id.show_checks')
    payment_method_id = fields.Many2one('account.payment.method', string='Payment Type', oldname="payment_method")
    rejection_action = fields.Selection([('transfer', _('Transfer To Cash')),
                                         ('reject', _('Reject'))], 'Rejection Action')
    rejection_cash_payment_id = fields.Many2one('account.payment', _("Payment"))
    bank_ids = fields.One2many(comodel_name="data.bank.cheque", inverse_name="payment_strg_request_id", string="Banks", required=False, )
    is_cheque = fields.Boolean(string="Is Cheque",  )
    Due_Date = fields.Date(string="Due Date", required=False, )
    def select_receive(self):
        for rec in self:
            rec.is_receive = True

    state_payment = fields.Selection([('cash', 'Cash'),
                                      ('visa', 'Visa'),
                                      ('cheque', 'Cheque'),
                              ('bank', 'Bank'),
                              ],default="cheque")


    payment_code = fields.Char(string="Payment Code", required=False, )

    @api.model
    def create(self, values):
        print("values :> ",values['state_payment'])
        if values['state_payment'] == 'cash':
                    values['payment_code'] = self.env['ir.sequence'].next_by_code('pay.cash.seq')
        elif values['state_payment'] == 'visa':
                    values['payment_code'] = self.env['ir.sequence'].next_by_code('pay.visa.seq')
        elif values['state_payment'] == 'cheque':
                    values['payment_code'] = self.env['ir.sequence'].next_by_code('pay.cheque.seq')
        elif values['state_payment'] == 'bank':
                    values['payment_code'] = self.env['ir.sequence'].next_by_code('pay.Bank.seq')
        return super(PaymentStrgRequest, self).create(values)

    def write(self, vals):
            print("values :> ", vals)
            if 'state_payment' in vals:
                if vals['state_payment'] == 'cash':
                    vals['payment_code'] = self.env['ir.sequence'].next_by_code('pay.cash.seq')
                elif vals['state_payment'] == 'visa':
                    vals['payment_code'] = self.env['ir.sequence'].next_by_code('pay.visa.seq')
                elif vals['state_payment'] == 'cheque':
                    vals['payment_code'] = self.env['ir.sequence'].next_by_code('pay.cheque.seq')
                elif vals['state_payment'] == 'bank':
                    vals['payment_code'] = self.env['ir.sequence'].next_by_code('pay.Bank.seq')

            return super(PaymentStrgRequest, self).write(vals)

class PaymentStrg(models.Model):
    _name = 'payment.strg'
    _order = "id asc"
    _rec_name = 'description'

    # payments_ids = fields.One2many(comodel_name="account.payment", inverse_name="payment_strg_id", string="payments", required=False, )
    payments_ids = fields.Many2many(comodel_name="account.payment", relation="payment_str", column1="p", column2="s", string="", )
    state = fields.Selection([('draft', 'Draft'), ('posted', 'Posted'), ('deliver', 'Deliver'),
                              ('under_coll', 'Under collection'),
                              ('collected', 'Withdrawal'),
                              ('sent', 'Sent'), ('reconciled', 'Reconciled'),
                              ('cancelled', 'Cancelled'),
                              ('discount', 'Discount'),
                              ('loan', 'Loan'),
                              ('refund_from_discount', "Refund From Discount"),
                              ('refunded_from_notes', 'Refund Notes Receivable'),
                              ('refunded_under_collection', 'Refund Under collection'),
                              ('check_refund', 'Refunded')],
                             readonly=True, default='draft', copy=False, string="Status",compute="_compute_is_state_payment")
    def _compute_is_state_payment(self):
        for rec in self:
            if rec.payments_ids:
                for line in rec.payments_ids:
                    rec.state = line.state

            else:
                rec.state = 'draft'
    def get_group_of_logged_user(self):
        for obj in self:
            user = self.env['res.users'].browse(obj.env.uid)
            obj.accountant_status = True if user.has_group('account.group_account_manager') or user.has_group(
                'account.group_account_user') else False

    # def _compute_days_diff(self):
    #     days_diff = 0
    #     for rec in self:
    #         if rec.payment_date:
    #             d1 = datetime.date.today()
    #             d2 = rec.payment_date
    #             d2 = datetime.datetime.strptime(d2, "%Y-%m-%d").date()
    #             days_diff = (d2 - d1).days
    #         rec.days_diff = days_diff

    is_selected_to_action = fields.Boolean(string="Is Selected",default=False  )
    is_receive = fields.Boolean(string="Is Receive",default=False  )
    is_pay = fields.Boolean(string="Is Paid",default=False  )
    name = fields.Char(string='Name')
    accountant_status = fields.Boolean('Is accountant', compute='get_group_of_logged_user', default=True)
    reserve_id = fields.Many2one('res.reservation', _('Reservation'))

    is_add_unit = fields.Boolean(string="", compute = "_compute_unit_id" )
    def _compute_unit_id(self):
        for rec in self:
            if rec.unit_id.id == False:
                rec.unit_id = rec.reserve_id.property_id.id
                rec.is_add_unit = True
            else:
                rec.is_add_unit = True
    @api.onchange('reserve_id')
    def onchange_method_reserve_id(self):
        self.unit_id = self.reserve_id.property_id.id

    unit_id = fields.Many2one(comodel_name="product.product", string="Property", required=False, )
    sale_order_id = fields.Many2one('sale.order', string='Sale Order')
    payment_code = fields.Char(_('Code'))
    partner_id = fields.Many2one('res.partner', string='Customer', related='reserve_id.customer_id')
    customer_id = fields.Many2one('res.partner', string='Customer', related='reserve_id.customer_id', store=True)
    project_id = fields.Many2one('project.project', string='Project', related='reserve_id.project_id')
    property_ids = fields.Many2many('product.product', string='Properties')
    payment_date = fields.Date(_('Date'))
    base_amount = fields.Float(_('Amount'), digits=(16, 2),store=True)

    amount = fields.Float(_('Amount'), digits=(16, 4))
    amount_due = fields.Float(_('Amount Due'), digits=(16, 4),compute="_compute_amount_due")
    amount_pay = fields.Float(_('Amount Pay'), digits=(16, 4))
    is_part = fields.Boolean(string="part",  )
    is_maintainance = fields.Boolean(string=" maintainance & Insurance ",)
    is_garage = fields.Boolean(string="Is Garage",)
    is_garage_main = fields.Boolean(string="Is Garage&maintanance",)
    def _compute_amount_due(self):
        for rec in self:
            rec.amount_due = rec.amount - rec.amount_pay
            if rec.amount_due == 0.0:
                rec.is_pay = True
            else:
                rec.is_pay =False

    penalty_fees = fields.Float(_('Penalty Fees'))
    deduction_amount = fields.Float(_('Deduction Amount'))
    penalty_date = fields.Date(_('Deduction Payment Date'))
    penalty_journal_id = fields.Many2one('account.journal', _('Deduction Journal'))
    apply_penalty = fields.Boolean(string='Apply Penalty')
    old_value = fields.Float(_('Old Value'), digits=(16, 2))
    penalty_journal_entry_id = fields.Many2one('account.move', _('Penalty Fees Journal Entry'))
    description = fields.Char(_('Description'))
    move_check = fields.Boolean(string='Paid')
    journal_id = fields.Many2one('account.journal', _('Journal'))
    under_collected_journal_entry_id = fields.Many2one('account.move', _('Under Collected Journal Entry'))
    collected_journal_entry_id = fields.Many2one('account.move', _('Collected Journal Entry'))
    type = fields.Selection(selection=TYPE_SELECTION, related='journal_id.type', store=True, string='Payment Type')
    is_create_payment = fields.Boolean(string="",default=False  )
    cus_bank = fields.Many2one('payment.bank.cus', _("Customer Bank Name"))
    bank_name = fields.Many2one('payment.bank', _("Bank Name"))
    cheque = fields.Char(_("Cheque Number"))
    is_bank_transfer = fields.Boolean(string='Is Bank Transfer', related='journal_id.show_checks')
    cheque_status = fields.Selection([('draft', _("Draft")),
                                      ('received', _("Received")),
                                      ('under_collection', _("Under Collection")),
                                      ('collection', _("Collection")),
                                      ('rejected', _("Rejected"))], _('Check Status'),
                                     default='draft')
    deposite = fields.Boolean(string='Deposit')
    maintainance_fees = fields.Float(string='Fees', digits=(16, 2))
    add_extension = fields.Boolean(string='Maintenance & Insurance')
    use_unearned_revenu_account = fields.Boolean(string='Unearned Account')
    rejected = fields.Boolean(string='Rejected')
    # days_diff = fields.Integer(compute='_compute_days_diff', string='Days Diff')
    cancelled = fields.Boolean(string='Cancelled')
    payment_id = fields.Many2one('account.payment', _("Payment"))
    move_id = fields.Many2one('account.move', _("Move"))
    maintaince_id = fields.Many2one('account.payment', _("Maintenance"))
    is_bank_transfer = fields.Boolean(string='Bank Transfer', related='journal_id.show_checks')
    payment_method_id = fields.Many2one('account.payment.method', string='Payment Type', oldname="payment_method")
    rejection_action = fields.Selection([('transfer', _('Transfer To Cash')),
                                         ('reject', _('Reject'))], 'Rejection Action')
    rejection_cash_payment_id = fields.Many2one('account.payment', _("Payment"))

    _defaults = {
        'payment_code': lambda self, cr, uid, context: self.pool.get('ir.sequence').get(cr, uid,
                                                                                        'real.estate.payment.code.seq')
    }

    @api.depends('description', 'payment_code')
    def name_get(self):
        result = []
        name = ''
        for val in self:
            if val.payment_code:
                name = str(val.payment_code)
                if val.description:
                    name += ' - ' + val.description
            result.append((val.id, name))
        return result



    def unlink(self):
        for record in self:
            if record.under_collected_journal_entry_id:
                raise ValidationError(
                    _("Sorry .. You cannot delete this payment which in 'Under collection' or 'Collection'"))
        return super(PaymentStrg, self).unlink()

    bank_ids = fields.One2many(comodel_name="data.bank.cheque", inverse_name="payment_strg_id", string="Banks", required=False, )
    state_payment = fields.Selection([('cash', 'Cash'),
                                      ('visa', 'Visa'),
                                      ('cheque', 'Cheque'),
                              ('bank', 'Bank'),
                              ],default="cheque")


    payment_code = fields.Char(string="Payment Code", required=False, )

    @api.model
    def create(self, values):

        if 'state_payment' in values:
            if values['state_payment'] == 'cash':
                        values['payment_code'] = self.env['ir.sequence'].next_by_code('pay.cash.seq')
            elif values['state_payment'] == 'visa':
                        values['payment_code'] = self.env['ir.sequence'].next_by_code('pay.visa.seq')
            elif values['state_payment'] == 'cheque':
                        values['payment_code'] = self.env['ir.sequence'].next_by_code('pay.cheque.seq')
            elif values['state_payment'] == 'bank':
                        values['payment_code'] = self.env['ir.sequence'].next_by_code('pay.Bank.seq')
            return super(PaymentStrg, self).create(values)

    def write(self, vals):
            print("values :> ", vals)
            if 'state_payment' in vals:
                if vals['state_payment'] == 'cash':
                    vals['payment_code'] = self.env['ir.sequence'].next_by_code('pay.cash.seq')
                elif vals['state_payment'] == 'visa':
                    vals['payment_code'] = self.env['ir.sequence'].next_by_code('pay.visa.seq')
                elif vals['state_payment'] == 'cheque':
                    vals['payment_code'] = self.env['ir.sequence'].next_by_code('pay.cheque.seq')
                elif vals['state_payment'] == 'bank':
                    vals['payment_code'] = self.env['ir.sequence'].next_by_code('pay.Bank.seq')

            return super(PaymentStrg, self).write(vals)

    receipt_date = fields.Date(string="Receipt Date", required=False, )
    is_print = fields.Boolean(string=" Is Print",  )
    is_no_enter_total = fields.Boolean(string="No With Payment",  )