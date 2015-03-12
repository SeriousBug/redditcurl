import os
import doctest
from tests import test_base


class TestDocs(test_base.EnterTemp):
    def test_readme(self):
        # Create the directory structure shown in the example
        os.mkdir("images/")
        doctest.testfile("../Readme.rst")
        self.assertTrue(os.path.isfile("images/funny_picture.gif"))
