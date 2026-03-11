# ===================================
#          Base Error Boundary 
# ===================================
'''
To keep error handling as clean and decoupled as possible, we're breaking
the project into distinct error boundaries which bubble up (but never down)
the project structure.

This MixIn will give the public functions of a class a simple wrapper to ensure
that the function is run through the correct error section. 

Private functions (e.g. _do_something) will not be wrapped.
Dunder functions (e.g. __repr__) will not be wrapped.

'''
class BoundaryMixin:
    BOUNDARY = None  # override in subclasses

    def __getattribute__(self, name):
        attr = super().__getattribute__(name)

        # Only wrap: callable methods, not dunders, not privates
        if (
            callable(attr) 
            and not name.startswith("_")
            and not name.startswith("__")
        ):
            boundary = super().__getattribute__("BOUNDARY")

            if boundary is None:
                return attr

            # Return a wrapper that runs the boundary
            def wrapper(*args, **kwargs):
                return boundary.run(attr, *args, **kwargs)

            return wrapper

        return attr
