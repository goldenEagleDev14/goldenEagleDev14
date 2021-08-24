from odoo import models, fields, api, _

class AccountMove(models.Model):
    _inherit = "account.move"

    is_contract = fields.Boolean(string="Is Contract", readonly=True )
    reservation_id = fields.Many2one(comodel_name="res.reservation", string="Reservation", required=False, )
    broker_id = fields.Many2one(related="reservation_id.broker_id",comodel_name="res.partner", string="Broker", required=False, )


    def action_post(self):
        res = super(AccountMove, self).action_post()
        if self.reservation_id:
                total_ins = 0

                for line in self.reservation_id.payment_strg_ids:
                    print("line.reserve_id.id,", line.reserve_id.id)
                    print("line.reserve_id.id,", line.cheque)
                    print("line.reserve_id.id,", line.id)
                    # if line.cheque:
                    #     strg = self.env['payment.strg'].search([('id', '=', self.payment_strg_ids.ids),('cheque','=',line.cheque),('id','!=',line.id)])
                    #     if strg:
                    #         raise ValidationError(_('Error !,Number Cheque Duplicate.'))

                    if line.is_maintainance == False:
                        total_ins += line.amount

                print("self.env.user.has_group('add_real_estate.group_custom_payment') :> ",
                      self.env.user.has_group('add_real_estate.group_custom_payment'))
                if self.env.user.has_group('add_real_estate.group_custom_payment') == False:
                    # if  self.user_has_groups('add_real_estate.group_custom_payment'):

                    print("total_ins  :> ", total_ins)
                    print("total_ins  :> ", round(total_ins))
                    # print("self.net_price  :> ", self.net_price)
                    # print("self.net_price  :> ", round(self.net_price))
                    if self.reservation_id.pay_strategy_id:
                        if round(total_ins) != round(self.reservation_id.net_price):
                            raise ValidationError(_('Error !,The Total installment is not equal The net Price.'))

                self.reservation_id.state = 'contracted'
                self.reservation_id.property_id.state = 'contracted'


        return res

    def button_draft(self):
        res = super(AccountMove, self).button_draft()
        self.reservation_id.state = 'reserved'
        self.reservation_id.property_id.state = 'reserved'
        return res



class AccountMovedd(models.Model):
    _inherit = "account.move.line"


    @api.onchange('product_id')
    def _onchange_product_id(self):
        print("eid")
        for line in self:
            if not line.product_id or line.display_type in ('line_section', 'line_note'):
                continue

            line.name = line._get_computed_name()
            line.account_id = line._get_computed_account()
            line.tax_ids = line._get_computed_taxes()
            line.product_uom_id = line._get_computed_uom()
            line.price_unit = line._get_computed_price_unit()

            # Manage the fiscal position after that and adapt the price_unit.
            # E.g. mapping a price-included-tax to a price-excluded-tax must
            # remove the tax amount from the price_unit.
            # However, mapping a price-included tax to another price-included tax must preserve the balance but
            # adapt the price_unit to the new tax.
            # E.g. mapping a 10% price-included tax to a 20% price-included tax for a price_unit of 110 should preserve
            # 100 as balance but set 120 as price_unit.
            if line.tax_ids and line.move_id.fiscal_position_id:
                line.price_unit = line._get_price_total_and_subtotal()['price_subtotal']
                line.tax_ids = line.move_id.fiscal_position_id.map_tax(line.tax_ids._origin, partner=line.move_id.partner_id)
                accounting_vals = line._get_fields_onchange_subtotal(price_subtotal=line.price_unit, currency=line.move_id.company_currency_id)
                balance = accounting_vals['debit'] - accounting_vals['credit']
                line.price_unit = line._get_fields_onchange_balance(balance=balance).get('price_unit', line.price_unit)

            # Convert the unit price to the invoice's currency.
            company = line.move_id.company_id
            line.price_unit = company.currency_id._convert(line.price_unit, line.move_id.currency_id, company, line.move_id.date)

        if len(self) == 1:
            return {'domain': {'product_uom_id': [('category_id', '=', self.product_uom_id.category_id.id)]}}
