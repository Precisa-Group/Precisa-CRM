# -*- coding: utf-8 -*-

from datetime import timedelta
from odoo import models, fields, api
from odoo.exceptions import ValidationError
import re
import logging
from odoo.http import request
from odoo.exceptions import UserError
from dateutil.relativedelta import relativedelta
from pytz import timezone
from datetime import datetime

_logger = logging.getLogger(__name__)

class PrecisaForms(models.Model):
    _name = 'precisa_forms.form'
    _description = 'precisa_forms.precisa_forms'

    # STATUSBAR
    state = fields.Selection([
        ('new', 'Nuevo'),
        ('win','Ganada'),
        ('lost','Rechazada'),
        ('call_back','Volver a llamar'),
        ('untraceable','Ilocalizable'),
        ('not_answered','No contestado'),

    ], default='new',string="Estado")

    date_local = fields.Datetime(string="Fecha de Creación (Local)")
    closing_date = fields.Date(string="Fecha de cierre")

    lead_id = fields.Many2one('crm.lead', string='Related Lead')

    # INFORMACION GENERAL
    contact_id = fields.Many2one('res.partner', string="Contacto", required=True)
    first_name = fields.Char(string="Primer Nombre", required=True, compute="_compute_contact_info", store=True)
    second_name = fields.Char(string="Segundo Nombre")
    last_name = fields.Char(string="Primer Apellido", required=True, compute="_compute_contact_info", store=True)
    second_lastname = fields.Char(string="Segundo Apellido")
    
    marital_status = fields.Selection([
        ('single', 'Soltero/a'),
        ('married', 'Casado/a')
    ], string="Estado Civil")
    
    gender = fields.Selection([
        ('male', 'Masculino'),
        ('female', 'Femenino')
    ], string="Sexo", compute="_compute_contact_info", store=True)
    
    married_name = fields.Char(string="Apellido de Casada(o)", 
                               help="Solo necesario si está casado/a y usa un apellido marital.")
    
    residential_phone = fields.Char(string="Teléfono de Residencia", size=15, compute="_compute_contact_info", store=True, required=True)
    
    document = fields.Char(string="Cédula de Identidad", size=21, required=True, compute="_compute_contact_info", store=True)
    passport_document = fields.Char(string="Número de Pasaporte", size=21, compute="_compute_contact_info", store=True)
    
    
    birth_date = fields.Date(string="Fecha de Nacimiento", compute="_compute_contact_info", store=True)
    age = fields.Integer(string="Edad", compute="_compute_contact_info", store=True)

    call_history_ids = fields.One2many('call.history', 'form_id', string="Historial de llamadas")
    address_ids = fields.One2many('res.address', 'form_id', string='Direcciones', compute="_compute_contact_info", store=True)
    selected_address_id = fields.Many2one('res.address', string='Direccion', domain="[('id', 'in', address_ids)]", compute="_compute_contact_info", store=True)
    email_ids = fields.One2many('res.email', 'form_id', string='Emails', compute="_compute_contact_info", store=True)
    email = fields.Char(string="Correo Electrónico", compute="_compute_contact_info", store=True)
    selected_email_id = fields.Many2one('res.email', string="Correo Seleccionado", domain="[('id', 'in', email_ids)]", compute="_compute_contact_info", store=True)

    cellphone = fields.Char(string="Celular", size=15, compute="_compute_contact_info", store=True, required=True)
    postal = fields.Char(string="Apartado Postal", size=11, store=True)
    
    birth_place = fields.Char(string="Lugar de Nacimiento", compute="_compute_contact_info", store=True, required=True)
    
    country_id = fields.Many2one('res.country', string="País", compute="_compute_contact_info", store=True)
    state_id = fields.Many2one('res.country.state', string="Provincia/Estado", compute="_compute_contact_info", store=True)
    city = fields.Char(string="Ciudad", compute="_compute_contact_info", store=True)
    nationality = fields.Char( string="Nacionalidad")

    #INFORMACION ADICIONAL 1
    additional_name = fields.Char(string="Nombres")
    additional_lastname = fields.Char(string="Apellidos")
    additional_document = fields.Char(string="Cédula de Identidad")
    additional_nationality = fields.Char(string="Nacionalidad")
    additional_kinship = fields.Char(string="Parentesco")
    additional_birth_date = fields.Date(string="Fecha de Nacimiento")

    #INFORMACION ADICIONAL 2
    additional_name2 = fields.Char(string="Nombres")
    additional_lastname2 = fields.Char(string="Apellidos")
    additional_document2 = fields.Char(string="Cédula de Identidad")
    additional_nationality2 = fields.Char(string="Nacionalidad")
    additional_kinship2 = fields.Char(string="Parentesco")
    additional_birth_date2 = fields.Date(string="Fecha de Nacimiento")
    
    #INFORMACION DE RECIDENCIA
    address = fields.Char(string="Dirección de Residencia")
    building = fields.Char(string="Edificio")
    apartment = fields.Char(string="Apartamento")
    sector = fields.Char(string="Sector")
    
    residential_country_id = fields.Many2one('res.country', string="País de Residencia")
    residential_state_id = fields.Many2one('res.country.state', string="Provincia/Estado de Residencia")
    residential_city = fields.Char(string="Ciudad de Residencia")
    
    #APARTADO DE EMPLEO
    education_level = fields.Selection([
        ('none', 'Sin Educación Formal'),
        ('primary', 'Primaria'),
        ('secondary', 'Secundaria'),
        ('bachelor', 'Licenciatura'),
        ('master', 'Maestría'),
        ('phd', 'Doctorado')
    ], string="Nivel Educativo")
    
    job_occupation = fields.Char(string="Ocupación", compute="_compute_contact_info", store=True)
    profession = fields.Char(string="Profesión")
    economic_activity = fields.Char(string="Actividad Económica")
    
    # level_annual_income = fields.Monetary(string="Nivel de Ingreso Anual", currency_field='currency_id')
    monthly_salary = fields.Monetary(string="Salario Mensual", currency_field='currency_id')
    
    
    others_income = fields.Char(string="Otros Ingresos")
    
    currency_id = fields.Many2one('res.currency', string="Moneda", required=True, default=lambda self: self.env.company.currency_id)

    job_company = fields.Char(string="Empresa donde labora") 
    entry_date = fields.Date(string="Fecha de ingreso")
    job_economic_activity = fields.Char(string="Actividad economica de la empresa")
    job_email = fields.Char(string="Correo de la empresa")
    job_telephone = fields.Integer(string="Telefono de la empresa", size=15)
    job_cellphone = fields.Integer(string="Celular (Flota)", size=15)
    # job_fax = fields.Char(string="Fax")
    job_address = fields.Char(string="Dirección de la empresa")
    job_sector = fields.Char(string="Sector")
    job_country_id = fields.Many2one('res.country', string="País")
    job_city = fields.Char(string="Ciudad de Residencia")
    job_postal = fields.Integer(string="Apartado Postal", size=11)

    # INFORMACION SOBRE SOLICITUD
    request_type = fields.Selection([
        ('client_request', 'Solicitada por el cliente'),
        ('referred_business', 'Referida por ejecutivo de negocios')
    ], string="Tipo de solicitud")

    canal_type = fields.Selection([
        ('digital_canal', 'Canal digital'),
        ('external_canal', 'Canal externo'),
        ('telesales', 'Televentas'),
        ('internal_canal', 'Canal interno')
    ], string="Tipo de canal", require=True, default="external_canal")

    canal_name = fields.Char(string="Nombre del canal", default="Precisa Group")

    collaborator_relationship = fields.Char(string="Vinculacion con colaborador")
    referring_excutive = fields.Char(string="Ejecutivo que refiere", require=True, default=lambda self: self.env.user.name)

    suggested_product = fields.Char(string="Producto sugerido", require=True, compute="_compute_contact_info", store=True)
    suggested_limit = fields.Monetary(string="Limite sugerido", require=True, currency_field='currency_id', compute="_compute_contact_info", store=True)

    # PERSONAS EXPUESTA POLITICAMENTE

    politician_charge = fields.Boolean(string="Usted tiene o ha ocupado un cargo politico?")
    charge = fields.Char(string="Cargo")
    institution = fields.Char(string="Institucion")
    is_related = fields.Boolean(string="Usted tiene algun parentesco con alguna Persona Expuesta Politicamente (PEP)?")
    related_type = fields.Selection([
        ('father', 'Padre'),
        ('son', 'Hijos'),
        ('grandparents', 'Abuelos'),
        ('spouses', 'Conyugues'),
        ('parents_in_law', 'Suegros'),
        ('sons_in_law', 'Yernos'),
        ('daughters_in_law', 'Nueras'),
        ('other', 'Otro'),
    ], string="En caso de afirmativo indique:")

    related_name = fields.Char(string="Nombre")
    related_charge = fields.Char(string="Cargo")

    _sql_constraints = [
        ('cedula_unique', 'UNIQUE(document)', 'La cédula debe ser única.')
    ] 

    @api.constrains('document')
    def _check_document_unique(self):
        for record in self:
            if self.search_count([('document', '=', record.document)]) >= 1:
                raise ValidationError("Existe un formulario creado para este cliente")

    @api.onchange('state')  # Detecta cambio en el campo state
    def _onchange_state(self):
        if self.lead_id:
            stage = False  # Inicializa la variable stage
            
            if self.state == 'new':
                # Actualiza a la etapa correspondiente al estado 'new'
                stage = self.env.ref('crm.stage_lead1', raise_if_not_found=False)
            elif self.state == 'win':
                # Actualiza a la etapa correspondiente al estado 'win'
                stage = self.env.ref('crm.stage_lead2', raise_if_not_found=False)
            elif self.state == 'lost':
                # Actualiza a la etapa correspondiente al estado 'lost'
                stage = self.env.ref('crm.stage_lead3', raise_if_not_found=False)
            elif self.state == 'call_back':
                # Actualiza a la etapa correspondiente al estado 'call_back'
                stage = self.env.ref('crm.stage_lead4', raise_if_not_found=False)
            elif self.state == 'untraceable':
                # Actualiza a la etapa correspondiente al estado 'untraceable'
                stage = self.env.ref('crm.stage_lead5', raise_if_not_found=False)
            elif self.state == 'not_answered':
                # Actualiza a la etapa correspondiente al estado 'not_answered'
                stage = self.env.ref('crm.stage_lead6', raise_if_not_found=False)
            
            # Solo actualizar el campo stage_id si se encontró una etapa válida
            if stage:
                self.lead_id.stage_id = stage.id
            else:
                _logger.warning(f"No se encontró la etapa correspondiente para el estado {self.state}")
    

    # def actualizar_fecha_creacion_local(self):
    #     # Obtener la zona horaria de Santo Domingo
    #     tz = timezone('America/Santo_Domingo')

    #     # Buscar todos los registros existentes que aún no tienen la 'fecha_creacion_local' definida
    #     records_without_date_local = self.search([('date_local', '=', False)])

    #     for record in records_without_date_local:
    #         # Obtener el create_date (que está en UTC por defecto)
    #         if record.create_date:
    #             # Convertir create_date a la zona horaria local
    #             actual_date_utc = record.create_date
    #             actual_date_local = actual_date_utc.astimezone(tz)

    #             # Actualizar el campo 'fecha_creacion_local' con la fecha local
    #             record.write({
    #                 'date_local': actual_date_local.strftime('%Y-%m-%d %H:%M:%S')
    #             })

    #     return True

    @api.model
    def create(self, vals):

        tz = timezone('America/Santo_Domingo')
        # Obtener la fecha y hora actual en UTC y luego convertirla a la zona horaria local
        actual_date_utc = datetime.now()
        actual_date_local = actual_date_utc.astimezone(tz)
        # Asignar la fecha local al campo 'fecha_creacion_local'
        vals['date_local'] = actual_date_local.strftime('%Y-%m-%d %H:%M:%S')

        # self.actualizar_fecha_creacion_local()

        # Crear una oportunidad automáticamente al crear el formulario
        lead_vals = {}

        # Intentar buscar el contacto por contact_id
        contact = self.env['res.partner'].browse(vals.get('contact_id'))

        # Si no existe contact_id o el contacto no es encontrado, buscar por la cédula
        if not contact.exists():
            document = vals.get('document')  # Asegúrate de que 'document' se refiere a la cédula
            contact = self.env['res.partner'].search([('document', '=', document)], limit=1)

        stage_mapping = {
            'new': self.env.ref('crm.stage_lead1').id,   # Estado 'Nuevo'
            'win': self.env.ref('crm.stage_lead2').id,   # Estado 'Ganada'
            'lost': self.env.ref('crm.stage_lead3').id,  # Estado 'Rechazada'
            'call_back': self.env.ref('crm.stage_lead4').id,   # Estado 'Volver a llamar'
            'untraceable': self.env.ref('crm.stage_lead5').id, # Estado 'Ilocalizable'
            'not_answered': self.env.ref('crm.stage_lead6').id, # Estado 'No contestado'
        }

        # Obtener el estado proporcionado en vals o usar 'new' por defecto
        state = vals.get('state', 'new')

        # Asignar valores a lead_vals
        lead_vals = {
            'name': contact.name if contact else 'New Opportunity',  # Nombre del contacto o valor por defecto
            'partner_id': contact.id if contact else None,  # Asignar el partner_id si se encontró, de lo contrario None
            'stage_id': stage_mapping.get(state, self.env.ref('crm.stage_lead1').id),  # Etapa según el estado
        }

        # Crear la oportunidad en el CRM
        lead = self.env['crm.lead'].create(lead_vals)

        # Asignar el lead recién creado al formulario
        vals['lead_id'] = lead.id

        # Llamar al método original `create` para crear el formulario
        return super(PrecisaForms, self).create(vals)
    
    def write(self, vals):
        # Si el campo 'closing_date' está presente en los valores y no es nulo, usamos el valor proporcionado
        if 'closing_date' in vals and vals['closing_date']:
            vals['closing_date'] = vals['closing_date']
        # Si no se proporciona 'closing_date', no se actualiza, se deja como está (incluso si es null)

        return super(PrecisaForms, self).write(vals)
    
    #EMAIL VALIDATION
    @api.constrains('email')
    def _check_email_field(self):
        email_regex = r'^\b[A-Za-z1-9._%+-]+@[A-Za-z1-9.-]+\.[A-Z|a-z]{2,}\b'
        for record in self:
            if record.email and not re.match(email_regex, record.email):
                raise ValidationError("La dirección de email no es válida.")
            
    @api.onchange('canal_type')
    def _onchange_canal_type(self):
        # Esto limpia el nombre del canal cuando se cambia el tipo de canal
        if not self.canal_type:
            self.canal_name = False

    @api.model
    def default_get(self, fields_list):
        res = super(PrecisaForms, self).default_get(fields_list)
        
        contact_id = request.session.get('default_contact_id')
        # _logger.info('ID de contacto desde sesión: %s', contact_id)
        
        # Verificar y asignar el contact_id
        if contact_id:
            res.update({'contact_id': contact_id})
            # _logger.info('Valores predeterminados actualizados: %s', res)
        
        return res

    @api.onchange('contact_id', 'document')
    def _compute_contact_info(self):
        for record in self:

            if not record.contact_id and record.document:
                contact = self.env['res.partner'].search([('document', '=', record.document)], limit=1)
                if contact:
                    record.contact_id = contact.id

            if record.contact_id:

                first_name_parts = record.contact_id.first_name.split()
                record.first_name = first_name_parts[0] if len(first_name_parts) > 0 else ''
                record.second_name = first_name_parts[1] if len(first_name_parts) > 1 else ''

                # Split para separar los dos apellidos
                last_name_parts = record.contact_id.last_name.split()
                record.last_name = last_name_parts[0] if len(last_name_parts) > 0 else ''
                record.second_lastname = last_name_parts[1] if len(last_name_parts) > 1 else ''
                record.second_lastname = record.contact_id.second_lastname if record.contact_id.second_lastname else record.second_lastname
                record.first_name =  record.first_name
                record.last_name = record.last_name
                record.email_ids = record.contact_id.email_ids if record.contact_id.email_ids else record.email_ids
                record.selected_email_id = record.selected_email_id
                record.address_ids = record.contact_id.address_ids if record.contact_id.address_ids else record.address_ids
                record.selected_address_id = record.selected_address_id
                record.birth_date = record.contact_id.birth_date if record.contact_id.birth_date else record.birth_date
                record.birth_place = record.contact_id.birth_place if record.contact_id.birth_place else record.birth_place
                record.age = record.contact_id.age if record.contact_id.age else record.age
                # record.email = record.contact_id.email if record.contact_id.email else record.email
                record.suggested_product = record.contact_id.suggested_product if record.contact_id.suggested_product else record.suggested_product
                record.suggested_limit = record.contact_id.suggested_limit if record.contact_id.suggested_limit else record.suggested_limit
                record.residential_phone = record.contact_id.phone if record.contact_id.phone else record.residential_phone
                record.cellphone = record.contact_id.mobile if record.contact_id.mobile else record.cellphone
                record.document = record.contact_id.document if record.contact_id.document else record.document
                record.postal = record.contact_id.zip if record.contact_id.zip else record.postal
                record.job_occupation = record.contact_id.function if record.contact_id.function else record.job_occupation
                record.country_id = record.contact_id.country_id if record.contact_id.country_id else record.country_id
                record.state_id = record.contact_id.state_id if record.contact_id.state_id else record.state_id
                record.city = record.contact_id.city if record.contact_id.city else record.city
                record.gender = record.contact_id.gender if record.contact_id.gender else record.gender
                
                

            else:
                record.first_name = ''
                record.last_name = ''
                record.email = ''
                record.cellphone = ''
                record.document = ''
                record.postal = ''
                record.job_occupation = ''
                record.country_id = ''
                record.state_id = ''
                record.city = ''
                record.gender = ''
                record.residential_phone = ''
            
    #ACTUALIZAR DATOS
    @api.onchange('first_name', 'second_name', 'last_name', 'second_lastname',
                  'document', 'residential_phone', 'cellphone',
                  'postal', 'job_occupation', 'country_id', 
                  'state_id', 'city', 'gender')
    def _update_contact_info(self):
        for record in self:
            if record.contact_id:
                contact = record.contact_id
                full_name = f"{record.first_name} {record.second_name or ''} {record.last_name} {record.second_lastname or ''}".strip()
                contact.name = full_name
                contact.first_name = record.first_name
                contact.last_name = record.last_name
                contact.display_name = full_name
                contact.document = record.document
                contact.phone = record.residential_phone
                contact.mobile = record.cellphone
                contact.zip = record.postal
                contact.function = record.job_occupation
                contact.country_id = record.country_id
                contact.state_id = record.state_id
                contact.city = record.city
                contact.gender = record.gender

                for record in self:
                    if record.contact_id:
                        contact = record.contact_id
                        # Obtener todos los correos electrónicos actuales
                        existing_emails = self.env['res.email'].search([('partner_id', '=', contact.id)])
                        existing_address = self.env['res.address'].search([('partner_id', '=', contact.id)])
                        
                        # Crear un conjunto de los correos electrónicos que queremos mantener
                        new_email_set = {email_form.email for email_form in record.email_ids if email_form.email}
                
                    # Actualizar o crear nuevos correos electrónicos
                    for email_form in record.email_ids:
                        if email_form.email:
                            email_record = existing_emails.search([('email', '=', email_form.email)], limit=1)
                            if email_record:
                                email_record.write({'email': email_form.email})
                            else:
                                # Crear nuevo correo electrónico
                                self.env['res.email'].create({
                                    'partner_id': contact.id,
                                    'email': email_form.email
                                })
                    
                    # Eliminar correos electrónicos que no están en la nueva lista
                    for email_record in existing_emails:
                        if email_record.email not in new_email_set:
                            email_record.unlink()

                    for address_form in record.address_ids:
                        if address_form.address:
                            # Si el address ya existe, lo actualizamos, si no lo creamos
                            address_record = existing_address.search([('address', '=', address_form.address)], limit=1)
                            # address_record = self.env['res.address'].search([('partner_id', '=', contact.id), ('address', '=', address_form.address)])
                            if address_record:
                                address_record.write({'address': address_form.address})
                            else:
                                # Creación del correo electrónico asegurando que 'partner_id' no sea null
                                self.env['res.address'].create({
                                    'partner_id': contact.id,  # Asegúrate de que contact.id está asignado
                                    'address': address_form.address
                                })
                

    # @api.model
    # def create(self, vals):
    #     # Crear un registro del wizard cuando se crea un registro de este modelo
    #     res = super(PrecisaForms, self).create(vals)
    #     return res

    # def action_open_wizard(self):
    #     return {
    #         'name': 'My Wizard',
    #         'type': 'ir.actions.act_window',
    #         'res_model': 'precisa_forms.my.wizard',
    #         'view_mode': 'form',
    #         'view_id': self.env.ref('precisa_forms.view_my_wizard_form').id,
    #         'target': 'new',
    #     }
                



