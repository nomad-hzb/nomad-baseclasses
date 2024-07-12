# Setting Solution Parameter in experimental plan
We will discuss the logic behind accessing the parameters of a solution in a wet chemical deposition in Nomad.

The idea is that we create a path to uniquely identify a parameter based on the names in nomad.

Every solution parameter will start with accessing the solution:  
`solution/` which references the solution section. In theory there could be multiple solutions be used, to access the first we need to write `/0/`. To access the second `/1/`, and so on...

The first parameter is the solution_volume:  
`solution/0/solution_volume`

Keep in mind that the name of the parameter in nomad is usually  the name in lower cases with spaces substituted with and underscore `_`

The next level is the solution itself:
`solution/0/solution_details`

Here it is important to use solution_details, this refers to the details  of the specific  solution.

We can the choose between `additive`, `solvent`, `solute` to select the next level, there we then can select the parameters like this:  
Keep in mind that we again can have multiple solutes and solvents.  
`solution/0/solution_details/solute/0/concentration_mol`  
`solution/0/solution_details/solute/0/chemical_volume`   
`solution/0/solution_details/solute/0/chemical_mass`   
`solution/0/solution_details/solute/0/concentration_mass`  

replacing solute with `additive` or `solvent` gives the respective other sections.  

Now the whole procedure is recursive for `other_solution`.  
E.g. accessing the concentration of an solute of another solution would be:

`solution/0/solution_details/other_solution/0/solution_details/solute/0/concentration_mol`

If the path is correct and the unit field is empty it should be filled with a default unit. E.g. `mole / milliliter`


If you want to change the chemical the name is actual `chemical_2`, so to change the chemical of the first solute in the first solution of a deposition would be:  
`solution/0/solution_details/solute/0/chemical_2/name`  
