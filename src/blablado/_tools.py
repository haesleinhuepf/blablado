from langchain.tools import StructuredTool, tool
from ._machinery import _context

if _context.verbose:
    print("Setting up tools")


@_context.tools.append
@tool
def list_tools():
    """Lists all available tools"""

    return "\n".join(list([t.name for t in _context.tools]))


@_context.tools.append
@tool
def nop():
    """This is a no-op function. It does nothing. It is useful in case you don't know what to do."""
    print("nop")
