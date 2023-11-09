# Solution [CHEBI_75958](http://purl.obolibrary.org/obo/CHEBI_75958)

The plane solution lane looks like this:
![grafik](https://github.com/RoteKekse/nomad-baseclasses/assets/36420750/587aeeed-acf0-4a13-8f5e-f1181fad8796)

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
![grafik](https://github.com/RoteKekse/nomad-baseclasses/assets/36420750/e638b4c2-e2aa-4993-bd49-4ae1d80b4b6d)


## Solutes, solvents, additives
They all share the same properties. 
![grafik](https://github.com/RoteKekse/nomad-baseclasses/assets/36420750/b3985bef-b0ae-42ce-a719-1400ff03cb4d)
You can set:
- `Chemical`, `Chemical_2`, you should use `Chemical_2`, since there you directly can set a chemical by name. This will trigger a call to PubChem to fill out the missing information. `Chemical` is used if you would like to reference a specific chemical, which exists somewhere else. ![grafik](https://github.com/RoteKekse/nomad-baseclasses/assets/36420750/24128720-0720-407d-8371-17e212901fac)
- `Chemical volume`and `Chemical mass` specifiy the amount of the substance in absolute values
- `Concentration mol` and `Concentration mass` specifiy the amount of the substance in relative values
-  `Amount relative`, eg. if one has 3 solvents in ration 1:3:5, you could write 1, 3 and 5 for the respective substances

## Storage
![grafik](https://github.com/RoteKekse/nomad-baseclasses/assets/36420750/899a7ff1-ab1e-427f-b39a-c8fe8406bb53)
You can select:
 - `Start date`, `End date` 
 - `Storage conditions`, eg. Fridge
 - `Temperature`
 - `Atmosphere`, eg. N2, Ar
