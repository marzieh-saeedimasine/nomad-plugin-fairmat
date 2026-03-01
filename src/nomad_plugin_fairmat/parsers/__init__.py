from nomad.config.models.plugins import ParserEntryPoint


class SinteringParserEntryPoint(ParserEntryPoint):
    """Entry point for the Sintering CSV parser."""

    def load(self):
        from nomad_plugin_fairmat.parsers.sintering_parser import SinteringParser

        return SinteringParser(**self.dict())


parser_entry_point = SinteringParserEntryPoint(
    name='SinteringParser',
    description='Parser for sintering process CSV files with temperature ramp data.',
    mainfile_name_re=r'sintering.*\.csv',  # Match sintering-specific CSV files only
    mainfile_mime_re=r'text/csv',
)
