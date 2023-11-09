# Upload measurement

If you created an experimental plan and samples with ids (see: [create_experimental_plan.md](create_experimental_plan.md)) you can then take these ids to annotate your measurements.
Currently we have classes for `JV`, `EQE`, `PL`, `UVvis`, `Aging tests`, `trSPV`, simple `XRD` , some Potentiostat techniques.

For `JV`, `EQE`, `PL`, `UVvis`, `trSPV` at `HySprint` at HZB we have the following logic:
Name your file:
`<id>.<notes>.<technique>.<file_type>` please note the periods in the name!
eg:
`HZB_MiGo_20231109_BatchX_3_0.after_3_days.jv.txt`

The first part is the id, then you can put some individual note, then there is the type currently at `HySprint` we have `eqe`, `jv`, `pl`, `hy`, `spv` 
as possible techniques see also [Hysprint Parser](https://github.com/RoteKekse/nomad-hysprint-parser).

If you drag and drop these files (multiple at once possible) in your upload:   
![grafik](https://github.com/RoteKekse/nomad-baseclasses/assets/36420750/495fdb2e-4dad-42f0-853c-fef3a6a4cd03)

It automatically creates the respective nomad entry (eg. `HySprint_JVmeasurement`), links it to the corresponding sampleand puts the note int he comment.
