# Snythesis

The challinging part in material science is to model the synthesis of devices, such as solar cells, properly. Especially if these steps include information which is not stored in files automatically. This includes infromation on the manufacturing of solutions, but also the deposition of layers with manual Spin Coating, Slot Die Coating, and of course cleaning and annealing and quenching. All of these steps have plenty of parameters which need to be documented properly and inpart have great influence on the functional quality of the resulting devices. On the other hand we need to make sure that the manual work to document these steps for lab scientists needs to be as minimized as possible.


## Perovskite solar cells
For this task we developed the experimental planning tool for perovskite solarcell synthesis. It allows to create the reuqired synthesis information from precreated templates and links all of these steps together. It provides tool s to efficiently manipulate the templates for parameter vairation. 

One example would be:  
Me as a lab scientis, I want to produce a solar cell using:
1. Standard cleaning
2. A standard spincoated SAM HTL
3. Sloat Die Coating CsMAFA as a absorber layer, where I vary from standard the anti solvent chemicals, and the dropping time of the anti solvent
4. Standard evaporation for C60, BCP as ETLs
5. Standard evaporation for Cu as a back contact

As parameters I want Ethanol, and Anisole as anti solvents and to have 5, 10 ,15 ,20 ,25 seconds as the dropping time of the anti solvent.

Another owuld be:
Me as a lab scientis, I want to produce a solar cell using:
1. Standard cleaning
2. A standard spincoated SAM HTL
3. AlO3 as a Slot Die Coated buffer layer, which is present in one half and absent in the other half of my batch
4. Standard spincoating MaPbI3 as a absorber layer
5. Standard evaporation for C60, BCP as ETLs
6. Standard evaporation for Cu as a back contact

The experimental planning tool is designed to document these plans efficiently provided that the standard processes exist, see: [create_experimental_plan.md](create_experimental_plan.md), [create_standard_sample.md](create_standard_sample.md) and [create_wet_chemical_deposition.md](create_wet_chemical_deposition.md) for more how tos.
