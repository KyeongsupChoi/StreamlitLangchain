"""
3D apartment building visualization using Plotly.

Project role:
  Constructs an interactive 3D building figure highlighting a target floor
  and showing the apartment room layout inside it. Consumed by the valuation
  UI via ``st.plotly_chart()``.
"""

from __future__ import annotations

import plotly.graph_objects as go

FLOOR_HEIGHT = 3.0
WALL_HEIGHT = 2.5
BUILDING_WIDTH = 15.0
BUILDING_DEPTH = 10.0

# Korean room labels for a 2-room apartment layout.
_ROOM_LABELS = {
    "living": "거실",
    "bedroom1": "침실 1",
    "bedroom2": "침실 2",
    "kitchen": "주방",
    "bathroom": "욕실",
}


# -- Public API ---------------------------------------------------------------


def build_building_figure(
    floor: int,
    area_sqm: float,
    property_type: str,
    num_rooms: int = 2,
    total_floors: int = 20,
) -> go.Figure:
    """Build a 3D Plotly figure of an apartment building.

    Args:
        floor: Target floor number (1-indexed).
        area_sqm: Apartment area in square meters.
        property_type: Korean property type string (for future use).
        num_rooms: Number of bedrooms (default 2).
        total_floors: Total floors in the building.

    Returns:
        A ``plotly.graph_objects.Figure`` ready for ``st.plotly_chart()``.
    """
    total_floors = max(total_floors, floor + 2)
    building_height = total_floors * FLOOR_HEIGHT

    fig = go.Figure()

    # Floor slabs
    for f in range(1, total_floors + 1):
        z0 = (f - 1) * FLOOR_HEIGHT
        z1 = z0 + FLOOR_HEIGHT
        is_target = f == floor
        color = "rgba(60,120,216,0.45)" if is_target else "rgba(180,180,180,0.18)"
        name = f"{f}F (대상)" if is_target else f"{f}F"
        fig.add_trace(
            _make_box_mesh(0, 0, z0, BUILDING_WIDTH, BUILDING_DEPTH, z1, color, name)
        )

    # Apartment layout on the target floor
    layout = _compute_apartment_layout(area_sqm, num_rooms)
    apt_x0 = (BUILDING_WIDTH - layout["width"]) / 2
    apt_y0 = (BUILDING_DEPTH - layout["depth"]) / 2
    target_z = (floor - 1) * FLOOR_HEIGHT

    for trace in _make_room_walls(
        layout["rooms"], apt_x0, apt_y0, target_z, WALL_HEIGHT
    ):
        fig.add_trace(trace)

    for trace in _make_room_labels(
        layout["rooms"], apt_x0, apt_y0, target_z, WALL_HEIGHT
    ):
        fig.add_trace(trace)

    # Floor number labels on the building exterior
    for trace in _make_floor_labels(
        total_floors, floor, BUILDING_WIDTH, BUILDING_DEPTH / 2, FLOOR_HEIGHT
    ):
        fig.add_trace(trace)

    # Camera -- isometric 3/4 view, z centered on target floor
    z_center_ratio = (floor - 1) * FLOOR_HEIGHT / building_height
    fig.update_layout(
        scene=dict(
            xaxis=dict(visible=False),
            yaxis=dict(visible=False),
            zaxis=dict(visible=False),
            aspectmode="data",
            camera=dict(
                eye=dict(x=1.8, y=-1.8, z=0.8 + z_center_ratio),
                center=dict(x=0, y=0, z=z_center_ratio * 0.5),
                up=dict(x=0, y=0, z=1),
            ),
        ),
        margin=dict(l=0, r=0, t=30, b=0),
        showlegend=False,
        height=600,
    )

    return fig


# -- Private helpers ----------------------------------------------------------


def _make_box_mesh(
    x0: float,
    y0: float,
    z0: float,
    x1: float,
    y1: float,
    z1: float,
    color: str,
    name: str,
) -> go.Mesh3d:
    """Create a Mesh3d rectangular box from two corner coordinates.

    Args:
        x0, y0, z0: Minimum corner.
        x1, y1, z1: Maximum corner.
        color: RGBA color string.
        name: Trace hover name.

    Returns:
        A ``go.Mesh3d`` trace.
    """
    vertices_x = [x0, x1, x1, x0, x0, x1, x1, x0]
    vertices_y = [y0, y0, y1, y1, y0, y0, y1, y1]
    vertices_z = [z0, z0, z0, z0, z1, z1, z1, z1]

    # 12 triangles (2 per face, 6 faces)
    i = [0, 0, 0, 0, 4, 4, 0, 0, 1, 1, 0, 0]
    j = [1, 2, 1, 5, 5, 6, 3, 7, 2, 6, 4, 7]
    k = [2, 3, 5, 4, 6, 7, 7, 4, 6, 5, 3, 3]

    return go.Mesh3d(
        x=vertices_x,
        y=vertices_y,
        z=vertices_z,
        i=i,
        j=j,
        k=k,
        color=color,
        flatshading=True,
        name=name,
        hoverinfo="name",
    )


def _wall_segment(
    x_start: float,
    y_start: float,
    x_end: float,
    y_end: float,
    z_base: float,
    wall_height: float,
    color: str,
    width: float,
) -> go.Scatter3d:
    """Create a single wall as a 3D line loop (bottom-top-top-bottom).

    Args:
        x_start, y_start: Wall start position (plan view).
        x_end, y_end: Wall end position (plan view).
        z_base: Floor elevation.
        wall_height: Height of the wall.
        color: Line color.
        width: Line width in pixels.

    Returns:
        A ``go.Scatter3d`` trace.
    """
    z_top = z_base + wall_height
    return go.Scatter3d(
        x=[x_start, x_start, x_end, x_end, x_start],
        y=[y_start, y_start, y_end, y_end, y_start],
        z=[z_base, z_top, z_top, z_base, z_base],
        mode="lines",
        line=dict(color=color, width=width),
        hoverinfo="skip",
        showlegend=False,
    )


def _compute_apartment_layout(
    area_sqm: float, num_rooms: int
) -> dict:
    """Compute apartment dimensions and room rectangles.

    The layout follows a common Korean apartment floorplan: living room in
    the front half, bedrooms + kitchen/bath in the back half.

    Args:
        area_sqm: Total apartment area in square meters.
        num_rooms: Number of bedrooms.

    Returns:
        Dict with ``width``, ``depth``, and ``rooms`` list. Each room has
        ``x0``, ``y0``, ``x1``, ``y1`` (relative to apartment origin) and
        ``name`` (Korean label).
    """
    # Scale proportionally from a reference 84 sqm layout.
    scale = (area_sqm / 84.0) ** 0.5
    width = 10.0 * scale
    depth = 8.4 * scale

    half_depth = depth / 2.0
    bed_width = width / 2.0
    kitchen_width = width * 0.65
    bath_width = width - kitchen_width

    rooms = [
        # Front half -- living room spans full width
        {
            "x0": 0,
            "y0": 0,
            "x1": width,
            "y1": half_depth,
            "name": _ROOM_LABELS["living"],
        },
        # Back-left -- bedroom 1
        {
            "x0": 0,
            "y0": half_depth,
            "x1": bed_width,
            "y1": depth,
            "name": _ROOM_LABELS["bedroom1"],
        },
    ]

    if num_rooms >= 2:
        # Back-right -- bedroom 2
        rooms.append(
            {
                "x0": bed_width,
                "y0": half_depth,
                "x1": width,
                "y1": depth,
                "name": _ROOM_LABELS["bedroom2"],
            }
        )

    # Kitchen and bathroom sit above the back bedrooms (top strip)
    top_strip_y0 = depth
    top_strip_y1 = depth + half_depth * 0.5
    rooms.append(
        {
            "x0": 0,
            "y0": top_strip_y0,
            "x1": kitchen_width,
            "y1": top_strip_y1,
            "name": _ROOM_LABELS["kitchen"],
        }
    )
    rooms.append(
        {
            "x0": kitchen_width,
            "y0": top_strip_y0,
            "x1": width,
            "y1": top_strip_y1,
            "name": _ROOM_LABELS["bathroom"],
        }
    )

    # Recalculate total depth to include top strip
    total_depth = top_strip_y1

    return {"width": width, "depth": total_depth, "rooms": rooms}


def _make_room_walls(
    rooms: list[dict],
    apt_x0: float,
    apt_y0: float,
    z_base: float,
    wall_height: float,
) -> list[go.Scatter3d]:
    """Generate wall traces for all rooms.

    Args:
        rooms: Room dicts from ``_compute_apartment_layout``.
        apt_x0: Apartment X offset within the building.
        apt_y0: Apartment Y offset within the building.
        z_base: Floor elevation.
        wall_height: Wall height in meters.

    Returns:
        List of ``go.Scatter3d`` wall traces.
    """
    traces: list[go.Scatter3d] = []
    wall_color = "rgb(50,50,50)"

    for room in rooms:
        rx0 = apt_x0 + room["x0"]
        ry0 = apt_y0 + room["y0"]
        rx1 = apt_x0 + room["x1"]
        ry1 = apt_y0 + room["y1"]

        # Four walls per room (overlapping edges are fine visually)
        edges = [
            (rx0, ry0, rx1, ry0),
            (rx1, ry0, rx1, ry1),
            (rx1, ry1, rx0, ry1),
            (rx0, ry1, rx0, ry0),
        ]
        for xs, ys, xe, ye in edges:
            traces.append(
                _wall_segment(xs, ys, xe, ye, z_base, wall_height, wall_color, 3)
            )

    return traces


def _make_room_labels(
    rooms: list[dict],
    apt_x0: float,
    apt_y0: float,
    z_base: float,
    wall_height: float,
) -> list[go.Scatter3d]:
    """Generate text labels at the center of each room.

    Args:
        rooms: Room dicts from ``_compute_apartment_layout``.
        apt_x0: Apartment X offset within the building.
        apt_y0: Apartment Y offset within the building.
        z_base: Floor elevation.
        wall_height: Wall height in meters (label placed at mid-height).

    Returns:
        List of ``go.Scatter3d`` text traces.
    """
    xs, ys, zs, texts = [], [], [], []
    label_z = z_base + wall_height * 0.5

    for room in rooms:
        cx = apt_x0 + (room["x0"] + room["x1"]) / 2
        cy = apt_y0 + (room["y0"] + room["y1"]) / 2
        xs.append(cx)
        ys.append(cy)
        zs.append(label_z)
        texts.append(room["name"])

    return [
        go.Scatter3d(
            x=xs,
            y=ys,
            z=zs,
            mode="text",
            text=texts,
            textfont=dict(size=12, color="rgb(30,30,30)"),
            hoverinfo="skip",
            showlegend=False,
        )
    ]


def _make_floor_labels(
    total_floors: int,
    target_floor: int,
    building_x1: float,
    building_y_mid: float,
    floor_height: float,
) -> list[go.Scatter3d]:
    """Generate floor number labels on the building exterior.

    Labels are placed for the 1st floor, target floor, and top floor.

    Args:
        total_floors: Total number of floors.
        target_floor: The highlighted floor number.
        building_x1: X position of the building right edge.
        building_y_mid: Y midpoint of the building.
        floor_height: Height per floor in meters.

    Returns:
        List of ``go.Scatter3d`` text traces.
    """
    label_x = building_x1 + 1.5
    floors_to_label = sorted({1, target_floor, total_floors})

    xs, ys, zs, texts = [], [], [], []
    for f in floors_to_label:
        xs.append(label_x)
        ys.append(building_y_mid)
        zs.append((f - 0.5) * floor_height)
        label = f"{f}F"
        if f == target_floor:
            label += " <--"
        texts.append(label)

    return [
        go.Scatter3d(
            x=xs,
            y=ys,
            z=zs,
            mode="text",
            text=texts,
            textfont=dict(size=11, color="rgb(60,60,60)"),
            hoverinfo="skip",
            showlegend=False,
        )
    ]
