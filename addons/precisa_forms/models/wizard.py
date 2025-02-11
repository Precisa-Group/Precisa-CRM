from odoo import models, fields, api
from io import BytesIO
import xlsxwriter
from datetime import datetime
import base64

class ReportWizard(models.TransientModel):
    _name = 'report.wizard'
    _description = 'Wizard para generación de reportes de gestiones'

    start_date = fields.Date(string="Fecha de inicio")
    end_date = fields.Date(string="Fecha de fin")
    status = fields.Selection([
        ('all', 'Todos'),
        ('new', 'Nuevo'),
        ('win','Ganada'),
        ('lost','Rechazada'),
        ('call_back','Volver a llamar'),
        ('untraceable','Ilocalizable'),
        ('not_answered','No contestado'),
    ], default='all',string="Estado")
    agent_id = fields.Many2one('res.users', string="Agente")
    report_file = fields.Binary(string='Archivo Excel')
    report_name = fields.Char("Nombre del archivo", default="reporte_llamadas.xlsx")

    def _generate_excel_file(self, form_data, call_history_data, start_date, end_date, agent=None, state=None):
        """Generar el archivo Excel con los datos de llamadas."""
        output = BytesIO()
        workbook = xlsxwriter.Workbook(output, {'in_memory': True})

        # Primer hoja para el total de formularios
        sheet = workbook.add_worksheet('Reporte Total Formularios')

        # Agregar encabezado para la primera tabla
        sheet.write(0, 0, 'Reporte de Formularios')
        if start_date and end_date:
            sheet.write(1, 0, f"Período: {start_date} - {end_date}")
        else:
            sheet.write(1, 0, "Período: Todos los formularios")

        # Total de formularios generados
        total_forms = len(form_data)
    
        # Encabezados de la primera fila (estados)
        sheet.write(3, 0, 'Total de formularios generados')
        sheet.write(3, 1, 'Nuevo')
        sheet.write(3, 2, 'Ganada')
        sheet.write(3, 3, 'Perdida')
        sheet.write(3, 4, 'Volver a llamar')
        sheet.write(3, 5, 'Ilocalizable')
        sheet.write(3, 6, 'No contestado')

        # Obtener el desglose de los formularios por estado
        status_counts = {
            'Nuevo': len(form_data.filtered(lambda r: r.state == 'new')),
            'Ganada': len(form_data.filtered(lambda r: r.state == 'win')),
            'Perdida': len(form_data.filtered(lambda r: r.state == 'lost')),
            'Volver a llamar': len(form_data.filtered(lambda r: r.state == 'call_back')),
            'Ilocalizable': len(form_data.filtered(lambda r: r.state == 'untraceable')),
            'No contestado': len(form_data.filtered(lambda r: r.state == 'not_answered')),
        }

        # Segunda fila: mostrar los totales
        sheet.write(4, 0, total_forms)
        sheet.write(4, 1, status_counts['Nuevo'])
        sheet.write(4, 2, status_counts['Ganada'])
        sheet.write(4, 3, status_counts['Perdida'])
        sheet.write(4, 4, status_counts['Volver a llamar'])
        sheet.write(4, 5, status_counts['Ilocalizable'])
        sheet.write(4, 6, status_counts['No contestado'])

        # Segunda hoja para el desglose por agentes
        sheet = workbook.add_worksheet('Reporte por Agente')

        # Encabezados para el desglose por agente
        sheet.write(0, 0, 'Nombre del Agente')
        sheet.write(0, 1, 'Nombre del Cliente')
        sheet.write(0, 2, 'Apellido del Cliente')
        sheet.write(0, 3, 'Cédula del Cliente')
        sheet.write(0, 4, 'Fecha del Formulario')
        sheet.write(0, 5, 'Estado de la Llamada')
        sheet.write(0, 6, 'Comentarios')

        # Filtrar por agente y estado
        if agent and state:
            agent_forms = form_data.filtered(lambda r: r.create_uid.id == agent.id and r.state == state)
        elif agent:
            agent_forms = form_data.filtered(lambda r: r.create_uid.id == agent.id)
        elif state:
            agent_forms = form_data.filtered(lambda r: r.state == state)
        else:
            agent_forms = form_data

        # Rellenar los datos de la tabla por agente
        row = 1
        for record in agent_forms:
            sheet.write(row, 0, record.create_uid.name)
            sheet.write(row, 1, record.first_name or '')
            sheet.write(row, 2, record.last_name or '')
            sheet.write(row, 3, record.document or '') 
            sheet.write(row, 4, record.closing_date.strftime('%Y-%m-%d') if record.closing_date else record.date_local.strftime('%Y-%m-%d %H:%M:%S'))
            sheet.write(row, 5, dict(record._fields['state'].selection).get(record.state, ''))
            total_comments = len(record.call_history_ids)
            last_comment = record.call_history_ids[-1].comment if total_comments > 0 else ''

            # Escribir el último comentario seguido del número total de comentarios entre paréntesis
            sheet.write(row, 6, f"{last_comment} ({total_comments})" if total_comments > 0 else 'Sin comentarios')
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
            agent_forms = form_data.filtered(lambda r: r.create_uid.id == agent.id)
            total_forms = len(agent_forms)

            if total_forms > 0:
                won_forms = len(agent_forms.filtered(lambda r: r.state == 'win'))
                lost_forms = len(agent_forms.filtered(lambda r: r.state == 'lost'))
                call_back_forms = len(agent_forms.filtered(lambda r: r.state == 'call_back'))
                untraceable_forms = len(agent_forms.filtered(lambda r: r.state == 'untraceable'))
                not_answered_forms = len(agent_forms.filtered(lambda r: r.state == 'not_answered'))

                # Calcular efectividad para cada estado
                effectiveness_won = (won_forms / total_forms * 100) if total_forms > 0 else 0
                effectiveness_lost = (lost_forms / total_forms * 100) if total_forms > 0 else 0
                effectiveness_call_back = (call_back_forms / total_forms * 100) if total_forms > 0 else 0
                effectiveness_untraceable = (untraceable_forms / total_forms * 100) if total_forms > 0 else 0
                effectiveness_not_answered = (not_answered_forms / total_forms * 100) if total_forms > 0 else 0
                effectiveness_total = (won_forms / total_forms * 100) if total_forms > 0 else 0

                # Escribir los datos en la fila correspondiente al agente
                sheet.write(row, col_estado_start + 0, agent.name)  # Nombre del agente
                sheet.write(row, col_estado_start + 1, f"{effectiveness_won:.2f}%")  # Efectividad Ganada
                sheet.write(row, col_estado_start + 2, f"{effectiveness_lost:.2f}%")  # Efectividad Perdida
                sheet.write(row, col_estado_start + 3, f"{effectiveness_call_back:.2f}%")  # Efectividad Volver a Llamar
                sheet.write(row, col_estado_start + 4, f"{effectiveness_untraceable:.2f}%")  # Efectividad Ilocalizable
                sheet.write(row, col_estado_start + 5, f"{effectiveness_not_answered:.2f}%")  # Efectividad No Contestado
                sheet.write(row, col_estado_start + 6, f"{effectiveness_total:.2f}%")  # Efectividad Total

                row += 1

        workbook.close()
        output.seek(0)
        return output.read()
    
    
    def generate_report(self):
        """Generar el reporte de Excel según los filtros aplicados."""
        # Buscar todos los formularios (no solo los del usuario actual)
        form_data = self.env['precisa_forms.form'].sudo().search([])
        call_history_data = self.env['call.history'].sudo().search([])
        state = ''

        # Filtrar por fechas si se seleccionaron
        if self.start_date and self.end_date:
        # Filtrar form_data usando closing_date si existe, de lo contrario usar date_local
            form_data = form_data.filtered(
                lambda r: self.start_date <= (r.closing_date or r.date_local.date()) <= self.end_date
            )

            # Filtrar call_history_data usando create_date
            call_history_data = call_history_data.filtered(
                lambda r: self.start_date <= r.create_date.date() <= self.end_date
            )


        if self.status != 'all':
            state = self.status
        # Generar el archivo Excel
        report_content = self._generate_excel_file(form_data, call_history_data, self.start_date, self.end_date, self.agent_id, state)

        # Guardar el archivo en binario
        self.report_file = base64.b64encode(report_content)

        return {
            'type': 'ir.actions.act_url',
            'url': f"/web/content/{self._name}/{self.id}/report_file/{self.report_name}",
            'target': 'self',
        }

