from pydantic import BaseModel, ConfigDict, Field

_EXAMPLE = {
    "N": 90,
    "P": 42,
    "K": 43,
    "temperature": 20.87,
    "humidity": 82.0,
    "ph": 6.5,
    "rainfall": 202.9,
}


class SoilClimateFeatures(BaseModel):
    """
    Conditions pédoclimatiques utilisées par les DEUX modèles
    (classification et régression), conformément à mlops/model_loader.py
    (prepare_features).
    """

    model_config = ConfigDict(json_schema_extra={"example": _EXAMPLE})

    N: float = Field(..., description="Teneur en azote du sol", ge=0, examples=[90])
    P: float = Field(..., description="Teneur en phosphore du sol", ge=0, examples=[42])
    K: float = Field(..., description="Teneur en potassium du sol", ge=0, examples=[43])
    temperature: float = Field(..., description="Température en °C", examples=[20.87])
    humidity: float = Field(..., description="Humidité relative en %", ge=0, le=100, examples=[82.0])
    ph: float = Field(..., description="pH du sol", ge=0, le=14, examples=[6.5])
    rainfall: float = Field(..., description="Précipitations en mm", ge=0, examples=[202.9])
