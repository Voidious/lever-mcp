import main


def get_engine_expression(lua_expr, js_expr):
    """Return appropriate expression based on current engine configuration."""
    if getattr(main, "USE_JAVASCRIPT", False):
        return js_expr
    else:
        return lua_expr
