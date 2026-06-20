# Import the schemas and functions from our three sub-modules
from .files import FILE_TOOLS, read_file, write_file, edit_file, list_files
from .web import WEB_TOOLS, web_search, web_fetch
from .papers import PAPER_TOOLS, paper_search, read_paper

# 1. THE MASTER SCHEMA LIST
# We add all the individual tool lists together into one giant list.
# We will hand this directly to the LLM so it knows every tool it has.
ALL_TOOLS = FILE_TOOLS + WEB_TOOLS + PAPER_TOOLS

# 2. THE DISPATCH DICTIONARY
# This connects the string name the AI outputs (e.g., "read_file") 
# to the actual physical Python function in your code.
TOOL_FUNCTIONS = {
    "read_file": read_file,
    "write_file": write_file,
    "edit_file": edit_file,
    "list_files": list_files,
    "web_search": web_search,
    "web_fetch": web_fetch,
    "paper_search": paper_search,
    "read_paper": read_paper
}