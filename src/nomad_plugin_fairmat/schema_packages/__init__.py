from nomad.config.models.plugins import SchemaPackageEntryPoint


class SinteringEntryPoint(SchemaPackageEntryPoint):

    def load(self):
        from nomad_plugin_fairmat.schema_packages.sintering import m_package

        return m_package


sintering = SinteringEntryPoint(
    name='Sintering',
    description='Schema package for describing a sintering process.',
)

schema_package_entry_point = sintering
