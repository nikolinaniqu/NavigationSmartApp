from pyproj import Transformer
import pandas as pd
haltestellen = pd.read_csv("ZVV_HALTESTELLEN_P.csv")
# EPSG:2056 (LV95) → EPSG:4326 (WGS84)
transformer = Transformer.from_crs("EPSG:2056", "EPSG:4326", always_xy=True)

haltestellen[["lon", "lat"]] = haltestellen.apply(
    lambda row: transformer.transform(row["E"], row["N"]),
    axis=1, result_type="expand")
haltestellen.to_csv("ZVV_HALTESTELLEN_P_wgs84.csv", index=False, encoding="utf-8")

print("Datei gespeichert: ZVV_HALTESTELLEN_P_wgs84.csv")
