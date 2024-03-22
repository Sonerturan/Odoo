# -*- coding: utf-8 -*-

from odoo import api, fields, models, _
from datetime import date
from odoo.exceptions import ValidationError
from dateutil import relativedelta


class HospitalPatient(models.Model):
    _name = "hospital.patient"
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _description = "Hospital Patient"

    # Kayıt adını belirtir girilmez ise default name degiskenini alır
    # _rec_name = "name"
    name = fields.Char(string='Name', tracking=True)
    date_of_birth = fields.Date(string="Date of Birth")
    # bu model değerini bir fonksiyondan alacak
    calculated_age = fields.Integer(string='Calculated Age',
                                    compute="_compute_calculated_age",
                                    inverse="_inverse_compute_calculated_age",
                                    search='_search_calculated_age')
    ref = fields.Char(string='Reference')
    age = fields.Integer(string='Age', tracking=True)
    gender = fields.Selection([('male', 'Male'), ('female', 'Female')], string="Gender", default='male')
    active = fields.Boolean(string="Active", default=True)
    appointment_id = fields.Many2one('hospital.appointment', string="Appointment")
    image = fields.Image(string="Image")
    tag_ids = fields.Many2many('patient.tag', string="Tags")
    appointment_count = fields.Integer(string='Appointment Count', compute='_compute_appointment_count', store=True)
    appointment_ids = fields.One2many('hospital.appointment', 'patient_id', string='Appointment')
    parent = fields.Char(string="Parent")
    marital_status = fields.Selection([('married', 'Married'), ('single', 'Single')], string="Marial Status", tracking=True)
    partner_name = fields.Char(string="Partner Name")
    is_birthday = fields.Boolean(string='Birthday ?', compute='_compute_is_birthday')
    phone = fields.Char(string="Phone")
    email = fields.Char(string="Email")
    website = fields.Char(string="Website")

    # @api.depends --> belirtilen değer her değiştiğinde tekrardan _compute için çalışacak, hesaplama yapacak
    # store=True yapısı DB ye kaydedilmesini sağlar. Bu yüzden her defasında yeniden hesaplama olmaz bunun için api dependsd kullandık
    # store=True kullanmasaydık DB ye kaydetmeyecekti bunun için @api.depends e de gerek kalmazdı
    # @api.depends in çalışması için değişen bir yapı olduğunda çalışması gerekir bunun için appointment_ids field i oluşturulmuştur.
    @api.depends('appointment_ids')
    def _compute_appointment_count(self):
        for rec in self:
            rec.appointment_count = self.env['hospital.appointment'].search_count([('patient_id', '=', rec.id)])

    #contrains decorator' ü ile date of birth alanına kısıtlama ekledik (hastanın doğum tarihi güncel zamandan büyük olamaz)
    @api.constrains('date_of_birth')
    def _check_date_of_birth(self):
        for rec in self:
            if rec.date_of_birth and rec.date_of_birth > fields.Date.today():
                raise ValidationError(_("The entered date of birth is not acceptable !"))

    @api.ondelete(at_uninstall=False)
    def _check_appointments(self):
        for rec in self:
            if rec.appointment_ids:
                raise ValidationError(_("You cannot delete a patient with appointments !"))

    # Form'daki Save (Create) Butonunu Inherit Alma
    # formdaki save butonunu inherit alıyoruz
    # buradaki vals form' a create anında gönderilen verileri içerir.
    @api.model
    def create(self, vals):
        vals['ref'] = self.env['ir.sequence'].next_by_code('hospital.patient')
        return super(HospitalPatient, self).create(vals)

    def write(self, vals):
        if not self.ref and not vals.get('ref'):
            vals['ref'] = self.env['ir.sequence'].next_by_code('hospital.patient')
        return super(HospitalPatient, self).write(vals)

    # compute kullanımı model de bulunan field için değer sağlanması (@decarator= anlık değşim gözlenmesi için)
    @api.depends('date_of_birth')
    def _compute_calculated_age(self):
        for rec in self:
            today = date.today()
            if rec.date_of_birth:
                rec.calculated_age = today.year - rec.date_of_birth.year
            else:
                rec.calculated_age = 1

    # Tersine fonksiyon yazmak için
    @api.depends('calculated_age')
    def _inverse_compute_calculated_age(self):
        today = date.today()
        for rec in self:
            rec.date_of_birth = today - relativedelta.relativedelta(years=rec.calculated_age)

    #calculated_age değeri compute olup DB ye kaydedilmediği için search kısmında yapılan filtrelemede etki göstermeyeceğinden dolayı...+
    #DB ye kaydedilmeyen field lar üzerinde arama yapabilmek için bu fonksiyon kullanılır.
    #buradaki value değeri filtrelemede search için girilen değerdir.
    def _search_calculated_age(self, operator, value):
        date_of_birth = date.today() - relativedelta.relativedelta(years=value)
        start_of_year = date_of_birth.replace(day=1, month=1)
        end_of_year = date_of_birth.replace(day=31, month=12)
        return [('date_of_birth', '>=', start_of_year), ('date_of_birth', '<=', end_of_year)]



    #Model ile ilişki kurulurken _rec değerini name_get ile inherit etme -> " [HP001] Soner "
    def name_get(self):
        return [(record.id, "[%s] %s" % (record.ref, record.name)) for record in self]

    def action_test(self):
        print("clicked")
        return

    @api.depends('date_of_birth')
    def _compute_is_birthday(self):
        for rec in self:
            is_birthday = False
            if rec.date_of_birth:
                today = date.today()
                if today.day == rec.date_of_birth.day and today.month == rec.date_of_birth.month:
                    is_birthday = True
            rec.is_birthday = is_birthday

    def action_view_appointments(self):
        return {
            'name': _('Appointments'),
            'res_model': 'hospital.appointment',
            'view_mode': 'list,form,calendar,activity',
            'context': {'default_patient_id': self.id},
            'domain': [('patient_id', '=', self.id)],
            'target': 'current',
            'type': 'ir.actions.act_window',
        }
