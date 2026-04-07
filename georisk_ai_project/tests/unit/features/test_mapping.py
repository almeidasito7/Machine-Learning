import pandas as pd
import pytest

from app.features.mapping import map_to_geotechnical

def test_mapping_adds_proxy_columns():
    df = pd.DataFrame({f"feature_{i}": [float(i)] for i in range(1, 129)})

    result = map_to_geotechnical(df)

    assert not result.empty
    assert {"strain_proxy", "pressure_proxy", "displacement_proxy", "instability_proxy"}.issubset(
        result.columns
    )


def test_mapping_raises_without_feature_columns():
    df = pd.DataFrame({"sensor_1": [1.0], "sensor_2": [2.0]})

    with pytest.raises(ValueError):
        map_to_geotechnical(df)
