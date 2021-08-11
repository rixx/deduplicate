import click
import vpype as vp
import numpy as np
from vpype import LengthType
from vpype.model import LineCollection
from shapely.geometry import MultiLineString
from tqdm import tqdm


@click.command()
@click.option(
    "-t",
    "--tolerance",
    type=LengthType(),
    default="0.01mm",
    help="Max distance between start and end point to consider a path closed"
    "(default: 0.01mm)",
)
@click.option(
    "-p", "--progress-bar", is_flag=True, default=True, help="Display a progress bar"
)
@vp.layer_processor
def deduplicate(
    lines: LineCollection,
    tolerance: float,
    progress_bar: bool,
) -> vp.Document:
    """
    Remove duplicate lines.

    Args:
        lines: LineCollection input
        tolerance: maximum tolerance to consider 2 lines equal
        progress_bar: flag, display a progress bar if set

    Returns:
        a LineCollection where duplicated lines were removed.
    """

    lc = LineCollection()
    line_arr = np.array([np.array(line) for line in lines.as_mls()])
    mask = np.zeros(len(line_arr), dtype=bool)

    for i, line in enumerate(tqdm(line_arr[:-1], disable=progress_bar)):
        try:
            reshaped = line.reshape(-1, 2, 2)
        except ValueError:
            raise ValueError("Use 'splitall' command before 'deduplicate'.")

        mask[i + 1 :] |= np.all(
            np.isclose(reshaped, line_arr[i + 1 :], atol=tolerance), axis=(1, 2)
        )
        mask[i + 1 :] |= np.all(
            np.isclose(reshaped[:, ::-1, :], line_arr[i + 1 :], atol=tolerance),
            axis=(1, 2),
        )

    line_arr = line_arr[~mask]
    lc.extend(MultiLineString(list(line_arr)))

    return lc


deduplicate.help_group = "Plugins"
