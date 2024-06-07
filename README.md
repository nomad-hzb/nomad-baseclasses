# NOMAD base sections for solar cell and electro catalysis research

This is a nomad plugin, see [NOMAD Plugins](https://nomad-lab.eu/prod/v1/staging/docs/plugins.html) on how to use them.

## Documentation
see [docs](https://nomad-hzb.github.io/nomad-baseclasses/)

## Examples
At the heart of this plugin are deposition techniques as they are used  in perovskite solar cells, characterizations of these solar cells and electro chemical techniques using instruments such as a potentionstat.

The `baseclasses` folder contains several nomad schemas for different techniques as they are use at Helmoltz-Zentrum Berlin (HZB). See `docs`for some further explanations.
They can be used to derive application plugins and parsers as here:
- [HZB Solar Cells](https://github.com/RoteKekse/nomad-hysprint)
- [HZB Electro Catalysis](https://github.com/RoteKekse/nomad-chemical-energy)
- [KIT Solar Cells](https://github.com/RoteKekse/nomad-perotf)

See [NOMAD Schemas](https://nomad-lab.eu/prod/v1/staging/docs/howto/customization/basics.html) on documentation how to create nomad schemas. We would recommend to write plugins in Python whcih allows to write custom parser for your lab data.
