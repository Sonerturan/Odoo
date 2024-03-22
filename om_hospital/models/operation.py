# -*- coding: utf-8 -*-

from odoo import api, fields, models, _


class HospitalOperation(models.Model):
    _name = "hospital.operation"
    _description = "Hospital Operation"
    _log_access = False
    _order = 'sequence,id'

    # _log_access alanı create_date, create_uid, write_date, write_uid değerlerini DB' ye eklemez
    # Many2one ile uzaktan create işlemi oluşturmayı kapatır
    # _rec_name değeri bulunmaz

    doctor_id = fields.Many2one('res.users', string='Doctor')
    operation_name = fields.Char(string='Name')
    reference_record = fields.Reference(selection=[('hospital.patient', 'Patient'),
                                                   ('hospital.appointment', 'Appointment')], string='Record')

    sequence = fields.Integer(string="Sequence", default=10)

    # many2one field' lar ile uzaktan yapılan create işlemini inherit alır
    @api.model
    def name_create(self, name):
        return self.create({'operation_name': name}).name_get()[0]