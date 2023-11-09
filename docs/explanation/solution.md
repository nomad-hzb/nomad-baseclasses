![grafik](https://github.com/RoteKekse/nomad-baseclasses/assets/36420750/35f0cb59-eb38-4087-9808-5c479118292b)# Solution [CHEBI_75958](http://purl.obolibrary.org/obo/CHEBI_75958)

The plane solution lane looks like this:
![grafik](https://github.com/RoteKekse/nomad-hysprint/assets/36420750/436d0e8e-6362-4919-8ae8-81b60f213e56)

You can select:
 - `preparation`, information on the preparation information needed, 
 - `solutes`, eg. PbI2
 - `solvents`, eg. Isoprpanol
 - `other solutiion`, eg. a similar entry to what you are doing right now
 - `additives`, similar to solutes, but with a special purpose
 - `storage`, information on where and for how long the solution was stored
 - `properties`, some properties, like ph value
 - `solution_id`, some times a solution is a sample of itself and is characterized in this case

## Preparation
You can set:
- `Atmosphere`, eg. N2, there are some suggestion but you can type what you want
- `Method`, eg. stirring
- `Temperature`,
- `Time`
- `Speed`, for some methods the speed is relevant, if not leaveit blank
- `Solven ratio`, this is a free text field, you can fill it as you wish, e.g. 1:3:5 Anisole,Ethanol,IPA
![grafik](https://github.com/RoteKekse/nomad-hysprint/assets/36420750/b98e621c-dbd5-469f-ab0f-46d2c3e75c49)

## Solutes, solvents, additives
They all share the same properties. ![grafik](https://github.com/RoteKekse/nomad-baseclasses/assets/36420750/6c4f6ac0-915e-40ab-8fcb-6681dc33d5b3)
You can set:
- `Chemical`, `Chemical_2`, you should use `Chemical_2`, since there you directly can set a chemical by name. This will trigger a call to PubChem to fill out the missing information. `Chemical` is used if you would like to reference a specific chemical, which exists somewhere else. ![grafik](https://github.com/RoteKekse/nomad-baseclasses/assets/36420750/5a24d0ae-3765-49e4-9d19-1865133043a2)
- `Chemical volume`and `Chemical mass` specifiy the amount of the substance in absolute values
- `Concentration mol` and `Concentration mass` specifiy the amount of the substance in relative values
-  `Amount relative`, eg. if one has 3 solvents in ration 1:3:5, you could write 1, 3 and 5 for the respective substances


