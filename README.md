# CazyCrawler

## run

`docker-compose up`

## Docker

- output directory is `/output` (command in Docker uses `-o /output/cazy.jsonlines)
- cache directory `/httpcache`
- **Note**: both `output` and `httpcache` are gitignored because they are mapped to Docker when running in the project
  directory

## scrapy config

- cache is enabled
- cache directory is confiured based on ENV var `TARGET`: if `docker` -> `/httpcache`, else local default path
    - `HTTPCACHE_EXPIRATION_SECS` is currently `0`, meaning cache is never cleaned
- autothrottle is enabled
    - start delay is set to 0
