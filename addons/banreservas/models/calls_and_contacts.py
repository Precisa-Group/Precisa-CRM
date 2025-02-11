from odoo import models, fields
from odoo.fields import Datetime


class Calls_and_contacts(models.Model):
    _name = 'calls.and.contacts' 
    _description = 'Manual Call and contacts Entry'

    call_date = fields.Date(string='Fecha de la llamadas', required=True, default=fields.Date.context_today)
    total_calls = fields.Integer(string='Total de la llamadas', required=True, help="Enter the total number of calls made on this date.")
    total_contacts = fields.Integer(string='Total de los contactos', help="Enter the total number of calls made on this date.")
    work_hours = fields.Integer(string='Total de horas trabajas')
    total_agents = fields.Integer(string='Total de agentes')
    
    def action_save_calls(self):
        """
        Guarda el conteo de llamadas en un modelo principal.
        Si ya existe un registro para la misma fecha, lo actualiza.
        """
        # Busca un solo registro existente con la misma fecha
        existing_record = self.env['calls.and.contacts'].search([
            ('call_date', '=', self.call_date)
        ], limit=1)

        if existing_record:
            # Si el registro existe, lo actualiza
            existing_record.write({
                'total_calls': self.total_calls,
                'total_contacts': self.total_contacts,
                'total_agents': self.total_agents
            })
        else:
            # Si no existe, crea un nuevo registro
            self.env['calls.and.contacts'].create({
                'total_calls': self.total_calls,
                'call_date': self.call_date,
                'total_contacts': self.total_contacts,
                'total_agents': self.total_agents
            })

        duplicate_records = self.env['calls.and.contacts'].search([
            ('call_date', '=', self.call_date)
        ])
        if len(duplicate_records) > 1:
            duplicate_records[1:].unlink()

        return {'type': 'ir.actions.act_window_close'}

    def get_totals_by_date(self, date):
        """
        Retorna el total de llamadas y contactos para una fecha específica.
        :param date: Fecha en formato 'YYYY-MM-DD'.
        :return: Diccionario con 'total_calls' y 'total_contacts' o None si no hay datos para esa fecha.
        """

        # Buscar el registro dentro del rango de la fecha
        record = self.env['calls.and.contacts'].search([
            ('call_date', '=', date,)
        ], limit=1)

        if record:
            return [
                record.total_calls,
                record.total_contacts,
                record.work_hours,
                record.total_agents
            ]
        return [0,0,0,0]