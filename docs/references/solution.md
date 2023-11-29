# Solution [CHEBI_75958](http://purl.obolibrary.org/obo/CHEBI_75958)

The plane solution lane looks like this:  
![grafik](https://github.com/RoteKekse/nomad-baseclasses/assets/36420750/6adb7972-aece-496b-b56a-7e562d7b55f1)


You can select:
 - `preparation`, information on the preparation information needed, 
 - `solutes`, eg. PbI2
 - `solvents`, eg. Isoprpanol
 - `other solution`, eg. a similar entry to what you are doing right now
 - `additives`, similar to solutes, but with a special purpose
 - `storage`, information on where and for how long the solution was stored
 - `properties`, some properties, like ph value
 - `solution_id`, sometimes a solution is a sample of itself and is characterized in this case

## Preparation
You can set:
- `Atmosphere`, eg. N2, there are some suggestion but you can type what you want
- `Method`, eg. stirring
- `Temperature`,
- `Time`
- `Speed`, for some methods the speed is relevant, if not leave it blank
- `Solven ratio`, this is a free text field, you can fill it as you wish, e.g. 1:3:5 Anisole,Ethanol,IPA  
![grafik](https://github.com/RoteKekse/nomad-baseclasses/assets/36420750/2a6d79d2-527c-4c24-8546-bc70d4c581df)


## Solutes, solvents, additives
They all share the same properties.  
![grafik](https://github.com/RoteKekse/nomad-baseclasses/assets/36420750/c16a2e7a-c4a7-438a-922c-4f07581d12d3)

You can set:
- `Chemical`, `Chemical_2`, you should use `Chemical_2`, since there you directly can set a chemical by name. This will trigger a call to PubChem to fill out the missing information. `Chemical` is used if you would like to reference a specific chemical, which exists somewhere else.
  
![grafik](https://github.com/RoteKekse/nomad-baseclasses/assets/36420750/bbc98802-76d1-48d3-b73b-d24f79417544)
- `Chemical volume`and `Chemical mass` specifiy the amount of the substance in absolute values
- `Concentration mol` and `Concentration mass` specifiy the amount of the substance in relative values
-  `Amount relative`, eg. if one has 3 solvents in ration 1:3:5, you could write 1, 3 and 5 for the respective substances

## Storage
![grafik](https://github.com/RoteKekse/nomad-baseclasses/assets/36420750/247ada93-d3fb-4bc4-9c67-8183174c361b)

You can select:
 - `Start date`, `End date` 
 - `Storage conditions`, eg. Fridge
 - `Temperature`
 - `Atmosphere`, eg. N2, Ar

## Properties
![grafik](https://github.com/RoteKekse/nomad-baseclasses/assets/36420750/0b744311-6f80-4192-a6b7-503a48a8ae78)  
This includes:
- `ph Value`, `final volume` and `final concentration`
