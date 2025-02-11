from odoo import models, fields


class Pending_forms(models.Model):
    _name = 'pending.forms' 

    answering_machine = fields.Integer()
    busy = fields.Integer()
    no_answer = fields.Integer()
    audio_problems = fields.Integer()
    call_later = fields.Integer()
    date = fields.Date()