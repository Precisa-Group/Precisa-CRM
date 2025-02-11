from odoo import models, fields, api
import pytz
from datetime import datetime

class CallHistory(models.Model):
    _name = 'call.history'
    _description = 'Historial de llamadas y comentarios'

    comment = fields.Text(string="Comentario", required=True)
    state = fields.Selection([
        ('new', 'Nuevo'),
        ('win','Ganada'),
        ('lost','Rechazada'),
        ('call_back','Volver a llamar'),
        ('untraceable','Ilocalizable'),
        ('not_answered','No contestado'),
    ], default='new', string="Estado")
    call_date = fields.Datetime(string="Fecha de la llamada", default=fields.Datetime.now)
    form_id = fields.Many2one('precisa_forms.form', string="Formulario relacionado")
    user_id = fields.Many2one('res.users', string="Agente", default=lambda self: self.env.user, readonly=True)

    # @api.model
    # def _get_default_call_date(self):
    #     # Obtener la zona horaria de Santo Domingo
    #     santo_domingo_tz = pytz.timezone('America/Santo_Domingo')
    #     # Obtener la hora actual en UTC
    #     utc_now = datetime.now(pytz.utc)
    #     # Convertir la hora a la zona horaria de Santo Domingo
    #     santo_domingo_time = utc_now.astimezone(santo_domingo_tz)
    #     self.actualizar_fecha_creacion_local()
    #     # Convertir el datetime a naive eliminando la información de zona horaria
    #     return santo_domingo_time.replace(tzinfo=None)


    # def actualizar_fecha_creacion_local(self):
    #     # Obtener la zona horaria de Santo Domingo
    #     santo_domingo_tz = pytz.timezone('America/Santo_Domingo')

    #     # Buscar todos los registros de 'call.history'
    #     call_records = self.env['call.history'].search([])

    #     for record in call_records:
    #         if record.call_date:
    #             # Convertir la fecha call_date en UTC a la zona horaria de Santo Domingo
    #             utc_date = record.call_date.replace(tzinfo=pytz.utc)
    #             santo_domingo_date = utc_date.astimezone(santo_domingo_tz)

    #             # Convertir la fecha de Santo Domingo a una fecha naive (sin zona horaria)
    #             santo_domingo_date_naive = santo_domingo_date.replace(tzinfo=None)

    #             # Actualizar el campo call_date con la fecha naive
    #             record.write({'call_date': santo_domingo_date_naive})

    #     return True