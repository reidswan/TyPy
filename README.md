# TyPy
Simplistic decorator-based runtime type checker for Python

## Usage
    from typy import strongly_typed
    
    @strongly_typed
    def foo(bar: str, baz: List[str])-> str:
        # do something
        # be sure to return a str
        return "some string"
