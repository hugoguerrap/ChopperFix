import unittest
from unittest.mock import patch

from llm_integration.langchain_manager import LangChainManager


class LangChainManagerTest(unittest.TestCase):
    @patch("llm_integration.langchain_manager.ChatOpenAI")
    def test_suggest_alternative_selector(self, mock_chat):
        mock_chat.return_value.predict.return_value = "//input[@id='searchInput']"
        manager = LangChainManager()
        result = manager.suggest_alternative_selector("<input id='q'>", "//input[@id='x']", "type")
        self.assertEqual(result, "//input[@id=\"searchInput\"]")
        self.assertTrue(result)

    @patch("llm_integration.langchain_manager.ChatOpenAI")
    def test_generate_description(self, mock_chat):
        mock_chat.return_value.predict.return_value = "Fill search field"
        manager = LangChainManager()
        desc = manager.generate_description("type", "//input", "http://t", "<html></html>")
        self.assertEqual(desc, "Fill search field")
        self.assertTrue(desc)

    @patch("llm_integration.langchain_manager.ChatOpenAI")
    def test_analyze_context_from_text(self, mock_chat):
        mock_chat.return_value.predict.return_value = "//div[@id='best']"
        manager = LangChainManager()
        result = manager.analyze_context_from_text("data", "//div[@id='old']", "click")
        self.assertEqual(result, "//div[@id=best]")
        self.assertTrue(result)


if __name__ == "__main__":
    unittest.main()
