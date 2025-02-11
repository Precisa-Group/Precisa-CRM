from odoo import models, fields, api
from datetime import datetime, timedelta
from odoo.exceptions import UserError

class AgentWorkHours(models.Model):
    _name = 'agent.work.hours'
    _description = 'Registro de Horas de Trabajo de Agentes'

    user_id = fields.Many2one('res.users', string='Agente', required=True)
    form_type = fields.Selection([
        ('banreservas', 'Banreservas'),
        ('lasfice', 'Lasfice')
    ], string="Formulario", required=True)
    start_time = fields.Datetime(string='Hora de Inicio', default=fields.Datetime.now)
    end_time = fields.Datetime(string='Hora de Fin')
    total_hours = fields.Float(string='Total de Horas', compute='_compute_total_time', store=True)
    total_minutes = fields.Integer(string='Total de Minutos', compute='_compute_total_time', store=True)
    total_seconds = fields.Integer(string='Total de Segundos', compute='_compute_total_time', store=True)

    @api.depends('start_time', 'end_time')
    def _compute_total_time(self):
        for record in self:
            if record.start_time and record.end_time:
                duration = record.end_time - record.start_time
                total_seconds = duration.total_seconds()
                record.total_hours = int(total_seconds // 3600)
                record.total_minutes = int((total_seconds % 3600) // 60)
                record.total_seconds = int(total_seconds % 60)
            else:
                record.total_hours = 0
                record.total_minutes = 0
                record.total_seconds = 0
    
    @api.model
    def calculate_daily_hours_for_banreservas(self):
        # Filtrar los registros con form_type 'banreservas'
        banreservas_hours = self.search([
            ('form_type', '=', 'banreservas'),
            ('start_time', '!=', False),
            ('end_time', '!=', False)
        ])

        if not banreservas_hours:
            raise UserError("No se encontraron registros con el tipo de formulario 'banreservas' y tiempos válidos.")

        # Inicializar el diccionario de resultados
        daily_totals = {}

        for record in banreservas_hours:
            date_key = record.start_time.date()  # Usar la fecha como clave

            if date_key not in daily_totals:
                # Inicializar horas en 0 y formatear la fecha
                daily_totals[date_key] = 0

            # Calcular la duración en horas y sumarla al total
            duration = (record.end_time - record.start_time).total_seconds() / 3600  # Convertir segundos a horas
            daily_totals[date_key] += duration

        # Redondear las horas a 2 decimales
        for date in daily_totals:
            daily_totals[date] = round(daily_totals[date], 2)
        
        formatted_daily_totals = {date.strftime('%Y-%m-%d'): hours for date, hours in daily_totals.items()}
    

        # Convertir el diccionario para devolver una lista de valores ordenada
        return sorted(
            [{'date': date, 'hours': hours} for date, hours in formatted_daily_totals.items()],
            key=lambda x: x['date']
        )


    # def action_end_work(self):
    #     """Establece la hora de fin en el momento actual para la sesión del usuario en curso."""
    #     self.ensure_one()
    #     if not self.end_time:
    #         self.end_time = fields.Datetime.now()

    # @api.model
    # def action_close_all_sessions_at_6_pm(self):
    #     """Cierra todas las sesiones abiertas al establecer la hora de fin a las 6 PM para las que no tienen end_time."""
    #     now = fields.Datetime.now()
    #     six_pm_today = now.replace(hour=18, minute=0, second=0, microsecond=0)
        
    #     # Cerrar sesiones abiertas sin hora de fin
    #     sessions = self.search([('end_time', '=', False)])
    #     for session in sessions:
    #         if session.start_time.date() == six_pm_today.date():  # Asegura que sea la fecha de hoy
    #             session.end_time = six_pm_today if six_pm_today <= now else now
