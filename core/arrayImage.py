from osgeo import gdal
import numpy as np

class ArrayImage:
    """
    Converts a raster image to a numpy array representation
    """

    def __init__(self, image_path: str):
        self.image_path = image_path

    def getArray(self, single_band: bool = False) -> np.ndarray:

        raster = gdal.Open(self.image_path)

        if single_band:
            band = raster.GetRasterBand(1)  # use the first band
            band_data = band.ReadAsArray().astype(np.uint8)
            raster_data = np.stack([band_data, band_data, band_data], axis=2)

        else:
            band_data = list()
            for i in range(1, raster.RasterCount + 1):
                band = raster.GetRasterBand(i)
                band_data.append(band.ReadAsArray().astype(np.uint8))
            raster_data = np.stack(band_data, axis=2)

        return raster_data
