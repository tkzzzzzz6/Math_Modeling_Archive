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



def evaluate_complexity(hexagons_by_layer):
    """Evaluate the complexity of the hexagonal tiling by calculating the number of hexagons per layer."""
    complexities = [len(layer) for layer in hexagons_by_layer]
    layers = list(range(1, len(hexagons_by_layer) + 1))
    return layers, complexities


def visualize_complexity(layers, complexities):
    """Visualize the complexity of the tiling as a line plot."""
    plt.figure(figsize=(8, 6))
    plt.plot(layers, complexities, 'o-', label="Actual Complexity", linewidth=2, markersize=8)
    plt.title("Complexity of Hexagonal Tiling")
    plt.xlabel("Layer Number")
    plt.ylabel("Number of Hexagons")
    plt.grid(True, linestyle='--', alpha=0.7)
    plt.xticks(layers)
    plt.legend()
    plt.show()


def evaluate_optimization_limit(hexagons_by_layer):
    """Evaluate and estimate the upper limit of complexity growth for the tiling."""
    layers, complexities = evaluate_complexity(hexagons_by_layer)

    # Fit a quadratic model to estimate growth
    coefficients = np.polyfit(layers, complexities, 2)
    growth_model = np.poly1d(coefficients)

    # Generate values for visualization
    layers_extended = np.linspace(1, len(layers) + 5, 100)  # Extend beyond current layers
    estimated_complexities = growth_model(layers_extended)

    return layers, complexities, layers_extended, estimated_complexities, coefficients


def visualize_optimization_limit(layers, complexities, layers_extended, estimated_complexities):
    """Visualize the optimization limit and complexity growth."""
    plt.figure(figsize=(8, 6))
    plt.plot(layers, complexities, 'o-', label="Actual Complexity", linewidth=2, markersize=8)
    plt.plot(layers_extended, estimated_complexities, '--', label="Estimated Growth (Quadratic)", linewidth=2)
    plt.title("Hexagonal Tiling Optimization Limit")
    plt.xlabel("Layer Number")
    plt.ylabel("Number of Hexagons")
    plt.legend()
    plt.grid(True, linestyle='--', alpha=0.7)
    plt.show()


# Parameters for the tiling
radius = 1
layers = 5  # Number of layers to generate

# Generate the hexagonal tiling
hexagons_by_layer = generate_colored_hexagonal_tiling(radius, layers)

# Visualize the result layer by layer
visualize_layer_by_layer_with_color(hexagons_by_layer)

# Evaluate and visualize the complexity of the tiling
layers, complexities = evaluate_complexity(hexagons_by_layer)
visualize_complexity(layers, complexities)

# Evaluate and visualize the optimization limit
layers, complexities, layers_extended, estimated_complexities, coefficients = evaluate_optimization_limit(hexagons_by_layer)
visualize_optimization_limit(layers, complexities, layers_extended, estimated_complexities)
