# Wet chemical deposition

This covers `Slot Die Coating`, `Spin Coating`, `Spray Pyrolysis`, `Drop Casting`, `Dip Coating`, and `Inkjet Printing`.


They all share this view:  
![grafik](https://github.com/RoteKekse/nomad-baseclasses/assets/36420750/74df8b02-eb9f-46e9-ac39-c95beb38ef11)

- `samples` refers to the sample or substrate the deposition was performed on
- `solution` refers to the solution/ink used in the deposition
- `layer` referes to the layer type, such as HTL, ETL... and the `layer material name`, which is meant to be the common abbreviation such as MAPbI3, 2PACz,
from this we try to convert it in the correct molecular formula, you can als write the molecular formula yourself.
![grafik](https://github.com/RoteKekse/nomad-baseclasses/assets/36420750/f2fe5f48-e1d2-4cfe-9f39-d3e28ed460b2)
 - `quenching` relates to different types of quenching, e.g. `anti solvent quenching` afer some `spin coating` or `Air knife quenching`after some `slot die coating`, the
specific quenching can be selected from a drop-down menu  ![grafik](https://github.com/RoteKekse/nomad-baseclasses/assets/36420750/c59d9804-f43e-4ffd-b74b-1b143fefd448)
 - `annealing`, information of annealing afterwards
 - `sintering`, information of annealing afterwards
