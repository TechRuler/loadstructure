# class SchemaError(Exception):
#     """Raised when configuration does not match schema rules."""
#     pass

# class ConfigNode:
#     """Wraps a dictionary to allow attribute-style and dict-style access
#     with automatic nested creation and dict wrapping."""

#     def __init__(self, d=None, schema=None):
#         object.__setattr__(self, "_data", {})
#         d = d or {}
#         self._schema = schema
#         for key, value in d.items():
#             self._data[key] = self._wrap(value)

#     # ------------------ WRAPPING ------------------
#     def _wrap(self, value, rule):
#         # If rule is dict TYPE → allow any child (no schema inside)
#         if rule == dict:
#             if isinstance(value, dict):
#                 return ConfigNode(value, None)  # no inner validation
#             return value

#         # If rule is nested SCHEMA (actual dict)
#         if isinstance(rule, dict):
#             if isinstance(value, dict):
#                 return ConfigNode(value, rule)
#             return value

#         # Default wrapping
#         if isinstance(value, dict):
#             return ConfigNode(value)
#         elif isinstance(value, list):
#             return [self._wrap(v) for v in value]
#         return value

#     # ------------------ AUTO-CREATE GET ------------------
#     def __getattr__(self, key):
#         if key not in self._data:
#             # auto-create nested empty ConfigNode
#             self._data[key] = ConfigNode({})
#         return self._data[key]

#     # ------------------ AUTO-WRAP SET ------------------
#     def __setattr__(self, key, value):
#         if key == "_data":  # internal attribute
#             return object.__setattr__(self, key, value)
#         self._data[key] = self._wrap(value)

#     # ------------------ DICT ACCESS ------------------
#     def __getitem__(self, key):
#         if key not in self._data:
#             self._data[key] = ConfigNode({})
#         return self._data[key]

#     def __setitem__(self, key, value):
#         self._data[key] = self._wrap(value)

#     # ------------------ UPDATE ------------------
#     def update(self, d: dict):
#         for key, value in d.items():
#             self._data[key] = self._wrap(value)

#     # ------------------ REPLACE (FOR WHOLE CFG) ------------------
#     def replace(self, new_dict: dict):
#         self._data.clear()
#         for key, value in new_dict.items():
#             self._data[key] = self._wrap(value)

    # # ------------------ SET using dotted path ------------------
    # def set(self, dotted_key: str, value):
    #     parts = dotted_key.split(".")
    #     node = self
    #     for p in parts[:-1]:
    #         if p not in node._data or not isinstance(node._data[p], ConfigNode):
    #             node._data[p] = ConfigNode({})
    #         node = node._data[p]
    #     node._data[parts[-1]] = self._wrap(value)

    # # ------------------ GET using dotted path ------------------
    # def get(self, dotted_key, default=None):
    #     parts = dotted_key.split(".")
    #     node = self
    #     for p in parts:
    #         if isinstance(node, ConfigNode) and p in node._data:
    #             node = node._data[p]
    #         else:
    #             return default
    #     return node

#     # ------------------ CONVERT TO DICT ------------------
#     def to_dict(self):
#         def convert(v):
#             if isinstance(v, ConfigNode):
#                 return v.to_dict()
#             elif isinstance(v, list):
#                 return [convert(x) for x in v]
#             return v

#         return {k: convert(v) for k, v in self._data.items()}
#     # ----------------- Validataions -----------------------
#     def _validate(self, key, value):
#         if not self._schema:
#             return  # schema not provided → no validation

#         if key not in self._schema:
#             raise SchemaError(f"'{key}' not allowed in schema.")

#         rule = self._schema[key]

#         # Case 1 — rule == dict TYPE → only check type
#         if rule == dict:
#             if not isinstance(value, (dict, ConfigNode)):
#                 raise SchemaError(f"'{key}' must be a dict.")
#             return

#         # Case 2 — nested schema (actual schema dict)
#         if isinstance(rule, dict):
#             if not isinstance(value, (dict, ConfigNode)):
#                 raise SchemaError(f"'{key}' must be a dict/object.")
#             return

#         # Case 3 — normal expected type
#         if isinstance(rule, type):
#             if not isinstance(value, rule):
#                 raise SchemaError(
#                     f"'{key}' must be {rule.__name__}, got {type(value).__name__}"
#                 )


class SchemaError(Exception):
    """Raised when configuration does not match the schema rules."""
    pass


class ConfigNode:
    def __init__(self, d=None, schema=None):
        object.__setattr__(self, "_data", {})
        object.__setattr__(self, "_schema", schema)
        d = d or {}

        for key, value in d.items():
            rule = self._schema.get(key) if schema else None
            self._data[key] = self._wrap(value, rule)

    # -------------------- WRAP WITH VALIDATION --------------------
    def _wrap(self, value, rule=None):
        # validate before wrapping
        if rule is not None:
            self._validate(rule, value)

        # nested schema dict → create nested ConfigNode with that schema
        if isinstance(rule, dict):
            if isinstance(value, dict):
                return ConfigNode(value, rule)
            return ConfigNode({}, rule)

        # rule == dict → any dict allowed
        if rule == dict:
            if isinstance(value, dict):
                return ConfigNode(value, None)   # no inner schema
            return value

        # default wrapping
        if isinstance(value, dict):
            return ConfigNode(value, None)
        elif isinstance(value, list):
            return [self._wrap(v) for v in value]
        return value
    # -------------------- AUTO-CREATE MISSING KEYS --------------------
    def __getattr__(self, key):

        # -------- Case 1: No schema: always auto-create dict nodes --------
        if self._schema is None:
            if key not in self._data:
                self._data[key] = ConfigNode({}, None)
            return self._data[key]

        # -------- Case 2: Schema exists --------
        if key not in self._schema:
            raise SchemaError(f"'{key}' is not allowed by the schema.")

        # Already created
        if key in self._data:
            return self._data[key]

        rule = self._schema[key]

        # -------- Rule is nested dict → auto create ConfigNode --------
        if isinstance(rule, dict):
            node = ConfigNode({}, rule)
            self._data[key] = node
            return node

        # -------- Rule is dict type (any dict allowed) --------
        if rule == dict:
            node = ConfigNode({}, None)
            self._data[key] = node
            return node

        # -------- Primitive type → cannot auto-create --------
        raise SchemaError(
            f"Cannot auto-create '{key}' because schema expects primitive type {rule.__name__}"
        )

    # -------------------- SET ATTR WITH VALIDATION --------------------
    def __setattr__(self, key, value):

        # Internal attributes
        if key in ("_data", "_schema"):
            super().__setattr__(key, value)
            return

        # -------- Case 1: No schema → accept anything, auto-wrap dicts --------
        if self._schema is None:
            if isinstance(value, dict):
                self._data[key] = ConfigNode(value, None)
            else:
                self._data[key] = value
            return

        # -------- Case 2: Schema exists --------
        if key not in self._schema:
            raise SchemaError(f"'{key}' is not allowed by the schema.")

        rule = self._schema[key]

        # -------- Nested dict rule --------
        if isinstance(rule, dict):
            if not isinstance(value, dict):
                raise SchemaError(f"Invalid type for '{key}'. Expected dict.")
            self._data[key] = ConfigNode(value, rule)
            return

        # -------- Dict rule with no subschema --------
        if rule == dict:
            if not isinstance(value, dict):
                raise SchemaError(f"Invalid type for '{key}'. Expected dict.")
            self._data[key] = ConfigNode(value, None)
            return

        # -------- Primitive type rule --------
        if not isinstance(value, rule):
            raise SchemaError(
                f"Invalid type for '{key}'. Expected {rule.__name__}, got {type(value).__name__}"
            )

        self._data[key] = value



    # -------------------- DICT ACCESS --------------------
    def __setitem__(self, key, value):
        rule = self._schema.get(key) if self._schema else None
        self._data[key] = self._wrap(value, rule)

    def __getitem__(self, key):
        return self.__getattr__(key)
    
    # ------------------ SET using dotted path (with schema) ------------------
    def set(self, dotted_key: str, value):
        parts = dotted_key.split(".")
        node = self

        # ------------------ Traverse intermediate keys ------------------
        for p in parts[:-1]:

            # Determine subschema for this key
            if node._schema is None:
                subschema = None
            else:
                if p not in node._schema:
                    raise SchemaError(f"'{p}' is not allowed by the schema.")

                rule = node._schema[p]

                if isinstance(rule, dict):
                    subschema = rule
                elif rule == dict:              # dict allowed, no subschema
                    subschema = None
                else:
                    raise SchemaError(
                        f"Cannot auto-create '{p}' because schema expects primitive {rule.__name__}"
                    )

            # Auto-create node if missing
            if p not in node._data or not isinstance(node._data[p], ConfigNode):
                node._data[p] = ConfigNode({}, subschema)

            node = node._data[p]

        # ------------------ Handle last key ------------------
        last = parts[-1]

        # Schema validation
        if node._schema is not None:
            if last not in node._schema:
                raise SchemaError(f"'{last}' is not allowed by the schema.")

            rule = node._schema[last]

            # Nested dict rule
            if isinstance(rule, dict):
                if not isinstance(value, dict):
                    raise SchemaError(
                        f"Invalid type for '{last}'. Expected nested dict."
                    )
                node._data[last] = ConfigNode(value, rule)
                return

            # dict allowed
            if rule == dict:
                if not isinstance(value, dict):
                    raise SchemaError(
                        f"Invalid type for '{last}'. Expected dict."
                    )
                node._data[last] = ConfigNode(value, None)
                return

            # Primitive type rule
            if not isinstance(value, rule):
                raise SchemaError(
                    f"Invalid type for '{last}'. Expected {rule.__name__}, got {type(value).__name__}"
                )

            # Assign directly
            node._data[last] = value
            return

        # ------------------ No schema → free mode ------------------
        if isinstance(value, dict):
            node._data[last] = ConfigNode(value, None)
        else:
            node._data[last] = value

    # ------------------ GET using dotted path ------------------
    def get(self, dotted_key, default=None):
        parts = dotted_key.split(".")
        node = self
        for p in parts:
            if isinstance(node, ConfigNode) and p in node._data:
                node = node._data[p]
            else:
                return default
        return node


    # -------------------- VALIDATION CORE --------------------
    def _validate(self, rule, value):
        # rule == dict (type) → must be dict-like
        if rule == dict:
            if not isinstance(value, (dict, ConfigNode)):
                raise SchemaError(f"value must be dict, got {type(value).__name__}")
            return

        # nested schema (dict)
        if isinstance(rule, dict):
            if not isinstance(value, (dict, ConfigNode)):
                raise SchemaError("value must be an object/dict")
            return
        
        # validate list type
        if rule == list:
            if not isinstance(value, list):
                raise SchemaError(f"value must be list, got {type(value).__name__}")
            return


        # rule is a normal Python type
        if isinstance(rule, type):
            if not isinstance(value, rule):
                raise SchemaError(f"value must be {rule.__name__}, got {type(value).__name__}")

    # -------------------- to_dict --------------------
    def to_dict(self):
        def convert(v):
            if isinstance(v, ConfigNode):
                return v.to_dict()
            if isinstance(v, list):
                return [convert(x) for x in v]
            return v

        return {k: convert(v) for k, v in self._data.items()}

    # -------------------- UPDATE (with validation) --------------------
    def update(self, d: dict):
        for key, value in d.items():
            rule = self._schema.get(key) if self._schema else None
            self._data[key] = self._wrap(value, rule)
    # -------------------- REPLACE (validate entire dict before replacing) --------------------
    def replace(self, new_dict: dict):
        # validate first
        for key, value in new_dict.items():
            rule = self._schema.get(key) if self._schema else None
            self._validate(rule, value)

        # replace after full validation
        self._data.clear()
        for key, value in new_dict.items():
            rule = self._schema.get(key) if self._schema else None
            self._data[key] = self._wrap(value, rule)

    # ------------------ ITERATION & DICT-LIKE ACCESS ------------------
    def items(self):
        return self._data.items()

    def keys(self):
        return self._data.keys()
    
    def values(self):
        return self._data.values()

    def __iter__(self):
        """Iterate over keys."""
        return iter(self._data)

    def __len__(self):
        return len(self._data)

    def __repr__(self):
        return f"ConfigNode({self._data})"

    def __dir__(self):
        """Allow tab-completion for dynamic keys."""
        return list(super().__dir__()) + list(self._data.keys())
