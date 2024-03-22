# -*- coding: utf-8 -*-

from odoo import api, fields, models


class ResGroups(models.Model):
    _inherit = "account.move"

    so_confirmed_user_id = fields.Many2one('res.users', string="So Confirmed User")
