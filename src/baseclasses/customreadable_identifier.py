from nomad.datamodel.metainfo.basesections import ReadableIdentifiers
from nomad.metainfo import Quantity, Section


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
        if self.sample_owner:
            self.owner = self.sample_owner
        if self.sample_short_name:
            self.short_name = self.sample_short_name
        if self.sample_id and self.lab_id is None:
            self.lab_id = self.sample_id

        super(ReadableIdentifiersCustom, self).normalize(archive, logger)
