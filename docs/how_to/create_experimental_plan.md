[list_of_ids_plan HZB_MiGo_20231109_BatchX.csv](https://github.com/RoteKekse/nomad-baseclasses/files/13306666/list_of_ids_plan.HZB_MiGo_20231109_BatchX.csv)
# Create an experimental plan
The experimental plan is the core tool to document synthesis.
You should at least have created some processes, eg. `wet chemical depositions` as in [create_wet_chemical_deposition.md](create_wet_chemical_deposition.md), or cleaning or evaporation.
Or you create a `standard sample` as in [create_standard_sample.md](create_standard_sample.md)

Follow the first  steps in [create_entry.md](create_entry.md).
 
1. Select `HySprint_ExperimentalPlan` as a `built-in schema`.

2. If you have select a `standard sample` by reference (click pen symbol) and click `save`. This loads the process and information from the `standard sample`in to the experimental plan.
   ![grafik](https://github.com/RoteKekse/nomad-baseclasses/assets/36420750/f9ffca61-443e-4cbc-abec-ab2a9729e754)

3. Enter the `number of substrates` and the `substrates per subbatch`. It is important that the number `substrates per subbatch` devides the number `number of substrates`. In a parameter variation there is room for `number of substrates` devided by `substrates per subbatch` different variations. So if you hae 8 substrates and 2 substrates per subbatch you have 8/2=4 different parameter variations. Each variation will be applied to the whole subbatch.

4. You can now manual change or create the information in `solar cell properties` and `plan`. `plan` captures the steps planned for the synthesis by reference, if you added a `standard sample` you can change the references.

5. Parameter variation: for each step you can add some parameter variation. Select a `step` and then add the subsection `parameters` or click the `vary parameters`checkbox. If you added a `parameters`subsection select a parameter from the drop down menue, eg, `quenching/anti_solvent_dropping_time`.  
   ![grafik](https://github.com/RoteKekse/nomad-baseclasses/assets/36420750/50f193c5-d622-4b26-a875-6997ed3b335d)  
   The unit is filled automatically but can be changed.
   See also [set_parameters_in_experimental_plan.md](https://github.com/nomad-hzb/nomad-baseclasses/blob/main/docs/how_to/set_parameters_in_experimental_plan.md) to see how to select the correct parameters.

7. Once you entered all variations click the `LOAD STANDARD PROCESSES` button. This copies the information from the template from the reference (or from the `standard sample`) and the parameters subsection into the step
   ![grafik](https://github.com/RoteKekse/nomad-baseclasses/assets/36420750/95818665-3e7c-4f2e-b713-bf2ff0939382)
   As you see, there are now 8/2=4 `batch processes`. 

8. Now you can manually change further the parameter by navigating into the `batch process`. The `present` checkbox allows you to skip a process for a specific subbatch, just uncheck it if you for example use a buffer layer. `!ATTENTION:!` all manually changed data will get lost when pressing the `LOAD STANDARD PROCESSES` button again, this will load the template and parameter variation again as specified before.

9. If you are happy with the plan click the `CREATE SAMPLES AND PROCESSES` button. This creates all samples, batches, ids and processes.

10.  This also creates an html overview which you can find in `batch_plan_pdf`. You can download it and open and print it with your browser. This is a summary of all what nomad knows about your experimental plan as well as a reference to the main batch.

11. Finally, either navigate to the explore view (see: [browse_your_upload.md](browse_your_upload.md)) and select `HySprint_Batch` and select the one with the ID defined in the experimental plan or follow the reference in the experimental plan.
    ![grafik](https://github.com/RoteKekse/nomad-baseclasses/assets/36420750/4e2746a8-92be-47f2-8a0e-028f7f77c2e3) 

12. Click the `EXPORT BATCH IDS` button and then download the `csv_export_file`.
    ![grafik](https://github.com/RoteKekse/nomad-baseclasses/assets/36420750/a892651e-c959-4cb5-b4e2-549a7bcecc86)

This looks like this:

|0                           |1                                |2                    |3                              |4                       |5|
|------|----------------------------|---------------------------------|---------------------|-------------------------------|------------------------|
|0     |HZB_MiGo_20231109_BatchX_0_0|Solution and UV standard cleaning|Sam 2PACz spincoating|CsMAFA perovscite spincoating 1|Evaporation C60, BCP, Cu|
|1     |HZB_MiGo_20231109_BatchX_0_1|Solution and UV standard cleaning|Sam 2PACz spincoating|CsMAFA perovscite spincoating 1|Evaporation C60, BCP, Cu|
|2     |HZB_MiGo_20231109_BatchX_1_0|Solution and UV standard cleaning|Sam 2PACz spincoating|CsMAFA perovscite spincoating 2|Evaporation C60, BCP, Cu|
|3     |HZB_MiGo_20231109_BatchX_1_1|Solution and UV standard cleaning|Sam 2PACz spincoating|CsMAFA perovscite spincoating 2|Evaporation C60, BCP, Cu|
|4     |HZB_MiGo_20231109_BatchX_2_0|Solution and UV standard cleaning|Sam 2PACz spincoating|CsMAFA perovscite spincoating 3|Evaporation C60, BCP, Cu|
|5     |HZB_MiGo_20231109_BatchX_2_1|Solution and UV standard cleaning|Sam 2PACz spincoating|CsMAFA perovscite spincoating 3|Evaporation C60, BCP, Cu|
|6     |HZB_MiGo_20231109_BatchX_3_0|Solution and UV standard cleaning|Sam 2PACz spincoating|CsMAFA perovscite spincoating 4|Evaporation C60, BCP, Cu|
|7     |HZB_MiGo_20231109_BatchX_3_1|Solution and UV standard cleaning|Sam 2PACz spincoating|CsMAFA perovscite spincoating 4|Evaporation C60, BCP, Cu|

This gives you the ids for the respective parameter variation, which you can then copy into your measurement data (see: [upload_measurement.md](upload_measurement.md))


