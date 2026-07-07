select
    nitrogen,
    phosphorus,
    potassium,
    temperature,
    humidity,
    ph,
    rainfall,
    crop_label
from {{ ref('stg_crop_recommendation') }}