from odoo import models, fields, api


class Travel(models.Model):
    _name = 'travel.travel'

    name = fields.Char(string="Name")
    destination = fields.Char(string="Destination")
    start_date = fields.Char(string="Start Date")
    end_date = fields.Char(string="End Date")
