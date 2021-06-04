from odoo.tests import common
from odoo.exceptions import ValidationError
from datetime import date, timedelta


class TestHelpdeskTicket(common.SavepointCase):

    @classmethod
    def setUpClass(cls):
        super(TestHelpdeskTicket, cls).setUpClass()
        cls.user_admin = cls.env.ref('base.user_root')
        cls.company = cls.env.ref('base.main_company')
        cls.user = cls.env['res.users'].create({
            'name': 'Open',
            'login': 'user',
            'company_id': cls.company.id,
            'groups_id': [(4, cls.ref('helpdesk_mgmt.group_helpdesk_user'))]
        })

        cls.stage_open = cls.env.ref('helpdesk.ticket.stage')
        cls.stage_close = cls.env.ref('helpdesk.ticket.stage')

        cls.stage_open = cls.env['helpdesk.ticket.stage'].create({
            'name': 'Open',
            'closed': False,
        })
        cls.stage_close = cls.env['helpdesk.ticket.stage'].create({
            'name': 'Closed',
            'closed': True,
        })

    def test_helpdesk_ticket_closed_date(self):
        helpdesk = self.env['helpdesk.ticket']

        new_ticket_manager = helpdesk.create({
            'name': 'Test 1',
            'description': 'Ticket test manager',
            'stage_id': self.stage_open.id,
        })
        new_ticket_manager.stage_id = self.stage_close.id
        self.assertEqual(new_ticket_manager.closed_date_editable,
                         False,
                         'Helpdesk Ticket: When the stage of a ticket is '
                         'closed and you are a manager, the editable '
                         'closing date must be False.')

        new_ticket_manager.stage_id = self.stage_open.id
        self.assertEqual(new_ticket_manager.closed_date,
                         False,
                         'Helpdesk Ticket: When editing the stage '
                         'of a ticket already closed to an open stage, '
                         'the closed date must be False.')

        yesterday = date.today() - timedelta(days=1)
        with self.assertRaises(ValidationError,
                               msg='Helpdesk Ticket: When editing the closed '
                                   'date of a ticket with a date that is less '
                                   'than the creation date, an exception'
                                   'must be thrown.'):
            new_ticket_manager.closed_date = yesterday

        with self.assertRaises(ValidationError,
                               msg='Helpdesk Ticket: When editing the closed '
                                   'date of a ticket with no value, an '
                                   'exception must be thrown.'):
            new_ticket_manager.closed_date = False

        new_ticket_user = helpdesk.with_user(self.user).create({
            'name': 'Test 2',
            'description': 'Ticket test user',
            'stage_id': self.stage_open.id,
        })
        new_ticket_user.with_user(self.user).write({
            'stage_id': self.stage_close.id
        })
        self.assertEqual(new_ticket_user.closed_date_editable,
                         True,
                         'Helpdesk Ticket: When the stage of a ticket is '
                         'closed and you are not a manager, the editable '
                         'closing date must be True.')
