from odoo import models, fields

class BanreservasStage(models.Model):
    _name = 'banreservas.stage'
    _description = 'Banreservas Stage'
    _order = 'sequence'

    name = fields.Char(required=True, string="Stage Name")
    sequence = fields.Integer(default=1, string="Sequence", help="Order of the stages")
    fold = fields.Boolean(string="Folded in Kanban View", help="Folded in the Kanban view if enabled")
    is_default = fields.Boolean(string="Default Stage", help="Set as default stage")

