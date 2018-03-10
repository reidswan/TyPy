from inspect import signature
from typing import Callable, Any, Type, List, Dict, TypeVar, Generic, MutableMapping, GenericMeta, Tuple
from collections import OrderedDict

# generic 
T = TypeVar('T')

class TypedFunction(Callable, Generic[T]):
    """
    A class representing a strongly typed function
    """
    def __init__(self, f: Callable[..., T], arg_types: MutableMapping[str, Type], return_type: Type):
        # NOTE: using MutableMapping[k,v] as workaround for OrderedDict[k,v]
        self.f = f
        self.arg_types = OrderedDict([
            (key, val._gorg if val.__class__ is GenericMeta else val)
            for key, val in arg_types.items()
        ])
        self.return_type = return_type._gorg if return_type.__class__ is GenericMeta else return_type
        self.signature = [key + ": " + val.__name__ for key, val in arg_types.items()]
        try:
            self.__name__ = f.__name__
        except:
            self.__name__ = 'Anonymous typed function'

    def __call__(self, *args: List[Any], **kwargs: Dict[str, Any])-> T:
        if not self._valid_type_args(args, kwargs):
            raise TypeError("Expected argument types {} but got {}"
                .format(self.signature, to_signature(args, kwargs)))
        ans = self.f(*args, **kwargs)
        if not self._valid_type_return(ans):
            raise TypeError("Expected return type {} but got {}"
                .format(self.return_type.__name__, type(ans).__name__))
        return ans

    def _valid_type_args(self, args: Tuple[Any], kwargs: Dict[str, Any])-> bool:
        arg_types = self.arg_types.copy()
        args = list(args)
        for key, value in kwargs.items():
            try:
                expected = arg_types.pop(key)
                if expected is not Any and not isinstance(value, expected):
                    return False
            except KeyError:
                raise TypeError("Unexpected keyword argument: {}".format(key))
        while len(args):
            try:
                arg = args.pop()
                _, value = arg_types.popitem()
                if value is not Any and not isinstance(arg, value):
                    return False
            except KeyError:
                raise TypeError("Too many arguments supplied to function")
        return True

    def _valid_type_return(self, ret_val: Any)-> bool:
        return self.return_type is Any or isinstance(ret_val, self.return_type)

def to_signature(args: List[Any], kwargs: Dict[str, Any])-> List[str]:
    return ([type(i).__name__ for i in args] 
        + [key + ": " + type(val).__name__ for key, val in kwargs.items()])

def strongly_typed(f):
    """
    Decorator for an annotated function to be strongly type checked 
    (... at runtime ...)
    """
    sig = signature(f)
    params = sig.parameters
    arg_types = OrderedDict(
        [(name, params[name].annotation) for name in params]
    )
    return_type = sig.return_annotation
    return TypedFunction(f, arg_types, return_type)