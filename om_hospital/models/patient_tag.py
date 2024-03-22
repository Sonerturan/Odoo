# -*- coding: utf-8 -*-

from odoo import api, fields, models, _


class PatientTag(models.Model):
    _name = "patient.tag"
    _description = "Patient Tag"

    name = fields.Char(string="Name", required=True)
    # copy=False --> False olanları yani aktif olmayanları kopyaladığında aktif(default değer) yapar
    active = fields.Boolean(string="Active", default=True, copy=False)
    color = fields.Integer(string="Color")
    color_2 = fields.Char(string="Color 2")
    sequence = fields.Integer(string="Sequence")

    # Duplicate Yani Kopyala işlemini inherit alma
    # Kopyalama işleminde name değerini direk yazmak yerine yanına (copy) yazar
    # Sequence değerini 10 yapar
    @api.returns('self', lambda value: value.id)
    def copy(self, default=None):
        if default is None:
            default = {}
        if not default.get('name'):
            default['name'] = _("%s (copy)", self.name)
        default['sequence'] = 10
        return super(PatientTag, self).copy(default)

    #name değeri daha önce kayıtlı ise yeni kayıt oluşturmuyor
    #('unique_tag_name', 'unique (name)', 'Name must be unique')
    #name değeri daha önceden kayıtlı ve aktif olan bir kayıt varsa yeni kayıt oluşturmuyor
    #('unique_tag_name', 'unique (name,active)', 'Name must be unique')
    #Yeni kayıt esnaısnda squence değeri sıfırdan küçükse kabul etme
    #('check_sequence', 'check (sequence > 0)', 'Sequence must be non zero positive number.')
    _sql_constraints = [
        ('unique_tag_name', 'unique (name,active)', 'Name must be unique.'),
        ('check_sequence', 'check (sequence > 0)', 'Sequence must be non zero positive number.')
    ]
