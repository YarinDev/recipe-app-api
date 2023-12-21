"""
Test custom Django management commands.
"""

from unittest.mock import patch


from psycopg2 import OperationalError as Psycopg2OpError

from django.core.management import call_command
from django.db.utils import OperationalError
from django.test import SimpleTestCase

#mocking this command noted inside patch
@patch('core.management.commands.wait_for_db.Command.check')
class CommandTests(SimpleTestCase):
    """Test commands"""
    
    
    def test_wait_for_db_ready(self, patched_check):
        """Test waiting for db if db is ready"""
    
        patched_check.return_value = True
        call_command('wait_for_db')
        patched_check.assert_called_once_with(databases=['default'])
    
    # raise exception instead of just returning true
    # keep on vars order
    @patch('time.sleep')
    def test_wait_for_db_delay(self, patched_sleep, patched_check):
        """
        Test waiting for db when getting operational error
        """
        # first 2 times for psycopg2 error, and after 3 times it's operational error.
        patched_check.side_effect = [Psycopg2OpError] * 2 + \
            [OperationalError] * 3 + [True]

        
        call_command('wait_for_db')
        # based on the expections before, no more and no less
        self.assertEqual(patched_check.call_count, 6)
        #checking for default db called
        patched_check.assert_called_with(databases=['default'])
        
        