import matplotlib.pyplot as plt
import numpy as np


def create_hexagon(radius=1):
    """Create a single hexagon centered at the origin."""
    angles = np.linspace(0, 2 * np.pi, 7)[:-1]  # 6 points
    return np.array([[np.cos(a) * radius, np.sin(a) * radius] for a in angles])


def generate_colored_hexagonal_tiling(radius, layers):
    """Generate a hexagonal tiling with a specific color for each layer."""
    hexagons_by_layer = []

    for layer in range(layers + 1):
        layer_hexagons = []
        for q in range(-layer, layer + 1):
            for r in range(-layer, layer + 1):
                if abs(q + r) <= layer:
                    x_offset = radius * 3 / 2 * q
                    y_offset = radius * np.sqrt(3) * (r + q / 2)
                    layer_hexagons.append(create_hexagon(radius) + [x_offset, y_offset])
        hexagons_by_layer.append(layer_hexagons)

    return hexagons_by_layer


def visualize_colored_hexagonal_tiling(hexagons_by_layer):
    """Visualize the hexagonal tiling with different colors for each layer."""
    plt.figure(figsize=(8, 8))
    colors = plt.cm.viridis(np.linspace(0, 1, len(hexagons_by_layer)))

    for layer_idx, layer_hexagons in enumerate(hexagons_by_layer):
        for hexagon in layer_hexagons:
            plt.fill(hexagon[:, 0], hexagon[:, 1], color=colors[layer_idx], edgecolor='black', linewidth=0.5)

    plt.axis('equal')
    plt.axis('off')
    plt.show()


# Generate the hexagonal tiling with distinct layers and colors
radius = 1
layers = 4  # Change this for more layers
hexagons_by_layer = generate_colored_hexagonal_tiling(radius, layers)

# Visualize the result with distinct colors for each layer
visualize_colored_hexagonal_tiling(hexagons_by_layer)
