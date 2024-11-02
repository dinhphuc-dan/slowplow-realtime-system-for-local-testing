This repo inspired by https://github.com/wirelessr/snowplow-pipeline/blob/main/events-processor/app.py and https://github.com/edbullen/DockerSpark245
I am trying build a complete snow-plow stack using
- a tracker file to generate data
- snowplow stream collector to get data from tracker then will be enrich by snowplow-enrichment default. The output data will be go to Spark for some customized transfromation
- after basic transformation, data will be written to a Postgres table
- for reaching the real-time, I use kafka 
