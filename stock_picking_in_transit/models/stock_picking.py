from odoo import _, api, fields, models
from odoo.exceptions import UserError
from odoo.tools.float_utils import float_compare, float_is_zero, float_round

class stockPickingTransit(models.Model):
    _inherit = 'stock.picking'

    state = fields.Selection(selection_add=[('in_transit', "Transit")])
    in_transit = fields.Boolean('In Transit')
    show_transit = fields.Boolean(compute = '_compute_show_validate')
    show_transit_redo = fields.Boolean(compute = '_compute_show_validate')

    @api.depends('move_type', 'immediate_transfer', 'move_lines.state', 'move_lines.picking_id')
    def _compute_state(self):
        #We let Odoo handle the complex logic for us first :)
        super(stockPickingTransit,self)._compute_state()

        pickings = self.filtered(lambda picking: picking.state not in ['cancel', 'done','draft'])
        for picking in pickings:
            if picking.in_transit:
                picking.state = 'in_transit'
                picking.in_transit = True

    def action_transit(self):
        for pick in self:
            pick.state = 'in_transit'
            pick.in_transit = True
    
    def action_transit_redo(self):
        for pick in self:
            pick.state = 'waiting'
            pick.in_transit = False
            pick._compute_state()

    @api.depends('state')
    def _compute_show_validate(self):
        for picking in self:

            picking.show_transit_redo = picking.state == 'in_transit'
            picking.show_transit = False

            if not (picking.immediate_transfer) and picking.state == 'draft':
                picking.show_validate = False
            elif picking.picking_type_id.code == 'outgoing' and picking.state != 'in_transit':
                picking.show_validate = False

                if picking.state in ('waiting','confirmed', 'assigned'):
                    picking.show_transit = True

            elif picking.state not in ('draft', 'waiting', 'confirmed', 'assigned', 'in_transit'):
                picking.show_validate = False
            else:
                picking.show_validate = True

    @api.depends('immediate_transfer', 'state')
    def _compute_show_check_availability(self):
        """ According to `picking.show_check_availability`, the "check availability" button will be
        displayed in the form view of a picking.
        """
        for picking in self:
            
            if picking.state == 'in_transit':
                picking.show_check_availability = False
                continue
           
            if picking.immediate_transfer or picking.state not in ('confirmed', 'waiting', 'assigned'):
                picking.show_check_availability = False
                continue
            picking.show_check_availability = any(
                move.state in ('waiting', 'confirmed', 'partially_available') and
                float_compare(move.product_uom_qty, 0, precision_rounding=move.product_uom.rounding)
                for move in picking.move_lines
            )