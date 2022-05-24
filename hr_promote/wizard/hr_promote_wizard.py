import logging
import urllib
import re

from odoo import models, fields, api, _
from odoo.exceptions import ValidationError
from odoo.http import request
from odoo.tools.misc import formatLang

_logger = logging.getLogger(__name__)


class SendWhatsappPurchase(models.TransientModel):
    _name = 'hr.promote.signature'
    _description = 'Promote Hr Signature'

    user_id = fields.Many2one('res.users', readonly=True)
    promote_id = fields.Many2one('hr.promotion')
    signature = fields.Image(string="Signature", copy=False,
                             attachment=True, max_width=1024, max_height=1024, required=True)

    def action_confirm(self):
        self.promote_id.write({
            'hr_staff_signature': self.signature,
        })
        self.promote_id._action_validate()
