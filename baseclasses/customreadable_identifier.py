from nomad.metainfo import (
    Quantity, Section
)

from nomad.datamodel.metainfo.basesections import (
    ReadableIdentifiers
)


class ReadableIdentifiersCustom(ReadableIdentifiers):
    m_def = Section(
        a_eln=dict(
            hide=["sample_owner", "sample_short_name", "sample_id"]
        ))

    sample_owner = Quantity(
        type=str,
        shape=[],
        a_eln=dict(component='StringEditQuantity'))

    sample_short_name = Quantity(
        type=str,
        shape=[],
        a_eln=dict(component='StringEditQuantity'))

    sample_id = Quantity(
        type=str,
        shape=[],
        a_eln=dict(component='StringEditQuantity'))

    def normalize(self, archive, logger):
        if self.sample_owner and self.owner is None:
            self.owner = self.sample_owner
        if self.sample_short_name and self.short_name is None:
            self.sample_short_name = self.short_name
        if self.sample_id and self.lab_id is None:
            self.sample_id = self.lab_id

        super(ReadableIdentifiersCustom, self).normalize(archive, logger)
