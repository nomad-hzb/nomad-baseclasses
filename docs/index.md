
# NOMAD HZB base classes Plugin

## What is this Plugin?

This plugin provides a set of base schemas for the digital representation of synthesis and characterization techniques in materials science with focus on thin film solar cell and electro chemistry research. Developed at Helmholtz-Zentrum Berlin (HZB), it serves as a foundation for the NOMAD ecosystem, enabling standardized, interoperable, and extensible data management for a wide range of experimental workflows.

The plugin is under active development. We take care that the schemas in the plugins remains compatible through extensions and changes and are open for feedback and discussions. We believe that science digitalization and data management is subject to changes through usage of and exchange with lab scientist. The schemas are using vocabulary from [voc4cat](https://github.com/nfdi4cat/voc4cat) fir catalysis and from the [TFSCO](https://github.com/nomad-hzb/autoperosol) for thin film solar cells. Nomad quantities contain links referencing the respective concepts.

We believe that it is key to link digital information of all synthesis and characterization steps against the material science samples. With this plugin we give structure to all of this information.

## Key Features

- **Broad Coverage:** Includes schemas for synthesis, processing, and characterization of materials, with a focus on photovoltaics and electro chemistry.
- **Specializations:** Offers models for perovskite solar cell research, and electro chemistry.
- **Extensibility:** Designed to be extended for new techniques and custom workflows in further plugins extending and specializing these classes further.

## Main Schema Areas


### Synthesis & Processing

The plugin provides a rich set of schemas to capture the full complexity of modern materials synthesis, supporting both traditional and advanced methods:

- **Wet Chemical Deposition:**

    - Covers solution-based techniques such as spin coating, dip coating, drop casting, inkjet printing, doctor blading, spray pyrolysis, slot die coating.
    - Includes tracking of precursor solutions, concentrations, solvents, additives, and process parameters (e.g., temperature, humidity, atmosphere).
    - Supports multi-step protocols for layer-by-layer fabrication, post-deposition treatments (e.g., annealing, quenching), and combinatorial approaches.
    - Enables documentation of substrate cleaning.

- **Vapour-Based Deposition:**

    - Models for evaporations, sputtering, atomic layer deposition (ALD), and related techniques.
    - Captures source materials, gas flows, chamber conditions, substrate preparation.
    - Enables documentation of multi-source and multi-step processes, essential for advanced thin-film and nanostructure fabrication.
    - Supports hybrid and sequential deposition strategies, such as co-evaporation.

- **Electro chemical deposition:**

    - Schemas for the documentation of the electro chemical environment (electrolyte, puurging) and setup (electrodes, tools used)
    - Framework for linking various kinds of potentiometries with used sample, environment and setup.


These synthesis schemas are designed to interoperate with characterization and assay schemas, enabling tracking of a material’s full experimental history from initial preparation to final measurement.


### Characterization Techniques

- **Solar Energy Specializations:**

    - JV (current-voltage) measurements
    - Maximum power point (MPP) tracking
    - Photoluminescence (PL) and time-resolved PL
    - EQE (external quantum efficiency)
    - Conductivity and substrate characterization

- **Electrochemical & Catalysis:**

    - Cyclic voltammetry, chronoamperometry, chronopotentiometry, OCP
    - Electrochemical impedance spectroscopy
 
- **General Characterizations:** (general techniques are not covered in detail since they are planned to be covered by the NeXus Standard see also [pynxtools](https://github.com/FAIRmat-NFDI/pynxtools))

    - There are some comprehensive schemae,e.g. for XPS and SEM as well as XRF for combinatorial meaurments.
    - There are general schemas to link arbitrary data to samples as a placeholder for future extension.

## How to Use

These schemas are intended as building blocks for labs specific plugins and parsers. They can be extended and specialized a new lab specific needs. They are already used by several groups in NOMAD plugins, such as:

- [HZB Solar Cells](https://github.com/nomad-hzb/nomad-hysprint)
- [HZB Electro Catalysis](https://github.com/nomad-hzb/nomad-chemical-energy)
- [KIT Solar Cells](https://github.com/nomad-hzb/nomad-perotf)

To learn more about plugins, check the official [NOMAD documentation](https://nomad-lab.eu/prod/v1/staging/docs/howto/plugins/plugins.html)
