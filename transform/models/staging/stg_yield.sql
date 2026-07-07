select
    trim("Area")             as area,
    trim("Item")              as item,
    cast("Year" as integer)   as year,
    cast("Value" as double)   as yield_hg_ha
from {{ source('raw', 'yield') }}
where "Element" = 'Yield'
  and "Value" is not null