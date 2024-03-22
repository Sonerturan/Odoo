# -*- coding: utf-8 -*-

from odoo import api, fields, models


class ResGroups(models.Model):
    _inherit = "res.groups"

    # settings>users alanında bulunan technical group lardan gizleme işleme yapmak için kullanılır.
    def get_application_groups(self, domain):
        group_id = self.env.ref('product.group_product_variant').id
        wave_id = self.env.ref('account.group_sale_receipts').id
        return super(ResGroups, self).get_application_groups(domain + [('id', 'not in', (group_id, wave_id))])
