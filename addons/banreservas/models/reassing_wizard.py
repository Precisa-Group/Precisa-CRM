
from odoo import fields, models, api
from odoo.exceptions import UserError

class ReassignCustomersWizard(models.TransientModel):
    _name = 'reassign.customers.wizard'
    _description = 'Asistente para reasignar clientes'

    partner_ids = fields.Many2many('res.partner', string="Clientes", domain="[('campaign', '=', 'banreservas')]")
    new_user_id = fields.Many2one('res.users', string="Nuevo Agente", required=True)

    def reassign_customers(self):
        if not self.env.user.has_group('banreservas.group_edit_propose_limit'):
            raise UserError("Solo los administradores pueden reasignar clientes.")
        
        for partner in self.partner_ids:
            
            partner.user_id = self.new_user_id
            # raise UserError(f"Cliente {partner.name} ha sido reasignado de {partner.user_id.name} a {self.new_user_id.name}.")
