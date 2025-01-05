import matplotlib.pyplot as plt
import numpy as np
from shapely.geometry import Polygon
from shapely.affinity import translate


def create_regular_polygon(sides=5, radius=1):
    """Creates a regular polygon with a specified number of sides."""
    angles = np.linspace(0, 2 * np.pi, sides, endpoint=False)
    points = [(np.cos(a) * radius, np.sin(a) * radius) for a in angles]
    return Polygon(points).buffer(0)  # Ensure valid geometry


def generate_heesch_tiling_fixed(polygon, max_layers):
    """Generates a tiling for the given polygon with fixed logic."""
    tiling = [polygon]
    layer_polygons = [polygon]
    layer_distance = polygon.bounds[2] - polygon.bounds[0]  # Approximate diameter

    for layer in range(1, max_layers + 1):
        new_layer = []
        for poly in layer_polygons:
            # Generate snug positions (around edges)
            for angle in np.linspace(0, 2 * np.pi, len(poly.exterior.coords) - 1, endpoint=False):
                x_offset = np.cos(angle) * layer_distance
                y_offset = np.sin(angle) * layer_distance
                translated = translate(poly, xoff=x_offset, yoff=y_offset).buffer(0)

                if translated.is_valid and all(not translated.intersects(existing) for existing in tiling):
                    new_layer.append(translated)

        if not new_layer:
            print(f"Heesch number: {layer - 1}")
            return tiling

        tiling.extend(new_layer)
        layer_polygons = new_layer

        # Visualize the current layer
        visualize_tiling(tiling, title=f"Layer {layer}")

    print(f"Heesch number exceeds {max_layers}")
    return tiling


def visualize_tiling(tiling, title="Tiling Visualization"):
    """Visualizes the tiling at the current stage."""
    plt.figure(figsize=(8, 8))
    for polygon in tiling:
        x, y = polygon.exterior.xy
        plt.fill(x, y, alpha=0.5, edgecolor='black')
    plt.title(title)
    plt.gca().set_aspect('equal')
    plt.show()


# Create a regular pentagon (change `sides` to test different shapes)
base_polygon = create_regular_polygon(sides=5, radius=1)  # Change sides to other numbers for different shapes

# Attempt to generate a Heesch tiling with more than 6 layers
generate_heesch_tiling_fixed(base_polygon, max_layers=10)
