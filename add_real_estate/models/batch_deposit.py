from odoo import api, fields, models,_

from odoo.exceptions import UserError, ValidationError


class BatchDepositChecks(models.Model):
    _inherit = 'account.batch.payment'


    # counter for validation message in discount check
    #@api.multi
    def refund_under_collections(self,ref_und_coll_batch=None):
        print("enter hereerererererer")
        for rec in self:
            run = False
            for r in rec.payment_ids:
                print("multi_select :: %s",r.multi_select)
                print("state :: %s",r.state)
                if r.multi_select == True and r.state == 'under_coll':
                    run = True
                    r.refund_notes(ref_und_coll_batch=1)
                    # r.refund_under_collection_date = r.ref_coll_batch
                    r.multi_select = False
            if not run:
                raise ValidationError("please select any check to refund it")
            if rec.change_state_refunded_and_collect():
                print("1")
                rec.write({'state': 'done'})
            if rec.change_state_refunded():
                print("2")
                rec.write({'state': 'done'})

