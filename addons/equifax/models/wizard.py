from odoo import models, fields, api
from io import BytesIO
import xlsxwriter
from datetime import datetime
import base64

class ReportWizard(models.TransientModel):
    _name = 'report.wizard.equifax'
    _description = 'Wizard para generación de reportes'

    start_date = fields.Date(string="Fecha de inicio")
    end_date = fields.Date(string="Fecha de fin")
    status= fields.Many2one(
        'equifax.stage', 
        string="Estado",
        group_expand='_read_group_stage_ids', 
        tracking=True
    )
    agent_id = fields.Many2one('res.users', string="Agente")
    report_file = fields.Binary(string='Archivo Excel')
    report_name = fields.Char("Nombre del archivo", default="Reporte llamadas.xlsx")

    @api.model
    def _read_group_stage_ids(self, stages, domain, order):
        return self.env['equifax.stage'].search([])

    def _generate_excel_file(self, form_data, start_date, end_date, agent=None, state=None):
        """Generar el archivo Excel con los datos de llamadas."""
        output = BytesIO()
        workbook = xlsxwriter.Workbook(output, {'in_memory': True})

        
        # Segunda hoja para el desglose por agentes
        sheet = workbook.add_worksheet('Reporte por Agente')

        # Encabezados para el desglose por agente
        sheet.write(0, 0, 'Nombre del Agente')
        sheet.write(0, 1, 'Nombre del Cliente')
        sheet.write(0, 2, 'Apellido del Cliente')
        sheet.write(0, 3, 'Cédula del Cliente')
        sheet.write(0, 4, 'Fecha')
        sheet.write(0, 5, 'Estado de la Llamada')
        

        # Filtrar por agente y estado
        if agent and state:
            agent_forms = form_data.filtered(lambda r: r.create_uid.id == agent.id and r.stage_id == state)
        elif agent:
            agent_forms = form_data.filtered(lambda r: r.create_uid.id == agent.id)
        elif state:
            agent_forms = form_data.filtered(lambda r: r.stage_id == state)
        else:
            agent_forms = form_data

        # Rellenar los datos de la tabla por agente
        row = 1
        for record in agent_forms:
            sheet.write(row, 0, record.user_id.name)
            sheet.write(row, 1, record.partner_id.first_name or '')
            sheet.write(row, 2, record.partner_id.last_name or '')
            sheet.write(row, 3, record.partner_id.document or '') 
            sheet.write(
                row, 4,
                record.contact_date.strftime('%Y-%m-%d') if record.contact_date 
                else (record.create_date.strftime('%Y-%m-%d %H:%M:%S') if record.create_date else '')
            )
            sheet.write(row, 5, record.stage_id.name)
            
            row += 1

        # Espacio entre las dos tablas
        row += 2  # Aumentar la fila para dejar un espacio

        sheet = workbook.add_worksheet('Reporte de efectividad')
        col_estado_start = 0  # Comenzar en la columna 8, al lado de la tabla de agentes
        sheet.write(0, col_estado_start, 'Efectividad por Estados')

        # Encabezado para la tabla de efectividad por estado
        header_row = 1
        headers = ['Agente', 'Ganada', 'Perdida', 'Volver a Llamar', 'Ilocalizable', 'No Contestado', 'Efectividad Total (%)']
        for col, header in enumerate(headers):
            sheet.write(header_row, col_estado_start + col, header)

        # Verificar si hay un agente seleccionado en el wizard
        if agent:
            agents = [agent]  # Solo se procesa el agente seleccionado
        else:
            agents = self.env['res.users'].search([])  # Se procesan todos los agentes si no hay uno seleccionado

        # Rellenar la tabla con los agentes y su efectividad por estado
        row = header_row + 1  # Fila donde empiezan los datos
        for agent in agents:
            # Filtrar formularios por agente
            agent_forms = form_data.filtered(lambda r: r.user_id.id == agent.id)
            total_forms = len(agent_forms)

            if total_forms > 0:
                won_forms = len(agent_forms.filtered(lambda r: r.stage_id.name == 'Aceptado'))
                lost_forms = len(agent_forms.filtered(lambda r: r.stage_id.name == 'Rechazado'))
                call_back_forms = len(agent_forms.filtered(lambda r: r.stage_id.name == 'Volver a llamar'))
                untraceable_forms = len(agent_forms.filtered(lambda r: r.stage_id.name == 'Ilocalizable'))
                not_answered_forms = len(agent_forms.filtered(lambda r: r.stage_id.name == 'No contactado'))
                interested = len(agent_forms.filtered(lambda r: r.stage_id.name == 'Interesado/Comprara plan'))

                # Calcular efectividad para cada estado
                effectiveness_won = (won_forms / total_forms * 100) if total_forms > 0 else 0
                effectiveness_lost = (lost_forms / total_forms * 100) if total_forms > 0 else 0
                effectiveness_call_back = (call_back_forms / total_forms * 100) if total_forms > 0 else 0
                effectiveness_untraceable = (untraceable_forms / total_forms * 100) if total_forms > 0 else 0
                effectiveness_not_answered = (not_answered_forms / total_forms * 100) if total_forms > 0 else 0
                effectiveness_interested = (interested / total_forms * 100) if total_forms > 0 else 0
                effectiveness_total = (won_forms / total_forms * 100) if total_forms > 0 else 0

                # Escribir los datos en la fila correspondiente al agente
                sheet.write(row, col_estado_start + 0, agent.name)  # Nombre del agente
                sheet.write(row, col_estado_start + 1, f"{effectiveness_won:.2f}%")  # Efectividad Ganada
                sheet.write(row, col_estado_start + 2, f"{effectiveness_lost:.2f}%")  # Efectividad Perdida
                sheet.write(row, col_estado_start + 3, f"{effectiveness_call_back:.2f}%")  # Efectividad Volver a Llamar
                sheet.write(row, col_estado_start + 4, f"{effectiveness_untraceable:.2f}%")  # Efectividad Ilocalizable
                sheet.write(row, col_estado_start + 5, f"{effectiveness_not_answered:.2f}%")  # Efectividad No Contestado
                sheet.write(row, col_estado_start + 6, f"{effectiveness_interested:.2f}%")  # Efectividad No Contestado
                sheet.write(row, col_estado_start + 7, f"{effectiveness_total:.2f}%")  # Efectividad Total

                row += 1

        workbook.close()
        output.seek(0)
        return output.read()
    
    def generate_report(self):
        """Generar el reporte de Excel según los filtros aplicados."""
        # Buscar todos los formularios (no solo los del usuario actual)
        form_data = self.env['equifax'].sudo().search([])
        state = ''

        # Filtrar por fechas si se seleccionaron
        if self.start_date and self.end_date:
        # Filtrar form_data usando closing_date si existe, de lo contrario usar date_local
            form_data = form_data.filtered(
                lambda r: self.start_date <= (r.contact_date or r.create_date.date()) <= self.end_date
            )


        if self.status != 'all':
            state = self.status
        # Generar el archivo Excel
        report_content = self._generate_excel_file(form_data, self.start_date, self.end_date, self.agent_id, state)

        # Guardar el archivo en binario
        self.report_file = base64.b64encode(report_content)

        return {
            'type': 'ir.actions.act_url',
            'url': f"/web/content/{self._name}/{self.id}/report_file/{self.report_name}",
            'target': 'self',
        }
    
class EquifaxClientCounterWizard(models.TransientModel):
    _name = 'equifax.client.counter.wizard'
    _description = 'Contador de Clientes por Gestionar'

    total_clients = fields.Integer(string="Total de Clientes Asignados", readonly=True)
    managed_clients = fields.Integer(string="Clientes Gestionados", readonly=True)
    remaining_clients = fields.Integer(string="Clientes por Gestionar", compute="_compute_remaining_clients", store=False)

    @api.model
    def default_get(self, fields_list):
        res = super(EquifaxClientCounterWizard, self).default_get(fields_list)
        
        # Obtener el usuario actual
        current_user_id = self.env.uid

        # Contar todos los clientes asignados al usuario actual en res.partner
        assigned_clients = self.env['res.partner'].search_count([
            ('user_id', '=', current_user_id), 
            ('campaign', '=', 'equifax')
        ])

        # Contar los clientes que ya tienen un registro en el modelo equifax
        managed_clients = self.env['equifax'].search_count([
            ('user_id', '=', current_user_id),
            ('stage_id', '!=', False)
        ])

        # Asignar valores al wizard
        res.update({
            'total_clients': assigned_clients,
            'managed_clients': managed_clients,
            'remaining_clients': assigned_clients - managed_clients
        })
        return res

    @api.depends('total_clients', 'managed_clients')
    def _compute_remaining_clients(self):
        for record in self:
            record.remaining_clients = record.total_clients - record.managed_clients

    def open_wizard(self):
        """Método para abrir el wizard."""
        return {
            'type': 'ir.actions.act_window',
            'name': 'Clientes por Gestionar',
            'view_mode': 'form',
            'res_model': 'equifax.client.counter.wizard',
            'target': 'new',
            'context': self.env.context,
        }





