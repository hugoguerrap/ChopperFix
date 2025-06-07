import unittest
from learning.pattern_storage import PatternStorage, Pattern

class PatternStorageTest(unittest.TestCase):
    def setUp(self):
        self.storage = PatternStorage('sqlite:///:memory:')

    def tearDown(self):
        self.storage.close()

    def test_save_pattern_insert_and_update(self):
        # Insert new pattern
        self.storage.save_pattern(
            'click',
            "//div[@id='a']",
            'http://example.com',
            'desc',
            success=True,
            full_element_html='<div id="a"></div>',
            parent_element='<body></body>',
            child_elements=['<span></span>'],
            sibling_elements=['<p></p>']
        )

        session = self.storage.session
        patterns = session.query(Pattern).all()
        self.assertEqual(len(patterns), 1)
        p = patterns[0]
        self.assertEqual(p.usage_count, 1)
        self.assertEqual(p.success_rate, 1.0)
        self.assertFalse(p.failed)
        self.assertEqual(p.full_element_html, '<div id="a"></div>')

        # Update existing pattern with failure
        self.storage.save_pattern(
            'click',
            "//div[@id='a']",
            'http://example.com',
            'fail desc',
            success=False,
            replacement_selector="//div[@id='b']"
        )
        updated = session.query(Pattern).first()
        self.assertEqual(updated.usage_count, 2)
        self.assertAlmostEqual(updated.success_rate, 0.5)
        self.assertTrue(updated.failed)
        self.assertEqual(updated.replacement_selector, "//div[@id='b']")

if __name__ == '__main__':
    unittest.main()
