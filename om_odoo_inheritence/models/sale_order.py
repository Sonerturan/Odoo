# -*- coding: utf-8 -*-

from odoo import api, fields, models


class SaleOrder(models.Model):
    _inherit = "sale.order"

    confirmed_user_id = fields.Many2one('res.users', string="Confirmed User")

    
    def action_confirm(self):
        #super ile _inherit aldığımız modeldeki methodu da inherit alıyoruz(devralıyoruz ve ekleme yapabiliriz)
        #mevcut method inherit alınmadan(super kullanılmadan) method oluşturulursa, mevcut methodu ezmiş olursunuz(sadece burası çalışır)
        super(SaleOrder, self).action_confirm()
        
        self.confirmed_user_id = self.env.user.id
