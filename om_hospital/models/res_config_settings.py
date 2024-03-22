# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import fields, models


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    # Model transient yapıda olduğu için DB ye kaydedilmeyecektir.
    # Fakat config_parameter='' değeri ile settings bölümünden technical yapısına System parameters altında Config parametresi olarak kaydedilecektir.
    cancel_day = fields.Integer(string='Cancel Days', config_parameter='om_hospital.cancel_day')
