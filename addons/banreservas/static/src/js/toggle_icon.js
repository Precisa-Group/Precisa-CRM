odoo.define('banreservas.toggle_icon', function (require) {
    'use strict';
    console.log('paso 1')
    var core = require('web.core');
    var Widget = require('web.Widget');
    console.log('paso 2', core)

    var ToggleIcon = Widget.extend({
        events: {
            'click .toggle-icon-btn': '_onToggleIcon',
        },
        
        _onToggleIcon: function (ev) {
            ev.preventDefault();
            var $btn = $(ev.currentTarget);
            var $icon = $btn.find('i');
            console.log('paso 3')
            if ($icon.hasClass('fa-times')) {
                $icon.removeClass('fa-times').addClass('fa-check');
            } else {
                $icon.removeClass('fa-check').addClass('fa-times');
            }
        },
    });

    core.action_registry.add('toggle_icon', ToggleIcon);
});
