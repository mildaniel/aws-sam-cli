from samcli.cli.formatters import RootCommandHelpTextFormatter
from samcli.cli.row_modifiers import BaseLineRowModifier


class DocsCommandHelpTextFormatter(RootCommandHelpTextFormatter):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.left_justification_length = self.width // 2 - self.indent_increment
        self.modifiers = [BaseLineRowModifier()]
