from odoo import fields, models, api
from io import BytesIO
import xlsxwriter
from datetime import datetime
import base64

class ReportWizardBanreservas(models.TransientModel):
    _name = 'report.wizard.banreservas'
    _description = 'Wizard para generación de reportes de gestiones'

    start_date = fields.Date(string="Desde")
    end_date = fields.Date(string="Hasta")
    agent_id = fields.Many2one('res.users', string="Agente")

    form_state_section = fields.Selection([
        ('sale', 'Venta'),
        ('not_instreted', 'No Interesado'),
        ('incomplete', 'Incompleto'),
        ('pending', 'Pendiente'),
        ('all', 'Todos')
    ], string="Estado de la Sección")
    

    form_state = fields.Selection([
        ('sale', 'Venta'),
        ('economic_issues', 'Problemas Económicos'),
        ('limit_increase', 'Ya Tiene El Producto, Desea Aumento Límite'),
        ('already_has_product', 'Ya Tiene El Producto'),
        ('too_many_credit_cards', 'Tiene Muchas Tarjetas De Crédito'),
        ('not_interested', 'No Interesado'),
        ('income_below_10000', 'No Aplica/Ingresos Menores De $10,000'),
        ('age_range_exceeded', 'No Aplica/Fuera De Rango De Edad'),
        ('wants_to_visit_office', 'No Interesado/Desea Pasar Por La Oficina'),
        ('dissatisfied', 'No Interesado/Disgustado Con La Institución'),
        ('not_applicable_unemployed', 'No Aplica/No Está Laborando'),
        ('less_than_6_months', 'No Aplica/Menos De 6 Meses Laborando'),
        ('foreigner', 'No Aplica/Extranjero'),
        ('cash_only', 'No Interesado/Se Maneja Con Efectivo'),
        ('not_interested_loan', 'No Interesado/Desea Préstamo'),
        ('wants_amount_info', 'No Interesado/Desea Saber Monto Para Que Aplica'),
        ('banreservas_employee', 'No Aplica/Empleado De Banreservas'),
        ('credit_recovery', 'Recuperación De Crédito'),
        ('disconnected', 'Colgó'),
        ('very_low_limits', 'Límites Muy Bajos'),
        ('wrong_phone', 'Teléfono Equivocado'),
        ('dont_call_the_client', 'No Llamar Al Cliente'),
        ('outside_country', 'Fuera Del País'),
        ('died', 'Fallecido'),
        ('answering_machine', 'Máquina Contestadora'),
        ('busy', 'Ocupado'),
        ('no_answer', 'No Contestan'),
        ('audio_problems', 'Problemas De Audio'),
        ('call_later', 'Llamar Luego'),
        ('not_service','Teléfono Fuera De Servicio'),
        ('not_residential_contact','No Aplica/No Posee Contacto Residencial'),
        ('all', 'Todos')
    ],string="Disposiciones")

    report_file = fields.Binary(string='Archivo Excel')
    report_name = fields.Char(default="Reporte de gestiones.xlsx")
    campaing_month = fields.Selection([
        ('C1OCT2024', 'C1OCT2024'),
        ('C1NOV2024', 'C1NOV2024'),
        ('C1DIC2024', 'C1DIC2024'),
        ('C1ENE2025','C1ENE2025'),
        ('all', 'Todos')
    ], string="Mes de la campaña")

    phone_numbers = fields.Boolean(string='Numeros telefonicos', default=False)

    def _generate_excel_file(self, form_data, start_date, end_date, agent=None, form_state_section=None, form_state=None, campaing=None, phone_numbers=None):
        """Generar el archivo Excel con los datos de llamadas."""
        output = BytesIO()
        workbook = xlsxwriter.Workbook(output, {'in_memory': True})

        # Primer hoja para el total de formularios
        sheet = workbook.add_worksheet('Reporte Total Formularios')

        header_format = workbook.add_format({
            'bold': True,
            'align': 'center',
            'valign': 'vcenter',
            'bg_color': '#00B0F0',
            'font_color': 'white',
            'border': 1
        })
        
        if phone_numbers == True:
            headers = [
                'Nombre del Cliente',
                'Apellido del cliente',
                'Cédula',
                'Telefono 1',
                'Telefono 2',
                'Telefono 3',
                'Celular 1',
                'Celular 2',
                'Celular 3',
                'Correo electronico',
                'Estado de la Sección',
                'Disposición',
                'Nombre del Agente',
                'Codigo vendedor',
                'Tipo de lead',
                'Fecha',
                'Marca de tarjeta',
                'Tipo de producto',
                'Nombres (Tarjeta adicional)',
                'Apellidos (Tarjeta adicional)',
                'Cedula (Tarjeta adicional)',
                'Parentesco',
                'Mes de la campaña',
                'Comentario'
            ]
        else:
            headers = [
                'Nombre del Cliente',
                'Apellido del cliente',
                'Cédula',
                'Telefono celular',
                'Correo electronico',
                'Estado de la Sección',
                'Disposición',
                'Nombre del Agente',
                'Codigo vendedor',
                'Tipo de lead',
                'Fecha',
                'Marca de tarjeta',
                'Tipo de producto',
                'Nombres (Tarjeta adicional)',
                'Apellidos (Tarjeta adicional)',
                'Cedula (Tarjeta adicional)',
                'Parentesco',
                'Mes de la campaña',
                'Comentario',
            ]
             
        sheet.insert_image("H2", "/mnt/extra-addons/banreservas/views/FullLogo_Transparent.png", {"x_scale": 0.08, "y_scale": 0.07})
        sheet.merge_range('A6:S6', 'Relación de Ventas Tarjetas de Crédito', header_format)
        sheet.write(3, 0, 'Reporte de Formularios')
        if start_date and end_date:
                sheet.write(4, 0, f"Período: {start_date} - {end_date}")
        elif start_date:
            sheet.write(4,0, f"Período: {start_date}")
        else:
                sheet.write(4, 0, "Período: Todos los formularios")


        # Escribir los encabezados
        for col, header in enumerate(headers):
            sheet.write(7, col, header)

        # Filtrar los datos según los parámetros
        filtered_data = form_data
        if agent:
            filtered_data = filtered_data.filtered(lambda r: r.agent_id.id == agent.id)
        if form_state_section and form_state_section != 'all':
            filtered_data = filtered_data.filtered(lambda r: r.form_state_section == form_state_section)
        if form_state and form_state != 'all':
            filtered_data = filtered_data.filtered(lambda r: r.state == form_state)
        if campaing:
            filtered_data = filtered_data.filtered(lambda r: r.partner_id.campaing_month == campaing)

        # Escribir los datos en las filas
        for row_idx, record in enumerate(filtered_data, start=8):
            sheet.write(row_idx, 0, record.names or '')  # Nombre del Cliente
            sheet.write(row_idx, 1, record.lastnames or '')  # Apellido
            sheet.write(row_idx, 2, record.document or '')  # Cédula

            if phone_numbers == True:
                sheet.write(row_idx, 3, record.partner_id.phone or '')
                sheet.write(row_idx, 4, record.partner_id.phone_2 or '') 
                sheet.write(row_idx, 5, record.partner_id.phone_3 or '') 
                sheet.write(row_idx, 6, record.partner_id.mobile or '') 
                sheet.write(row_idx, 7, record.partner_id.mobile_2 or '') 
                sheet.write(row_idx, 8, record.partner_id.mobile_3 or '') 
                sheet.write(row_idx, 9, record.email or '')  
                sheet.write(row_idx, 10, dict(record._fields['form_state_section'].selection).get(record.form_state_section, '') or '')  # Estado de la Sección
                sheet.write(row_idx, 11, dict(record._fields['form_state'].selection).get(record.form_state, '') or '')  # Disposición
                sheet.write(row_idx, 12, record.create_uid.name or '')  # Nombre del Agente
                sheet.write(row_idx, 13, record.create_uid.br_code or '')  # Nombre del Agente
                sheet.write(row_idx, 14, 'Pre-Aprobada')
                sheet.write(row_idx, 15, record.close_date.strftime('%Y-%m-%d') if record.close_date else '')  # Fecha
                sheet.write(row_idx, 16, 'MasterCard')  # Comentario
                sheet.write(row_idx, 17, record.tc_propouse or '')
                sheet.write(row_idx, 18, record.additional_card_name or '')
                sheet.write(row_idx, 19, record.additional_card_lastnames or '')
                sheet.write(row_idx, 20, record.additional_card_document or '')
                sheet.write(row_idx, 21, record.additional_card_kinship or '')
                sheet.write(row_idx, 22, record.partner_id.campaing_month or '')
                sheet.write(row_idx, 23, record.comment or '')
            else:
                sheet.write(row_idx, 3, record.cellphone or '')  
                sheet.write(row_idx, 4, record.email or '')  
                sheet.write(row_idx, 5, dict(record._fields['form_state_section'].selection).get(record.form_state_section, '') or '')  # Estado de la Sección
                sheet.write(row_idx, 6, dict(record._fields['form_state'].selection).get(record.form_state, '') or '')  # Disposición
                sheet.write(row_idx, 7, record.create_uid.name or '')  # Nombre del Agente
                sheet.write(row_idx, 8, record.create_uid.br_code or '')  # Nombre del Agente
                sheet.write(row_idx, 9, 'Pre-Aprovada')
                sheet.write(row_idx, 10, record.close_date.strftime('%Y-%m-%d') if record.close_date else '')  # Fecha
                sheet.write(row_idx, 11, 'MasterCard')  # Comentario
                sheet.write(row_idx, 12, record.tc_propouse or '')
                sheet.write(row_idx, 13, record.additional_card_names or '')
                sheet.write(row_idx, 14, record.additional_card_lastnames or '')
                sheet.write(row_idx, 15, record.additional_card_document or '')
                sheet.write(row_idx, 16, record.additional_card_kinship or '')
                sheet.write(row_idx, 17, record.partner_id.campaing_month or '')
                sheet.write(row_idx, 18, record.comment or '')

        # Cerrar el libro de trabajo
        workbook.close()
        output.seek(0)
        return output.read()

    def generate_report(self):
        """Generar el reporte de Excel según los filtros aplicados."""
        # Buscar todos los formularios (no solo los del usuario actual)
        form_data = self.env['banreservas.forms'].sudo().search([])
        campaing = ''

        # Filtrar por fechas si se seleccionaron
        if self.start_date:
        # Filtrar form_data usando closing_date si existe, de lo contrario usar date_local
            form_data = form_data.filtered(
                lambda r: self.start_date <= (r.close_date or r.create_date.date()) <= self.end_date
            )

        
        if self.form_state_section != 'all':
            form_state_section = self.form_state_section

        if self.form_state != 'all':
            form_state = self.form_state

        if self.campaing_month != 'all':
            campaing = self.campaing_month


        # Generar el archivo Excel
        report_content = self._generate_excel_file(form_data, self.start_date, self.end_date, self.agent_id, form_state_section, form_state, campaing, self.phone_numbers)

        # Guardar el archivo en binario
        self.report_file = base64.b64encode(report_content)

        return {
            'type': 'ir.actions.act_url',
            'url': f"/web/content/{self._name}/{self.id}/report_file/{self.report_name}",
            'target': 'self',
        }


   