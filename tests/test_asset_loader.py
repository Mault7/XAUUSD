from backend.infrastructure.config.asset_loader import AssetConfigLoader


def test_asset_loader_reads_supported_assets() -> None:
    config = AssetConfigLoader("config/assets.yaml").load()

    assert len(config.assets) >= 3
    assert config.assets[0].symbol == "XAUUSD"
    assert config.assets[0].enabled is True
    assert config.assets[0].timeframes[0].value == "D1"
