import json
import urllib.parse
from odoo import http
from odoo.http import request
import logging
from odoo.exceptions import UserError

_logger = logging.getLogger(__name__)

class ContactFormBanController(http.Controller):
    
    @http.route(['/web/formulario-banreservas/cargar'], type='http', auth="user", website=True)
    def cargar_formulario(self, **kw):
        cedula = kw.get('cedula')
        validacion = False
        
        if cedula:
            contact = request.env['res.partner'].sudo().search([('document', '=', cedula), 
                        ('campaign', '=', 'banreservas')], limit=1)
            
            if contact:
                # Crear el contexto como un JSON válido
                context = json.dumps({'default_contact_id': contact.id})
                
                
                # Codificar el contexto para la URL
                if contact:
                # Guardar el contact_id en la sesión del usuario
                    request.session['default_contact_id'] = contact.id
                    # _logger.info(request.session['default_contact_id'])
                    
                    return request.redirect('/web#id=&cids=1&menu_id=133&action=352&model=banreservas.forms&view_type=form')
                
        
        return request.redirect('/web#id=&cids=1&menu_id=133&action=352&model=banreservas.forms&view_type=form')