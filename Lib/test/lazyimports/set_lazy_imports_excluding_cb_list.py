import self
if self._lazy_imports:
    self.skipTest("Test relevant only when running with global lazy imports disabled")

import importlib

class Checker:
    def __contains__(self, name):
        return name in ["test.lazyimports.data.metasyntactic.bar"]

checker = Checker()
importlib.set_lazy_imports(checker)

from test.lazyimports.data.metasyntactic import foo
self.assertTrue(importlib.is_lazy_import(globals(), "foo"))  # should be lazy

from test.lazyimports.data.metasyntactic import bar
self.assertTrue(importlib.is_lazy_import(globals(), "bar"))  # should be eager

foo  # force loaded
self.assertFalse(importlib.is_lazy_import(globals(), "foo"))  # should be loaded