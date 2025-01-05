import matplotlib.pyplot as plt
import numpy as np


def create_hexagon(radius=1):
    """Create a single hexagon centered at the origin."""
    angles = np.linspace(0, 2 * np.pi, 7)[:-1]  # 6 points
    return np.array([[np.cos(a) * radius, np.sin(a) * radius] for a in angles])


def generate_colored_hexagonal_tiling(radius, layers):
    """Generate a hexagonal tiling with specific color handling for each layer."""
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


def visualize_layer_by_layer_with_color(hexagons_by_layer):
    """Visualize the process of adding each layer step by step, only coloring new layers."""
    plt.figure(figsize=(8, 8))
    colors = plt.cm.viridis(np.linspace(0, 1, len(hexagons_by_layer)))

    for layer_idx, layer_hexagons in enumerate(hexagons_by_layer):
        # Draw previous layers
        for prev_layer_idx in range(layer_idx):
            for hexagon in hexagons_by_layer[prev_layer_idx]:
                plt.fill(hexagon[:, 0], hexagon[:, 1], color=colors[prev_layer_idx], edgecolor='black', linewidth=0.5)
        # Draw the current layer with a new color
        for hexagon in layer_hexagons:
            plt.fill(hexagon[:, 0], hexagon[:, 1], color=colors[layer_idx], edgecolor='black', linewidth=0.5)

        plt.axis('equal')
        plt.axis('off')
        plt.title(f"Layer {layer_idx + 1}")
        plt.show()


# Parameters for the tiling
radius = 1
layers = 5  # Number of layers to generate

# Generate the hexagonal tiling
hexagons_by_layer = generate_colored_hexagonal_tiling(radius, layers)

# Visualize the result layer by layer
visualize_layer_by_layer_with_color(hexagons_by_layer)
