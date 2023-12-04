# Tutorial on solar cells

This tutorial covers the efficient documentation of the synthesis of a batch of solarcells following a standard protocol with some parameter variation, linking 
characterizations to the finished devices (here JV data) and accessing this data through python using jupyter and nomads API.

## Synthesis
Create an experimental plan (see: [create_experimental_plan.md](../how_to/create_experimental_plan.md) for a how to guide). This could then look like this:  
![grafik](https://github.com/RoteKekse/nomad-baseclasses/assets/36420750/ba390101-8c28-44ab-a628-724a6d7a7b0e)

In this case we used standard cleaning, and some variations in the deposition techniques, in this case the anti-solvent dropping time.


## Measurement
Then after measuring the devices you can name the files based on the ids given from your synthesis, eg. `HZB_MiGo_20231005_Batch1_0_0.1.1.jv.txt` 
(see: [upload_measurement.md](../how_to/upload_measurement.md). Note that the id is build from the id from the experimental plan in the synthesis, this sample is the first sample
in the first subbatch.

When you drag and drop your measurement file, nomad processes the file and creates a nomad JV entry:  
![grafik](https://github.com/RoteKekse/nomad-baseclasses/assets/36420750/295fa750-bac7-469a-bde5-b292081a31d0)

After that you can browse your upload [browse_your_upload.md](../how_to/browse_your_upload.md). You can select the `Solar cell` view/app, which could look like this:  
![grafik](https://github.com/RoteKekse/nomad-baseclasses/assets/36420750/5710f364-6d89-438e-a5d5-3a98ac14d2fa)


## Analysis in jupyter
Open the jupyter hub from nomad, see: [North Tools Nomad](https://nomad-lab.eu/prod/v1/staging/docs/data/north.html). This could look like this:

![grafik](https://github.com/RoteKekse/nomad-baseclasses/assets/36420750/1beb8ef9-679f-40eb-a90d-a5a464d235a2)


Here we provide custom functions to join the data in nomad together to plot data from synthesis and measurements together. In this way we can group the anti-solvent dropping time from
before together and create box plots over the respective JV data which was measured.
