select
    nitrogen,
    phosphorus,
    potassium,
    temperature,
    humidity,
    ph,
    rainfall,
    crop_label,
  
    nitrogen + phosphorus + potassium as npk_total,
    nitrogen / (phosphorus + 1e-6) as np_ratio,
    nitrogen / (potassium + 1e-6) as nk_ratio,
    (temperature * humidity) / 100 as heat_humidity,
    rainfall * temperature as rain_temp
from {{ ref('stg_crop_recommendation') }}