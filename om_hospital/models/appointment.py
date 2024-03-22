from odoo import api, fields, models, _
from odoo.exceptions import ValidationError


class HospitalAppointment(models.Model):
    _name = "hospital.appointment"
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _description = "Hospital Appointment"
    _ref = 'ref'
    _order = 'id desc'

    name = fields.Char(string='Name', tracking=True, readonly=True)
    # Kayıt adını diğer tablodan gelen değerden alır. Çünkü name alanı yok ve _rec_name tanımlanmış
    _rec_name = "name"
    # ondelete='restrict' --> patient deki bağlı olduğu ilgili kaydın silinmesine izin vermez hata verir (çünkü bu kayıt ona bağlı)
    # ondelete='cascade' --> patient deki kayıt silindiğinde appointment daki ilgili kayıtları siler. Tam tersini de yapabilir.
    patient_id = fields.Many2one('hospital.patient', string="Patient", ondelete='restrict', tracking=True)
    # Diğer tablodan related ile  veri çekme (readonly=değiştirilebilirlik kazandırır)
    gender = fields.Selection([('male', 'Male'), ('female', 'Female')], string="Gender", related='patient_id.gender',
                              readonly=False)
    appointment_time = fields.Datetime(string="Appointment Time", default=fields.Datetime.now)
    booking_date = fields.Date(string="Booking Date", default=fields.Date.context_today, tracking=True)
    ref = fields.Char(string='Reference')
    prescription = fields.Html(string="Prescription")
    priority = fields.Selection([
        ('0', 'Normal'),
        ('1', 'Low'),
        ('2', 'High'),
        ('3', 'Very High')], string="Priority")
    state = fields.Selection([
        ('draft', 'Draft'),
        ('in_consultation', 'In Consultation'),
        ('done', 'Done'),
        ('cancel', 'Cancel')], default='draft', string="Status", required=True, tracking=True)
    doctor_id = fields.Many2one('res.users', string='Doctor', tracking=True)
    pharmacy_line_ids = fields.One2many('appointment.pharmacy.lines', 'appointment_id', string="Pharmacy Lines")
    hide_sales_price = fields.Boolean(string="Hide Sales Price", default=False)
    operation_id = fields.Many2one('hospital.operation', string='Operation')
    progress = fields.Integer(string='Progress', compute='_compute_progress')
    duration = fields.Float(string='Duration', tracking=True)

    company_id = fields.Many2one('res.company', string='Company', default=lambda self:self.env.company)
    currency_id = fields.Many2one('res.currency', related='company_id.currency_id')

    # Pharmacy alanınına girilen değerlerin create ve edit' e basılma durumunda numaralandırmak için oluşturuldu
    def set_line_number(self):
        sl_no = 0
        for line in self.pharmacy_line_ids:
            sl_no += 1
            line.sl_no = sl_no

    # Form'daki Save (Create) Butonunu Inherit Alma
    # formdaki save butonunu inherit alıyoruz
    # buradaki vals form' a create anında gönderilen verileri içerir.
    @api.model
    def create(self, vals):
        vals['name'] = self.env['ir.sequence'].next_by_code('hospital.appointment')
        res = super(HospitalAppointment, self).create(vals)
        res.set_line_number()
        return res

    def write(self, vals):
        if not self.name and not vals.get('name'):
            vals['name'] = self.env['ir.sequence'].next_by_code('hospital.appointment')
        res = super(HospitalAppointment, self).write(vals)
        self.set_line_number()
        return res

    # Silme işlemini inherit alma
    # silme işlemi için sadece draft olanları gerçekleştir
    def unlink(self):
        for rec in self:
            if self.state != 'draft':
                raise ValidationError(_("You can delete appoinment only in 'Draft' status !"))
        return super(HospitalAppointment, self).unlink()

    # Diğer tablodan  seçilen patient_id ye göre veri çekme (anlık güncelleme)
    @api.onchange('patient_id')
    def onchange_patient_id(self):
        self.ref = self.patient_id.ref

    def action_notification(self):
        message = 'Button click successfull'
        action = self.env.ref('om_hospital.action_hospital_patient')

        # sağ üstte bildirim görünümü yaratmak için
        # sticky: zamanla kaybolma durumu (True durumda manuel x ile kapatılır)
        # type: success, danger, warning
        # links: bağlantı linki eklenebilir bunun için message değerinde %s olmalıdır
        # next sayfa değiştirmek için (sayfa değişip pop up orada görünür)
        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'title': _('Click to open the patient record'),
                'message': message+' %s',
                'type': 'success',
                'links': [{
                    'label': self.patient_id.name,
                    'url': f'#action={action.id}&id={self.patient_id}&model=hospital.patient'
                }],
                'sticky': True,
                'next': {
                    'type': 'ir.actions.act_window',
                    'res_model': 'hospital.patient',
                    'res_id': self.patient_id.id,
                    'views': [(False, 'form')]
                }
            }
        }

    def action_test(self):
        return {
            'type': 'ir.actions.act_url',
            'target': 'new',
            'url': 'https://www.odoo.com'
        }

    def action_share_whatsapp(self):
        if not self.patient_id.phone:
            raise ValidationError(_("Missing phone number in patient record!"))
        message = 'Hi %s, you appointment number is: %s, Thank you' % (self.patient_id.name, self.name)
        whatsapp_api_url = 'https://api.whatsapp.com/send?phone=%s&text=%s' % (self.patient_id.phone, message)

        #Chatter a mesaj yazma
        self.message_post(body=message, subject='Whatsapp')

        return {
            'type': 'ir.actions.act_url',
            'target': 'new',
            'url': whatsapp_api_url
        }

    def action_in_consultation(self):
        for rec in self:
            if rec.state == 'draft':
                rec.state = 'in_consultation'

    def action_done(self):
        for rec in self:
            rec.state = 'done'
            # Rainbow Effect
        return {
            'effect': {
                'fadeout': 'slow',
                'message': 'Done',
                'type': 'rainbow_man',
            }
        }

    #def action_cancel(self):
    #    for rec in self:
    #        rec.state = 'cancel'

    def action_cancel(self):
        action = self.env.ref('om_hospital.action_cancel_appointment').read()[0]
        return action

    def action_draft(self):
        for rec in self:
            rec.state = 'draft'

    @api.depends('state')
    def _compute_progress(self):
        for rec in self:
            if rec.state == 'draft':
                progress = 25
            elif rec.state == 'in_consultation':
                progress = 50
            elif rec.state == 'done':
                progress = 100
            else:
                progress = 0
            rec.progress = progress

class AppointmentPharmacyLines(models.Model):
    _name = "appointment.pharmacy.lines"
    _description = "Appointment Pharmacy Lines"

    sl_no = fields.Integer(string="SNO.")
    product_id = fields.Many2one('product.product', required=True)
    price_unit = fields.Float(string="Price", related='product_id.list_price')
    qty = fields.Integer(string="Quantity", default=1)
    appointment_id = fields.Many2one('hospital.appointment', string='Appointment')
    currency_id = fields.Many2one('res.currency', related='appointment_id.currency_id')
    price_subtotal = fields.Monetary(string="Subtotal", compute="_compute_price_subtotal",
                                     currency_field='currency_id')

    @api.depends('price_unit', 'qty')
    def _compute_price_subtotal(self):
        for rec in self:
            rec.price_subtotal = rec.price_unit * rec.qty