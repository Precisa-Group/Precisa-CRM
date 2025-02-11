import json
import urllib.parse
from odoo import http
from odoo.http import request
import logging
from odoo.exceptions import UserError

_logger = logging.getLogger(__name__)

class ContactFormController(http.Controller):
    
    @http.route(['/web/formulario/cargar'], type='http', auth="user", website=True)
    def cargar_formulario(self, **kw):
        cedula = kw.get('email')
        validacion = False
        
        if cedula:
            contact = request.env['res.partner'].sudo().search([('document', '=', cedula)], limit=1)
            
            if contact:
                # Crear el contexto como un JSON válido
                context = json.dumps({'default_contact_id': contact.id})
                
                
                # Codificar el contexto para la URL
                if contact:
                # Guardar el contact_id en la sesión del usuario
                    request.session['default_contact_id'] = contact.id
                    # _logger.info(request.session['default_contact_id'])
                    
                    return request.redirect('/web#cids=1&action=210&model=precisa_forms.form&view_type=form&menu_id=133')
                
        
        return request.redirect('/web#cids=1&action=210&model=precisa_forms.form&view_type=form&menu_id=133')
# -*- coding: utf-8 -*-
# from odoo import http


# class PrecisaForms(http.Controller):
#     @http.route('/precisa_forms/precisa_forms', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/precisa_forms/precisa_forms/objects', auth='public')
#     def list(self, **kw):
#         return http.request.render('precisa_forms.listing', {
#             'root': '/precisa_forms/precisa_forms',
#             'objects': http.request.env['precisa_forms.precisa_forms'].search([]),
#         })

#     @http.route('/precisa_forms/precisa_forms/objects/<model("precisa_forms.precisa_forms"):obj>', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('precisa_forms.object', {
#             'object': obj
#         })
