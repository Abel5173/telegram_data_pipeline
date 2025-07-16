from dagster import asset

# Dummy asset just for startup testing
@asset
def dummy_asset():
    return "Hello from Dagster!"

# Export assets
all_assets = [dummy_asset]
