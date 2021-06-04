# Copyright 2021 Solvos Consultoría Informática (<http://www.solvos.es>)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from odoo import models, api, _, fields
from odoo.exceptions import ValidationError


class HelpdeskTicket(models.Model):
    _inherit = "helpdesk.ticket"

    closed_date_editable = fields.Boolean(
        compute="_compute_closed_date_editable"
    )

    def _prepare_ref_create_date(self):
        # Prepared method for further inheritances
        return self.create_date

    def _compute_closed_date_editable(self):
        is_manager = self.env.user.has_group(
            'helpdesk_mgmt.group_helpdesk_manager'
        )
        for record in self:
            record.closed_date_editable = record.closed and is_manager

    @api.constrains('closed_date')
    def _constrains_closed_date(self):
        for record in self.filtered("closed"):
            if (not record.closed_date or
               record.closed_date <= record._prepare_ref_create_date()):
                raise ValidationError(_(
                    "Wrong value for Closed Date:"
                    " It cannot be before the create date or empty!"
                ))

    @api.constrains('stage_id')
    def _constrains_stage_id(self):
        for record in self.filtered(lambda x: x.closed_date and not x.closed):
            record.closed_date = False
