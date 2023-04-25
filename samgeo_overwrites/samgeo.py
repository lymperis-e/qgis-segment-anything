from samgeo import SamGeo
import rasterio
import cv2
from samgeo.common import calculate_sample_grid, read_block, write_block, chw_to_hwc

# Overwrite the tiff_to_tiff function:
# Iterate over the sample grid rather than
# tqdm(sample_grid)

def tiff_to_tiff(
    src_fp,
    dst_fp,
    func,
    data_to_rgb=chw_to_hwc,
    sample_size=(512, 512),
    sample_resize=None,
    bound=128,
):
    with rasterio.open(src_fp) as src:
        profile = src.profile

        # Computer blocks
        rh, rw = profile['height'], profile['width']
        sh, sw = sample_size
        bound = bound

        resize_hw = sample_resize

        sample_grid = calculate_sample_grid(
            raster_h=rh, raster_w=rw, sample_h=sh, sample_w=sw, bound=bound
        )
        # set 1 channel uint8 output
        profile['count'] = 1
        profile['dtype'] = 'uint8'

        with rasterio.open(dst_fp, 'w', **profile) as dst:
            for b in sample_grid:
                r = read_block(src, **b)

                uint8_rgb_in = data_to_rgb(r)
                orig_size = uint8_rgb_in.shape[:2]
                if resize_hw is not None:
                    uint8_rgb_in = cv2.resize(
                        uint8_rgb_in, resize_hw, interpolation=cv2.INTER_LINEAR
                    )

                # Do something
                uin8_out = func(uint8_rgb_in)

                if resize_hw is not None:
                    uin8_out = cv2.resize(
                        uin8_out, orig_size, interpolation=cv2.INTER_NEAREST
                    )
                # Zero channel, because
                write_block(dst, uin8_out, **b)



class SamGeoMod(SamGeo):
    
    def generate(self, in_path, out_path, **kwargs):
        """
        **Overwriten**.
        Segment the input image and save the result to the output path.

        Args:
            in_path (str): The path to the input image.
            out_path (str): The path to the output image.
        """

        return tiff_to_tiff(in_path, out_path, self, **kwargs)