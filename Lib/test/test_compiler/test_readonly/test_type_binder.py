from .common import ReadonlyTestBase


class TypeBinderTest(ReadonlyTestBase):
    def test_readonly_redeclare_0(self) -> None:
        code = """
        def f():
            x = 1
            x: Readonly[int] = 2
        """
        errors = self.lint(code)
        errors.check(
            errors.match("cannot re-declare the readonliness of 'x'"),
        )

    def test_readonly_redeclare_1(self) -> None:
        code = """
        def f():
            x: Readonly[int] = 1
            x: int = 2
        """
        errors = self.lint(code)
        errors.check(
            errors.match("cannot re-declare the readonliness of 'x'"),
        )

    def test_readonly_wrapper(self) -> None:
        # Might be confusing. The number 2 is narrowed to
        # readonly because `x` is declared readonly
        code = """
        def f():
            x = readonly([])
            x = 2
        """
        errors = self.lint(code)
        self.assertEqual(errors.errors, [])

    def test_readonly_wrapper_redeclare(self) -> None:
        # x is redeclared
        code = """
        def f():
            x = readonly([])
            x: int = 2
        """
        errors = self.lint(code)
        errors.check(
            errors.match("cannot re-declare the readonliness of 'x'"),
        )

    def test_readonly_assign(self) -> None:
        code = """
        def f():
            x: Readonly[int] = 1
            x = 2
        """
        errors = self.lint(code)
        self.assertEqual(errors.errors, [])

    def test_readonly_augassign(self) -> None:
        code = """
        def f():
            l: Readonly[List[int]] = []
            l += [1]
        """
        errors = self.lint(code)
        errors.check(
            errors.match(
                "Cannot modify readonly reference 'l' via aug assign",
            ),
        )

    def test_call_readonly(self) -> None:
        code = """
        def f():
            x: Readonly[int] = 1
            f(x, 1 ,2)
        """
        errors = self.lint(code)
        self.assertEqual(errors.errors, [])

    def test_call_readonly_kw(self) -> None:
        code = """
        def f():
            x: Readonly[int] = 1
            f(x, 1 ,2, y=1)
        """
        errors = self.lint(code)
        errors.check(
            errors.match(
                "Unsupported: cannot use keyword args or"
                " star args when ANY argument is readonly"
            ),
        )

    def test_call_readonly_star_args(self) -> None:
        code = """
        def f():
            x: Readonly[List[int]] = [1, 2]
            f(1 ,2, *x)
        """
        errors = self.lint(code)
        errors.check(
            errors.match(
                "Unsupported: cannot use keyword args or"
                " star args when ANY argument is readonly"
            ),
        )

    def test_readonly_class_var(self) -> None:
        code = """
        class C:
            x: Readonly[int] = 1
        """
        errors = self.lint(code)
        errors.check(
            errors.match("cannot declare 'x' readonly in class/module"),
        )

    def test_readonly_base_class(self) -> None:
        code = """
        def f():
            C: Readonly[object]
            class D(C):
                ...
        """
        errors = self.lint(code)
        errors.check(
            errors.match("cannot inherit from a readonly base class 'C'"),
        )

    def test_readonly_func_global(self) -> None:
        code = """
        x = 1
        @readonly_func
        def f():
            x += 1
        """
        errors = self.lint(code)
        self.assertEqual(errors.errors, [])

    def test_readonly_func_closure(self) -> None:
        code = """
        def g():
            x = 1
            @readonly_func
            def f():
                nonlocal x
                x += 1
        """
        errors = self.lint(code)
        errors.check(
            errors.match(
                "Cannot modify readonly reference 'x' via aug assign",
            ),
            errors.match(
                "cannot modify 'x' from a closure, inside a readonly_func annotated function"
            ),
        )

    def test_readonly_func_closure_1(self) -> None:
        code = """
        def g():
            x = 1
            @readonly_func
            def f():
                nonlocal x
                x = 2
        """
        errors = self.lint(code)
        errors.check(
            errors.match(
                "cannot modify 'x' from a closure, inside a readonly_func annotated function"
            ),
        )

    def test_readonly_in_method(self) -> None:
        code = """
        class C:
            def f(self, x: Readonly[List[int]]):
                x += [1]
        """
        errors = self.lint(code)
        errors.check(
            errors.match(
                "Cannot modify readonly reference 'x' via aug assign",
            ),
        )
