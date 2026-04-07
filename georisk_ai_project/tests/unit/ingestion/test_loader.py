import pandas as pd
import pytest

from app.ingestion.loader import load_dataset


class TestLoader:

    def test_should_load_dataset_successfully(self, tmp_path, monkeypatch):
        data = pd.DataFrame({"feature_1": [1.0, 2.0], "feature_2": [3.0, 4.0]})

        train_dir = tmp_path / "train"
        train_dir.mkdir(parents=True, exist_ok=True)

        file_path = train_dir / "dataset_merged.csv"
        data.to_csv(file_path, index=False)

        monkeypatch.setattr("app.core.config.settings.data_dir", tmp_path)

        df = load_dataset(dataset_type="train")

        assert not df.empty
        assert list(df.columns) == ["feature_1", "feature_2"]

    def test_should_raise_error_when_file_not_found(self, tmp_path, monkeypatch):
        monkeypatch.setattr("app.core.config.settings.data_dir", tmp_path)

        with pytest.raises(FileNotFoundError):
            load_dataset(dataset_type="train")

    def test_should_raise_error_when_dataset_is_empty(self, tmp_path, monkeypatch):
        train_dir = tmp_path / "train"
        train_dir.mkdir(parents=True, exist_ok=True)

        file_path = train_dir / "dataset_merged.csv"
        pd.DataFrame().to_csv(file_path, index=False)

        monkeypatch.setattr("app.core.config.settings.data_dir", tmp_path)

        with pytest.raises(ValueError):
            load_dataset(dataset_type="train")

    def test_should_raise_error_for_invalid_dataset_type(self):
        with pytest.raises(ValueError):
            load_dataset(dataset_type="invalid")
