

    # def confirm_selection(self):
    #     user = self.env.user
    #     banreservas_group = self.env.ref('banreservas.group_banreservas')
    #     lasfice_group = self.env.ref('precisa_forms.group_lasfice')
        
    #     # Limpiar grupos previos
    #     user.groups_id -= banreservas_group
    #     user.groups_id -= lasfice_group
        
    #     # Asignar grupo según selección
    #     if self.formulario == 'banreservas':
    #         user.groups_id += banreservas_group
    #     elif self.formulario == 'lasfice':
    #         user.groups_id += lasfice_group
from odoo import models, fields, api
from datetime import datetime, timedelta
import base64
from io import BytesIO
import xlsxwriter
from datetime import datetime, timedelta, time
import pytz
 

class SelectFormWizard(models.TransientModel):
    _name = 'select.form.wizard'
    
    formulario = fields.Selection([
        ('banreservas', 'Banreservas'),
        ('lasfice', 'Lasfice')
    ], string="Formulario")

    file_data = fields.Binary("Archivo", readonly=True)
    file_name = fields.Char("Nombre del Archivo", readonly=True)

   
    def confirm_selection(self):
        user = self.env.user
        banreservas_group = self.env.ref('banreservas.group_banreservas')
        lasfice_group = self.env.ref('precisa_forms.group_lasfice')
        work_hours_model = self.env['agent.work.hours']

        # Cerrar cualquier registro de trabajo anterior sin finalizar
        open_work_hours = work_hours_model.search([
            ('user_id', '=', user.id),
            ('end_time', '=', False)
        ])
        open_work_hours.write({'end_time': fields.Datetime.now()})

        # Crear un nuevo registro de trabajo para el formulario seleccionado
        work_hours_model.create({
            'user_id': user.id,
            'form_type': self.formulario,
            'start_time': fields.Datetime.now(),
        })
        
        # Determina el grupo a asignar según la selección
        selected_group = banreservas_group if self.formulario == 'banreservas' else lasfice_group

        # Remueve los grupos que no están seleccionados
        groups_to_remove = (banreservas_group | lasfice_group) - selected_group
        user.groups_id -= groups_to_remove

        # Asigna el grupo seleccionado solo si no pertenece ya a él
        if selected_group not in user.groups_id:
            user.groups_id += selected_group

        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'title': 'Inicio de trabajo',
                'message': f'Has iniciado tu jornada en el formulario: {self.formulario.capitalize()}',
                'type': 'success',  # Tipos: 'success', 'warning', 'info', 'danger'
                'sticky': False,   # True si quieres que la notificación no desaparezca automáticamente
            },
        }

    def action_end_work(self):
        """Finaliza la sesión de trabajo actual del usuario en curso."""
        user = self.env.user
        work_hours_model = self.env['agent.work.hours']

        # Buscar registros de trabajo abiertos para el usuario actual
        open_work_hours = work_hours_model.search([
            ('user_id', '=', user.id),
            ('end_time', '=', False)
        ])
        # Marcar el fin del tiempo de trabajo
        open_work_hours.write({'end_time': fields.Datetime.now()})

        # Identificar los grupos relacionados
        banreservas_group = self.env.ref('banreservas.group_banreservas')
        lasfice_group = self.env.ref('precisa_forms.group_lasfice')

        # Calcular los grupos a eliminar
        groups_to_remove = banreservas_group | lasfice_group

        # Eliminar los grupos relacionados del usuario
        user.groups_id -= groups_to_remove

        # Retornar una notificación al usuario
        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'title': 'Concluyendo jornada de trabajo',
                'message': f'Has concluido tu jornada de trabajo',
                'type': 'success',  # Tipos: 'success', 'warning', 'info', 'danger'
                'sticky': False,    # True si quieres que la notificación no desaparezca automáticamente
            },
        }
    
    def calculate_and_save_daily_hours(self):
        # Llama a la función para obtener las horas diarias
        daily_totals = self.env['agent.work.hours'].calculate_daily_hours_for_banreservas()

        # Guardar cada resultado en el modelo
        for entry in daily_totals:
            self.env['agent.hours.banreservas'].create({
                'date': entry['date'],
                'hours': entry['hours'],
            })


    def action_close_all_sessions_at_6_pm(self):
        """Cerrar todas las sesiones abiertas de trabajo a las 6 PM en la zona horaria local."""
        # Define la zona horaria local
        local_tz = pytz.timezone('America/Santo_Domingo')
        
        # Obtén la hora actual en UTC y convíertela a la hora local ajustada a las 6 PM
        now_utc = datetime.now(pytz.utc)
        today_local = now_utc.astimezone(local_tz).date()
        closing_time_local = datetime.combine(today_local, time(17, 0))
        
        # Convertir la hora de cierre a UTC y luego hacerla naive
        closing_time_utc = local_tz.localize(closing_time_local).astimezone(pytz.utc)
        closing_time_naive = closing_time_utc.replace(tzinfo=None)

        # Cerrar todas las sesiones sin hora de fin
        open_work_hours = self.env['agent.work.hours'].search([
            ('end_time', '=', False)
        ])
        open_work_hours.write({'end_time': closing_time_naive})

   