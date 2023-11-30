# Measurements

In contrast to synthesis, measurements come at least in a file. Depending on the measurement software more or less meta data is provided. Here we  focus on two important steps.

1. We need to make sure that individual measurements contain relevant metadata, usually this is a quite involved task, ideas are here to convert some measurments into [NeXus](http://www.nexusformat.org/)
   or to develop new standards and then making sure that the measurement software complies to these standards.
2. Once a data file exist, independent of the quality of the metadata, we provide parser in nomad, which read the files and create entries in nomad. Ideally at least the sample id of the measured samples is
   provided so that the relevant linking in nomad is established (see: [upload_measurement.md](../how_to/upload_measurement.md) for a possible solution).

Then uploading and processing these files to nomad is straight forward and can be either done by drag and dropping multiple measurement files or upload them through nomad API.
