# -*- encoding: utf-8 -*-
##############################################################################
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as published
#    by the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see http://www.gnu.org/licenses/.
#
##############################################################################
from openerp import api
from openerp import models, fields, _
from openerp.exceptions import except_orm


class ProductProductType(models.Model):
    _name = 'sale.order.type'

    name = fields.Char(string='Order Type', translate=True)
    is_show_to_menu = fields.Boolean(string=_('Show to menu'),default=False)

    menu_id = fields.Many2one('ir.ui.menu', readonly=True)
    action_id = fields.Many2one('ir.actions.act_window', readonly=True)
    parent_menu_id = fields.Many2one('sale.order.type')

    @api.model
    def create(self, vals):
        model = super(ProductProductType, self).create(vals)
        if vals.get('is_show_to_menu'):  # 去除name，防止自动seq失效
            self.menu_create(vals.get('name'), model)
        return model

    @api.one
    def write(self, vals):
        if vals.get('is_show_to_menu'):
            self.menu_create(self.name, self)
        else:
            self.unlink_menu(self.menu_id, self.action_id)
        return super(ProductProductType, self).write(vals)

    @api.one
    def unlink(self):
        self.unlink_menu(self.menu_id, self.action_id)
        return super(ProductProductType, self).unlink()


    def menu_create(self, name, order_type):
        model = 'sale.order'
        view_id = self.env.ref('sale.view_order_tree').id
        val = {
            'name': name,
            'res_model': model,
            'view_type': 'form',
            'view_mode': 'tree,form,kanban',
            'domain': '[["order_type", "=", %d]]' % int(order_type.id),
             'context': '{"default_order_type":%d, "search_default_user_id":uid}' % int(order_type.id),
            'view_id': view_id,
            # 'help': u'<p class="oe_view_nocontent_create">Create an order type and show to the menu </p>'
        }

        action_id = self.env['ir.actions.act_window'].create(val)
        order_type.action_id = action_id

        if len(self.env['ir.ui.menu'].search([('name','=',name)]))>=1:
            raise except_orm(_('Error!'), _('此产品菜单已经创建'))

        if order_type.parent_menu_id is None:
            parent_id = self.env.ref('sale.menu_sale_order')
        else:
            parent_id = order_type.parent_menu_id.menu_id
        order_type.menu_id = self.env['ir.ui.menu'].create({
            'name': name,
            'parent_id': parent_id.id,
            'action': 'ir.actions.act_window,%d' % (action_id.id)
        })

    def unlink_menu(self, menu_id, action_id):
        if menu_id.id is False or action_id.id is False:
            return
        action_window = self.env['ir.actions.act_window'].search([('view_id', '=', action_id.id)])
        action_window.unlink()
        menu = self.env['ir.ui.menu'].search([('id', '=', menu_id.id)])
        menu.unlink()


class sale_order(models.Model):
    _inherit = 'sale.order'

    order_type = fields.Many2one(comodel_name='sale.order.type',
                                   string='Order Type', required=True)

    pi_number = fields.Char(string='PI Number')

    delivery_date = fields.Date(string='交货日期')

