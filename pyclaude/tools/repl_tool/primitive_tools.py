# REPL Tool Primitive Tools
# Reference: src/tools/REPLTool/primitiveTools.ts

# Import tool classes - lazy loading to avoid circular imports
_primitive_tools = None


def get_repl_primitive_tools():
    """Get primitive tools hidden from direct model use when REPL mode is on"""
    global _primitive_tools

    if _primitive_tools is None:
        from ..read_tool.file_read_tool import FileReadTool
        from ..write_tool.write_tool import FileWriteTool
        from ..edit_tool.file_edit_tool import FileEditTool
        from ..glob_tool.glob_tool import GLOB_TOOL_NAME
        from ..grep_tool.grep_tool import GREP_TOOL_NAME
        from ..bash_tool.bash_tool import BashTool
        from ..notebook_edit_tool.notebook_edit_tool import NotebookEditTool
        from ..agent_tool.agent_tool import AgentTool

        _primitive_tools = [
            FileReadTool,
            FileWriteTool,
            FileEditTool,
            GLOB_TOOL_NAME,
            GREP_TOOL_NAME,
            BashTool,
            NotebookEditTool,
            AgentTool,
        ]

    return _primitive_tools