# Synthesis

The challenging part in material science is to model the synthesis of devices, such as solar cells, properly. Especially if these steps include information which is not stored in files automatically. This includes information on the manufacturing of solutions, but also the deposition of layers with manual Spin Coating, Slot Die Coating, and of course cleaning and annealing and quenching. All of these steps have plenty of parameters which need to be documented properly and inpart have great influence on the functional quality of the resulting devices. On the other hand we need to make sure that the manual work to document these steps for lab scientists needs to be as minimized as possible.


## Perovskite solar cells
For this task we developed the experimental planning tool for perovskite solarcell synthesis. It allows to create the required synthesis information from pre-created templates and links all of these steps together. It provides tools to efficiently manipulate the templates for parameter variation.

### Example 1

I want to produce a solar cell using:

1. Standard cleaning
2. A standard spin-coated SAM HTL
3. Slot Die Coating CsMAFAPbI3 as a absorber layer, where I vary the anti-solvent chemicals, and the dropping time of the anti-solvent
4. Standard evaporation of C60 and BCP as ETLs
5. Standard evaporation of Cu as a back contact

As variable parameters I want Ethanol, and Anisole as anti-solvents and exploring 5, 10 ,15 ,20 ,25 seconds as the dropping time in each of them.

### Example 2

I want to produce a solar cell using:

1. Standard cleaning
2. A standard spin-coated SAM HTL
3. AlO3 as a Slot Die Coated buffer layer, which is present in one half and absent in the other half of my batch
4. Standard spin-coating MAPbI3 as a absorber layer
5. Standard evaporation of C60 and BCP as ETLs
6. Standard evaporation of Cu as a back contact

The experimental planning tool is designed to document these plans efficiently provided that the standard processes exist, see: [create experimental plan](create_experimental_plan.md), [create standard sample](create_standard_sample.md) and [create wet chemical deposition](create_wet_chemical_deposition.md) for more how-tos.
