# -*- coding: utf-8 -*-

from odoo import api, fields, models
from odoo.tools.safe_eval import safe_eval

class OdooPlayGround(models.Model):
    _name = "odoo.playground"
    _description = "Odoo PlayGround"

    DEFAULT_ENV_VARIABLES = """# Available variables:
    # - self: Currnet Object
              #Mevcut Nesne
              
    # - self.env: Odoo Environment on wich the action is trigged
                  #Eylemin tetiklendiği Odoo Ortamı
                  
    # - self.env.user: Return the current user (as an instance)
                       #Geçerli kullanıcıyı döndür (örnek olarak)

    # - self.env.is_system: Return whether the current user has group "Settings", or is in superuser mode.
                            #Geçerli kullanıcının "Ayarlar" grubuna sahip olup olmadığını veya süper kullanıcı modunda olup olmadığını döndürün.
                            
    # - self.env.is_admin: Return whether the current user has group "Access Rights", or is in superuser mode.
                           #Geçerli kullanıcının "Erişim Hakları" grubuna sahip olup olmadığını veya süper kullanıcı modunda olup olmadığını belirtin.

    # - self.env.is_superuser: Return whether the environment is in superuser mode.
                               #Ortamın süper kullanıcı modunda olup olmadığını döndürün.

    # - self.env.company: Return the current company (as an instance)
                          #Mevcut şirketi döndür (örnek olarak)

    # - self.env.companies: Return a recordset of te enabled companies by the user
                            #Kullanıcı tarafından etkinleştirilmiş şirketlerin kayıt kümesini döndürür

    # - self.env.lang: Return the current language code
                       #Geçerli dil kodunu döndür
                       
    # - self.env.cr: Cursor
                       #Db işaretçisi self.env.cr.execute(select * from users)
    
    # - self.env.context: Context
                       #Mevcut sayfa verilerini döndürür self.env.context.get('uid')
                       #{'lang': 'tr_TR', 'tz': 'Europe/Istanbul', 'uid': 7, 'allowed_company_ids': [1], 'params': {'menu_id': 93, 'action': 492, 'model': 'odoo.playground', 'view_type': 'form', 'id': 3, 'cids': 1}}\n\n\n\n"""

    model_id = fields.Many2one('ir.model', string="Model")
    code = fields.Text(string="Code", default=DEFAULT_ENV_VARIABLES)
    result = fields.Text(string="Result")

    def action_execute(self):
        try:
            if self.model_id:
                model = self.env[self.model_id.model]
            else:
                model = self
            self.result = safe_eval(self.code.strip(), {'self': model})
        except Exception as e:
            self.result = str(e)
