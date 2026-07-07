select
    area as country,
    item as crop,
    year,
    year - min(year) over () as year_norm,
    yield_hg_ha,
    round(yield_hg_ha / 10000.0, 3) as yield_tonnes_per_ha,
    ln(1 + yield_hg_ha) as log_yield
from {{ ref('stg_yield') }}