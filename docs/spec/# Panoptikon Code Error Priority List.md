# # Panoptikon Code Error Priority List
# Critical (Fix Immediately)
* ⚠️ Dataclass ordering: Non-default attributes after default ones
* ⚠️ MRO issues in class inheritance
* ⚠️ Null safety: Calling methods on potential None values
* ⚠️ Circular dependencies

⠀High (Fix Before Merge)
* Type annotation correctness and null safety
* Function complexity > 10
* Missing type annotations
* Unhandled exceptions
* Proper thread safety
* Memory leaks in PyObjC code

⠀Medium (Fix During Code Review)
* Modern syntax: Use list not List, X | Y not Union[X, Y]
* Nested if statements and control flow
* File length > 500 lines
* Function length > 50 lines
* Unused imports and code

⠀Low (Fix When Convenient)
* Line length consistency
* Docstring coverage
* Using optimized patterns (contextlib.suppress)
* Import order
* String format consistency

⠀Include this with prompts to remind of error priorities during development.
