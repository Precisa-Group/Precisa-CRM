from odoo import models, fields, api
from odoo.exceptions import UserError

class ResPartner (models.Model):
    _inherit = 'res.partner'

    phone_2 = fields.Char(string="Telefono 2")
    phone_3 = fields.Char(string="Telefono 3")
    phone_4 = fields.Char(string="Telefono 4")
    phone_5 = fields.Char(string="Telefono 5")
    phone_6 = fields.Char(string="Telefono 6")
    mobile_2 = fields.Char(string="Celular 2")
    mobile_3 = fields.Char(string="Celular 3")
    mobile_4 = fields.Char(string="Celular 4")
    mobile_5 = fields.Char(string="Celular 5")
    mobile_6 = fields.Char(string="Celular 6")
    Reason_not_applicable = fields.Char(string="Razon no aplicable")
    propose_limit_rd = fields.Monetary(string="Limite propuesto en RD", currency_field='currency_id')
    propose_limit_us = fields.Char(string="Limite propuesto en US")
    tc_propouse = fields.Char(string="TC propuesto")

    currency_id = fields.Many2one('res.currency', string="Moneda", default=lambda self: self.env.company.currency_id)

    rd_amount_income_less_than_60m = fields.Monetary(string="Ingresos menores a 60m RD", currency_field='currency_id')
    tc_amount_income_less_than_60m = fields.Char(string="TC para ingresos menores de 60m")
    rd_amount_income_less_than_20m = fields.Monetary(string="Ingresos menores a 20m RD", currency_field='currency_id')
    tc_amount_income_less_than_20m = fields.Char(string="TC para ingresos menores de 20m")
    campaing_month = fields.Char(string="Mes de la campaña")
    document = fields.Char()
    first_name = fields.Char()
    last_name = fields.Char()
    is_gestioned = fields.Boolean(string="fue gestionado", compute="_compute_has_form", store=True)
    form_id = fields.Many2one('banreservas.forms', string="Formulario asociado")

    @api.depends('form_id')
    def _compute_has_form(self):
        for partner in self:
            partner.is_gestioned = bool(partner.form_id)

    def _update_form_status(self):
        """
        Actualiza el estado del formulario para el cliente:
        - Si existe un formulario asociado, lo asigna al campo `form_id`.
        - Si no existe, limpia el campo `form_id` y desmarca `has_form`.
        """
        form = self.env['banreservas.forms'].search([('partner_id', '=', self.id)], limit=1)
        self.form_id = form.id if form else False

    def redirect_to_form(self):
        """
        Redirige al formulario Banreservas, pasando la cédula como parámetro en la URL.
        """
        for record in self:
            # Asegúrate de que el campo 'document' contiene la cédula
            cedula = record.document or ''  # Reemplaza 'document' por el nombre correcto del campo en tu modelo
            url = f'/web/formulario-banreservas/cargar?cedula={cedula}'
            
            return {
                'type': 'ir.actions.act_url',
                'url': url,
                'target': 'self',  # Cambia a 'new' si quieres abrir en una nueva pestaña
            }
        
    def view_form(self):
        """
        Redirige al formulario asociado al cliente actual si existe.
        """
        self.ensure_one()
        # Buscar el formulario asociado al cliente
        form = self.env['banreservas.forms'].search([('partner_id', '=', self.id)], limit=1)

        if not form:
            raise UserError("No existe un formulario asociado a este cliente.")

        # Redirigir al formulario encontrado
        return {
            'type': 'ir.actions.act_window',
            'name': 'Formulario',
            'view_mode': 'form',
            'res_model': 'banreservas.forms',
            'res_id': form.id,
            'target': 'current',
        }


