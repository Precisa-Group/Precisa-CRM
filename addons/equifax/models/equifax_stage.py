from odoo import models, fields

class EquifaxStage(models.Model):
    _name = 'equifax.stage'
    _description = 'Equifax Stage'
    _order = 'sequence'

    name = fields.Char(required=True, string="Stage Name")
    sequence = fields.Integer(default=1, string="Sequence", help="Order of the stages")
    fold = fields.Boolean(string="Folded in Kanban View", help="Folded in the Kanban view if enabled")
    is_default = fields.Boolean(string="Default Stage", help="Set as default stage")
