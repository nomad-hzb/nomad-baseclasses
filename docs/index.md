
# NOMAD HZB base classes Plugin

## What is this Plugin?

This plugin provides a comprehensive set of base schemas for the digital representation of synthesis and characterization techniques in materials science. Developed at Helmholtz-Zentrum Berlin (HZB), it serves as a foundation for the NOMAD ecosystem, enabling standardized, interoperable, and extensible data management for a wide range of experimental workflows.

## Key Features

- **Broad Coverage:** Includes schemas for synthesis, processing, and characterization of materials, with a focus on photovoltaics and heterogeneous catalysis.
- **Specializations:** Offers detailed models for perovskite solar cell research, electrochemical energy conversion, and catalytic processes.
- **Extensibility:** Designed to be extended for new techniques and custom workflows in further plugins extending and specializing these classes further.

## Main Schema Areas


### Synthesis & Processing

The plugin provides a rich set of schemas to capture the full complexity of modern materials synthesis, supporting both traditional and advanced methods:

- **Wet Chemical Deposition:**

    - Covers solution-based techniques such as spin coating, dip coating, drop casting, inkjet printing, and doctor blading.
    - Includes detailed tracking of precursor solutions, concentrations, solvents, additives, and process parameters (e.g., temperature, humidity, atmosphere).
    - Supports multi-step protocols for layer-by-layer fabrication, post-deposition treatments (e.g., annealing, washing), and combinatorial approaches.
    - Enables documentation of substrate cleaning, surface functionalization, and interface engineering steps.

- **Vapour-Based Deposition:**

    - Models for physical vapor deposition (PVD), chemical vapor deposition (CVD), atomic layer deposition (ALD), and related techniques.
    - Captures source materials, gas flows, chamber conditions, substrate preparation, and in-situ monitoring.
    - Enables documentation of complex multi-source and multi-step processes, essential for advanced thin-film and nanostructure fabrication.
    - Supports hybrid and sequential deposition strategies, such as co-evaporation and pulsed laser deposition.

- **Solution Manufacturing:**

    - Schemas for the preparation, mixing, and storage of chemical solutions used in synthesis.
    - Tracks batch information, purity, and handling protocols to ensure reproducibility and traceability.
    - Supports documentation of precursor aging, filtration, and quality control procedures.

- **Material Processes Miscellaneous:**

    - Additional protocols for specialized or emerging synthesis methods not covered by standard categories.
    - Flexible schema design allows for rapid adaptation to new experimental workflows, including combinatorial and high-throughput synthesis.

- **Atmosphere and Environmental Control:**

    - Detailed models for controlled-atmosphere synthesis, including glovebox operations, inert gas handling, and environmental monitoring.
    - Enables tracking of environmental parameters throughout the synthesis process for reproducibility and data integrity.

These synthesis schemas are designed to interoperate with characterization and assay schemas, enabling seamless tracking of a material’s full experimental history from initial preparation to final measurement.


### Characterization Techniques

- **General Characterizations:**

    - Raman, IR, UV-Vis, and ellipsometry spectroscopy
    - X-ray techniques: XRD, XRF, XAS, XPS, XRR, XPEEM
    - Electron microscopy: SEM, TEM, and specialized detectors
    - Surface and interface analysis

- **Solar Energy Specializations:**

    - JV (current-voltage) measurements
    - Maximum power point (MPP) tracking
    - Photoluminescence (PL) and time-resolved PL
    - EQE (external quantum efficiency)
    - Conductivity and substrate characterization

- **Electrochemical & Catalysis:**

    - Cyclic voltammetry, chronoamperometry, chronopotentiometry
    - Electrochemical impedance spectroscopy
    - Catalytic sample and measurement schemas
    - Gas-phase and solution-phase catalysis protocols


### Assays & Atmosphere

- **Assays:**

    - Environmental and process measurement schemas.

- **Atmosphere:**

    - Models for controlled environment and gas-phase experiments.

## How to Use

These schemas are intended as building blocks for labs specific plugins and parsers. They can be extended and specialized a new lab specific needs. They are already used by several groups in NOMAD plugins, such as:

- [HZB Solar Cells](https://github.com/nomad-hzb/nomad-hysprint)
- [HZB Electro Catalysis](https://github.com/nomad-hzb/nomad-chemical-energy)
- [KIT Solar Cells](https://github.com/nomad-hzb/nomad-perotf)

To learn more about plugins, check the official [NOMAD documentation](https://nomad-lab.eu/prod/v1/staging/docs/howto/plugins/plugins.html)
