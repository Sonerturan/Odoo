import datetime
from odoo import api, fields, models, _
from odoo.exceptions import ValidationError
from datetime import date
from dateutil import relativedelta


class CancelAppointmentWizard(models.TransientModel):
    _name = "cancel.appointment.wizard"
    _description = "Cancel Appointment Wizard"

    @api.model
    def default_get(self, fields):
        res = super(CancelAppointmentWizard, self).default_get(fields)
        res['date_cancel'] = datetime.date.today()
        if self.env.context.get('active_id'):
            res['appointment_id'] = self.env.context.get('active_id')
        return res

    appointment_id = fields.Many2one('hospital.appointment', string="Appointment", domain=[('state', '=', 'draft'), ('priority', 'in', ('0', '1', False))])
    reason = fields.Text(string="Reason", default='Test Reason')
    date_cancel = fields.Date(string="Cancellation Date")

    def action_cancel(self):
        cancel_day = self.env['ir.config_parameter'].sudo().get_param('om_hospital.cancel_day')

        allowed_date = self.appointment_id.booking_date - relativedelta.relativedelta(days=int(cancel_day))
        if allowed_date < date.today():
            raise ValidationError(_("Sorry, cancellation is not allowed for this booking (Tarih sorunu)"))
        self.appointment_id.state = 'cancel'

        # Database' e doğrudan erişerek işlem yapma
        query = """select name from hospital_patient"""
        self.env.cr.execute(query)
        #patients = self.env.cr.fetchall()
        # kayıtları dict formatında döner
        #patients = self.env.cr.dictfetchall()
        # dictfetchallone sadece 1 adet kayıt döner
        patients = self.env.cr.dictfetchallone()
        print('patients----->', patients)

        #Bu yapı ile wizard işlemden sonra kapanmıyor bir sonraki işlem için yine ekranda kalıyor
        return {
            'type': 'ir.actions.act_window',
            'view_mode': 'form',
            'res_model': 'cancel.appointment.wizard',
            'target': 'new',
            'res_id': self.id
        }

        #bu method kullanıldıktan sonra sayfa yenilenir.
        #return {
        #    'type': 'ir.actions.client',
        #    'tag': 'reload',
        #}