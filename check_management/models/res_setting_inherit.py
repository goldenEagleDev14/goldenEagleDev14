from odoo import api, fields, models ,_
import logging


_logger = logging.getLogger(__name__)

class ResBaseConfigSettings(models.TransientModel):

    _name = "my.config.settings"   # that's prototype inheritance (vs. class inheritance if omitted)
                                   # see https://www.odoo.com/documentation/10.0/howtos/backend.html#inheritance

    _inherit = "res.config.settings"


    @api.model
    def set_setting_batch_parameters(self):
        _logger.info("> Settings sign-up parameters")


        settings = self.env['res.config.settings'].create({
            'module_l10n_us_check_printing': True,
            'module_account_batch_payment': True,
        })
        settings.execute()
        _logger.info(">done")