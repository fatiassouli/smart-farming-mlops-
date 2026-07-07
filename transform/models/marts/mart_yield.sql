select
    area as country,
    item as crop,
    year,
    yield_hg_ha,
    round(yield_hg_ha / 10000.0, 3) as yield_tonnes_per_ha
from {{ ref('stg_yield') }}