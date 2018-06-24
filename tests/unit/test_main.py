import unittest

from click.testing import CliRunner
from cv_origami.main import main
from cv_origami.constants import WELCOME_TEXT


class TestMain(unittest.TestCase):
    def test_main(self):
        runner = CliRunner()
        result = runner.invoke(main)
        self.assertEqual(result.exit_code, 0)
        self.assertEqual(result.output, WELCOME_TEXT + '\n')
