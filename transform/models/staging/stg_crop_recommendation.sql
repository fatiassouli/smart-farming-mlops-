select
    cast(n as double)             as nitrogen,
    cast(p as double)              as phosphorus,
    cast(k as double)              as potassium,
    cast(temperature as double)    as temperature,
    cast(humidity as double)       as humidity,
    cast(ph as double)             as ph,
    cast(rainfall as double)       as rainfall,
    lower(trim(label))             as crop_label
from {{ source('raw', 'crop_recommendation') }}
where n is not null
  and label is not null