import unittest

from PersonalizedLinks import redirected_link, remove_query_string, get_body


class PersonalizedLinksTestCase(unittest.TestCase):
    def test_redirect(self):
        urls = [{"original": "http://instagram.com", "final": "https://www.instagram.com/"},
                {"original": "https://www.instagram.com/", "final": "https://www.instagram.com/"},
                {"original": "http://google.com", "final": "https://www.google.com/?gws_rd=ssl"}]

        for url in urls:
            self.assertEqual(redirected_link(url["original"]), url["final"])

    def test_remove_query_string(self):
        urls = [{"original": "http://example.com/?a=text&q2=text2&q3=text3&q2=text4", "final": "http://example.com/"},
                {"original": "http://example.com/", "final": "http://example.com/"}]

        for url in urls:
            self.assertEqual(remove_query_string(url["original"]), url["final"])

    def test_get_body(self):
        url = "https://www.instagram.com/"
        body = get_body(url)
        self.assertTrue(len(body) > 0)

        url = "https://www.instagram.com/idontexistksdfjkldafs"
        try:
            body = get_body(url)
            self.assertTrue(False)
        except Exception as e:
            pass


if __name__ == '__main__':
    unittest.main()
