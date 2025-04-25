from llvmlite import ir

class Environment:
    """ Symbol Table with Initialization Tracking """
    def __init__(self, records: dict[str, tuple[ir.Value, ir.Type, bool]] = None, parent=None, name: str = "global") -> None:
        self.records: dict[str, tuple[ir.Value, ir.Type, bool]] = records if records else {}
        self.parent: Environment | None = parent
        self.name: str = name

    def define(self, name: str, ptr: ir.Value, _type: ir.Type, initialized: bool = False) -> ir.Value:
        self.records[name] = (ptr, _type, initialized)
        return ptr

    def lookup(self, name: str) -> tuple[ir.Value, ir.Type, bool] | None:
        return self.__resolve(name)

    def set_initialized(self, name: str):
        if name in self.records:
            ptr, typ, _ = self.records[name]
            self.records[name] = (ptr, typ, True)
        elif self.parent:
            self.parent.set_initialized(name)
        else:
            raise Exception(f"Variable '{name}' not declared")

    def __resolve(self, name: str) -> tuple[ir.Value, ir.Type, bool] | None:
        if name in self.records:
            return self.records[name]
        elif self.parent:
            return self.parent.__resolve(name)
        else:
            return None  # Let the compiler raise the error
