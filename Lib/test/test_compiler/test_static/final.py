from compiler.errors import TypedSyntaxError

from .common import StaticTestBase


class FinalTests(StaticTestBase):
    def test_final_multiple_typeargs(self):
        codestr = """
        from typing import Final
        from something import hello

        x: Final[int, str] = hello()
        """
        with self.assertRaisesRegex(
            TypedSyntaxError,
            r"incorrect number of generic arguments for Final\[T\], expected 1, got 2",
        ):
            self.compile(codestr, modname="foo")

    def test_final_annotation_nesting(self):
        with self.assertRaisesRegex(
            TypedSyntaxError, "Final annotation is only valid in initial declaration"
        ):
            self.compile(
                """
                from typing import Final, List

                x: List[Final[str]] = []
                """,
                modname="foo",
            )

        with self.assertRaisesRegex(
            TypedSyntaxError, "Final annotation is only valid in initial declaration"
        ):
            self.compile(
                """
                from typing import Final, List
                x: List[int | Final] = []
                """,
                modname="foo",
            )

    def test_final(self):
        codestr = """
        from typing import Final

        x: Final[int] = 0xdeadbeef
        """
        self.compile(codestr, modname="foo")

    def test_final_generic(self):
        codestr = """
        from typing import Final

        x: Final[int] = 0xdeadbeef
        """
        self.compile(codestr, modname="foo")

    def test_final_generic_types(self):
        codestr = """
        from typing import Final

        def g(i: int) -> int:
            return i

        def f() -> int:
            x: Final[int] = 0xdeadbeef
            return g(x)
        """
        self.compile(codestr, modname="foo")

    def test_final_uninitialized(self):
        codestr = """
        from typing import Final

        x: Final[int]
        """
        with self.assertRaisesRegex(
            TypedSyntaxError, "Must assign a value when declaring a Final"
        ):
            self.compile(codestr, modname="foo")

    def test_final_reassign(self):
        codestr = """
        from typing import Any, Final

        x: Final[Any] = 0xdeadbeef
        x = "something"
        """
        with self.assertRaisesRegex(
            TypedSyntaxError, "Cannot assign to a Final variable"
        ):
            self.compile(codestr, modname="foo")

    def test_final_reassign_explicit_global(self):
        codestr = """
            from typing import Final

            a: Final[int] = 1337

            def fn():
                def fn2():
                    global a
                    a = 0
        """
        with self.assertRaisesRegex(
            TypedSyntaxError, "Cannot assign to a Final variable"
        ):
            self.compile(codestr, modname="foo")

    def test_final_reassign_explicit_global_shadowed(self):
        codestr = """
            from typing import Final

            a: Final[int] = 1337

            def fn():
                a = 2
                def fn2():
                    global a
                    a = 0
        """
        with self.assertRaisesRegex(
            TypedSyntaxError, "Cannot assign to a Final variable"
        ):
            self.compile(codestr, modname="foo")

    def test_final_reassign_nonlocal(self):
        codestr = """
            from typing import Final

            a: Final[int] = 1337

            def fn():
                def fn2():
                    nonlocal a
                    a = 0
        """
        with self.assertRaisesRegex(
            TypedSyntaxError, "Cannot assign to a Final variable"
        ):
            self.compile(codestr, modname="foo")

    def test_final_reassign_nonlocal_shadowed(self):
        codestr = """
            from typing import Final

            a: Final[int] = 1337

            def fn():
                a = 3
                def fn2():
                    nonlocal a
                    # should be allowed, we're assigning to the shadowed
                    # value
                    a = 0
        """
        self.compile(codestr, modname="foo")

    def test_final_reassigned_in_tuple(self):
        codestr = """
        from typing import Final

        x: Final[int] = 0xdeadbeef
        y = 3
        x, y = 4, 5
        """
        with self.assertRaisesRegex(
            TypedSyntaxError, "Cannot assign to a Final variable"
        ):
            self.compile(codestr, modname="foo")

    def test_final_reassigned_in_loop(self):
        codestr = """
        from typing import Final

        x: Final[int] = 0xdeadbeef

        for x in [1, 3, 5]:
            pass
        """
        with self.assertRaisesRegex(
            TypedSyntaxError, "Cannot assign to a Final variable"
        ):
            self.compile(codestr, modname="foo")

    def test_final_reassigned_in_except(self):
        codestr = """
        from typing import Final

        def f():
            e: Final[int] = 3
            try:
                x = 1 + "2"
            except Exception as e:
                pass
        """
        with self.assertRaisesRegex(
            TypedSyntaxError, "Cannot assign to a Final variable"
        ):
            self.compile(codestr, modname="foo")

    def test_final_reassigned_in_loop_target_tuple(self):
        codestr = """
        from typing import Final

        x: Final[int] = 0xdeadbeef

        for x, y in [(1, 2)]:
            pass
        """
        with self.assertRaisesRegex(
            TypedSyntaxError, "Cannot assign to a Final variable"
        ):
            self.compile(codestr, modname="foo")

    def test_final_reassigned_in_ctxmgr(self):
        codestr = """
        from typing import Final

        x: Final[int] = 0xdeadbeef

        with open("lol") as x:
            pass
        """
        with self.assertRaisesRegex(
            TypedSyntaxError, "Cannot assign to a Final variable"
        ):
            self.compile(codestr, modname="foo")

    def test_final_generic_reassign(self):
        codestr = """
        from typing import Final

        x: Final[int] = 0xdeadbeef
        x = 0x5ca1ab1e
        """
        with self.assertRaisesRegex(
            TypedSyntaxError, "Cannot assign to a Final variable"
        ):
            self.compile(codestr, modname="foo")

    def test_final_callable_protocol_retains_inferred_type(self):
        codestr = """
        from typing import Final, Protocol

        def foo(x: int) -> str:
            return "A"

        class CallableProtocol(Protocol):
            def __call__(self, x: int) -> str:
                pass

        f: Final[CallableProtocol] = foo

        def bar(x: int) -> str:
            return f(x)
        """
        with self.in_module(codestr) as mod:
            f = mod.bar
            self.assertInBytecode(f, "INVOKE_FUNCTION")

    def test_final_in_args(self):
        codestr = """
        from typing import Final

        def f(a: Final) -> None:
            pass
        """
        with self.assertRaisesRegex(
            TypedSyntaxError,
            "Final annotation is only valid in initial declaration",
        ):
            self.compile(codestr, modname="foo")

    def test_final_returns(self):
        codestr = """
        from typing import Final

        def f() -> Final[int]:
            return 1
        """
        with self.assertRaisesRegex(
            TypedSyntaxError,
            "Final annotation is only valid in initial declaration",
        ):
            self.compile(codestr, modname="foo")

    def test_final_decorator(self):
        codestr = """
        from typing import final

        class C:
            @final
            def f():
                pass
        """
        self.compile(codestr, modname="foo")

    def test_final_decorator_override(self):
        codestr = """
        from typing import final

        class C:
            @final
            def f():
                pass

        class D(C):
            def f():
                pass
        """
        with self.assertRaisesRegex(
            TypedSyntaxError, "Cannot assign to a Final attribute of foo.D:f"
        ):
            self.compile(codestr, modname="foo")

    def test_final_decorator_override_with_assignment(self):
        codestr = """
        from typing import final

        class C:
            @final
            def f():
                pass

        class D(C):
            f = print
        """
        with self.assertRaisesRegex(
            TypedSyntaxError, "Cannot assign to a Final attribute of foo.D:f"
        ):
            self.compile(codestr, modname="foo")

    def test_final_decorator_override_transitivity(self):
        codestr = """
        from typing import final

        class C:
            @final
            def f():
                pass

        class D(C):
            pass

        class E(D):
            def f():
                pass
        """
        with self.assertRaisesRegex(
            TypedSyntaxError, "Cannot assign to a Final attribute of foo.E:f"
        ):
            self.compile(codestr, modname="foo")

    def test_final_decorator_class(self):
        codestr = """
        from typing import final

        @final
        class C:
            def f(self):
                pass

        def f():
            return C().f()
        """
        c = self.compile(codestr, modname="foo")
        f = self.find_code(c, "f")
        self.assertInBytecode(f, "INVOKE_FUNCTION")

    def test_final_decorator_class_inheritance(self):
        codestr = """
        from typing import final

        @final
        class C:
            pass

        class D(C):
            pass
        """
        with self.assertRaisesRegex(
            TypedSyntaxError, "Class `foo.D` cannot subclass a Final class: `foo.C`"
        ):
            self.compile(codestr, modname="foo")

    def test_final_decorator_class_nonstatic_subclass(self):
        codestr = """
            from typing import final

            @final
            class C:
                pass
        """
        with self.in_module(codestr) as mod:
            with self.assertRaisesRegex(
                TypeError, "type 'C' is not an acceptable base type"
            ):

                class D(mod.C):
                    pass

    def test_final_decorator_class_dynamic(self):
        """We should never mark DYNAMIC_TYPE as final."""
        codestr = """
            from typing import final, Generic, NamedTuple

            @final
            class NT(NamedTuple):
                x: int

            class C(Generic):
                pass
        """
        # No TypedSyntaxError "cannot inherit from Final class 'dynamic'"
        self.compile(codestr)

    def test_final_constant_folding_int(self):
        codestr = """
        from typing import Final

        X: Final[int] = 1337

        def plus_1337(i: int) -> int:
            return i + X
        """
        with self.in_module(codestr) as mod:
            plus_1337 = mod.plus_1337
            self.assertInBytecode(plus_1337, "LOAD_CONST", 1337)
            self.assertNotInBytecode(plus_1337, "LOAD_GLOBAL")
            self.assertEqual(plus_1337(3), 1340)

    def test_final_constant_folding_bool(self):
        codestr = """
        from typing import Final

        X: Final[bool] = True

        def f() -> bool:
            return not X
        """
        with self.in_module(codestr) as mod:
            f = mod.f
            self.assertInBytecode(f, "LOAD_CONST", True)
            self.assertNotInBytecode(f, "LOAD_GLOBAL")
            self.assertFalse(f())

    def test_final_constant_folding_str(self):
        codestr = """
        from typing import Final

        X: Final[str] = "omg"

        def f() -> str:
            return X[1]
        """
        with self.in_module(codestr) as mod:
            f = mod.f
            self.assertInBytecode(f, "LOAD_CONST", "omg")
            self.assertNotInBytecode(f, "LOAD_GLOBAL")
            self.assertEqual(f(), "m")

    def test_final_constant_folding_disabled_on_nonfinals(self):
        codestr = """
        from typing import Final

        X: str = "omg"

        def f() -> str:
            return X[1]
        """
        with self.in_module(codestr) as mod:
            f = mod.f
            self.assertNotInBytecode(f, "LOAD_CONST", "omg")
            self.assertInBytecode(f, "LOAD_GLOBAL", "X")
            self.assertEqual(f(), "m")

    def test_final_constant_folding_disabled_on_nonconstant_finals(self):
        codestr = """
        from typing import Final

        def p() -> str:
            return "omg"

        X: Final[str] = p()

        def f() -> str:
            return X[1]
        """
        with self.in_module(codestr) as mod:
            f = mod.f
            self.assertNotInBytecode(f, "LOAD_CONST", "omg")
            self.assertInBytecode(f, "LOAD_GLOBAL", "X")
            self.assertEqual(f(), "m")

    def test_final_constant_folding_shadowing(self):
        codestr = """
        from typing import Final

        X: Final[str] = "omg"

        def f() -> str:
            X = "lol"
            return X[1]
        """
        with self.in_module(codestr) as mod:
            f = mod.f
            self.assertInBytecode(f, "LOAD_CONST", "lol")
            self.assertNotInBytecode(f, "LOAD_GLOBAL", "omg")
            self.assertEqual(f(), "o")

    def test_final_constant_folding_in_module_scope(self):
        codestr = """
        from typing import Final

        X: Final[int] = 21
        y = X + 3
        """
        c = self.compile(codestr, modname="foo.py")
        self.assertNotInBytecode(c, "LOAD_NAME", "X")
        with self.in_module(codestr) as mod:
            self.assertEqual(mod.y, 24)

    def test_final_constant_in_module_scope(self):
        codestr = """
        from typing import Final

        X: Final[int] = 21
        """
        with self.in_module(codestr) as mod:
            self.assertEqual(mod.__final_constants__, ("X",))

    def test_final_nonconstant_in_module_scope(self):
        codestr = """
        from typing import Final

        def p() -> str:
            return "omg"

        X: Final[str] = p()
        """
        with self.in_module(codestr) as mod:
            self.assertEqual(mod.__final_constants__, ())