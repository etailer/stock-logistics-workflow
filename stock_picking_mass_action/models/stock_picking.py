# Copyright 2014 Camptocamp SA - Guewen Baconnier
# Copyright 2018 Tecnativa - Vicent Cubells
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import _, api
from odoo.models import Model


class StockPicking(Model):
    _inherit = "stock.picking"

    @api.model
    def check_assign_all(self):
        """Try to assign confirmed pickings"""
        domain = [("picking_type_code", "=", "outgoing"), ("state", "=", "confirmed")]
        records = self.search(domain, order="scheduled_date")
        records.action_assign()

    def _log_activity_get_documents(
        self,
        orig_obj_changes,
        stream_field,
        stream,
        sorted_method=False,
        groupby_method=False,
    ):
        """Avoid error in method:
        env['stock.backorder.confirmation']._process(cancel_backorder=True)
        if mixing complete picking with partial picking and select cancel
        backorder
        """
        if not orig_obj_changes:
            return {}
        else:
            return super()._log_activity_get_documents(
                orig_obj_changes,
                stream_field,
                stream,
                sorted_method=sorted_method,
                groupby_method=groupby_method,
            )

    def action_immediate_transfer_wizard(self):
        view = self.env.ref("stock.view_immediate_transfer")
        wiz = self.env["stock.immediate.transfer"].create(
            {"pick_ids": [(4, p.id) for p in self]}
        )
        return {
            "name": _("Immediate Transfer?"),
            "type": "ir.actions.act_window",
            "view_mode": "form",
            "res_model": "stock.immediate.transfer",
            "views": [(view.id, "form")],
            "view_id": view.id,
            "target": "new",
            "res_id": wiz.id,
            "context": self.env.context,
        }