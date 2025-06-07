import os
import unittest
from unittest.mock import MagicMock, patch

# Ensure LangChain does not require a real API key during import
os.environ.setdefault("OPENAI_API_KEY", "test")

from chopperfix.chopper_decorators import chopperdoc

class FakePage:
    def __init__(self):
        self.url = 'http://example.com'
        self._html = "<html><div id='a'></div></html>"
    def content(self):
        return self._html

class FakeDriver:
    def __init__(self):
        self.page = FakePage()

calls = []

@chopperdoc
def action(driver, action, **kwargs):
    calls.append(kwargs.get('xpath'))
    if kwargs.get('xpath') == '//bad':
        raise Exception('fail')
    return 'ok'

class ChopperDecoratorTest(unittest.TestCase):
    def setUp(self):
        calls.clear()
        self.driver = FakeDriver()

    @patch('chopperfix.chopper_decorators.pattern_storage')
    @patch('chopperfix.chopper_decorators.adalFlow_Manger')
    def test_self_healing_flow(self, mock_manager, mock_storage):
        mock_storage.get_replacement_selector.return_value = '//fixed'
        mock_storage.save_pattern = MagicMock()
        mock_manager.generate_description.return_value = 'desc'
        mock_manager.suggest_alternative_selector.return_value = None

        result = action(self.driver, 'click', xpath='//bad')

        self.assertEqual(result, 'ok')
        self.assertEqual(calls, ['//bad', '//fixed'])
        mock_storage.get_replacement_selector.assert_called_once_with('//bad', 'http://example.com', 'click')
        self.assertEqual(mock_storage.save_pattern.call_count, 2)
        first_call = mock_storage.save_pattern.call_args_list[0]
        self.assertFalse(first_call.kwargs['success'])
        self.assertEqual(first_call.kwargs['replacement_selector'], '//fixed')
        second_call = mock_storage.save_pattern.call_args_list[1]
        self.assertTrue(second_call.kwargs['success'])
        self.assertEqual(second_call.args[1], '//fixed')

if __name__ == '__main__':
    unittest.main()
