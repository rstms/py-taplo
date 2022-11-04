# taplo config file toml text

# https://taplo.tamasfe.dev/

config_toml = """
include = []

[formatting]
align_comments        = true
align_entries         = true
allowed_blank_lines   = 1
array_auto_collapse   = false
array_auto_expand     = true
array_trailing_comma  = true
column_width          = 1
compact_arrays        = false
compact_entries       = false
compact_inline_tables = false
crlf                  = false
indent_entries        = true
indent_string         = "  "
indent_tables         = true
reorder_keys          = true
trailing_newline      = true

[[rule]]
include = ["**/pyproject.toml"]

[rule.schema]
path=https://json.schemastore.org/pyproject.json
"""
