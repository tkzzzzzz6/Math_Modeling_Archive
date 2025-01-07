import matplotlib.pyplot as plt
import numpy as np
import matplotlib.patches as patches

def create_hexagon(radius=1):
    """Create a single hexagon centered at the origin."""
    angles = np.linspace(0, 2 * np.pi, 7)[:-1]  # 6 points
    return np.array([[np.cos(a) * radius, np.sin(a) * radius] for a in angles])


def generate_colored_hexagonal_tiling(radius, layers):
    """Generate a hexagonal tiling with a specific color for each layer."""
    hexagons_by_layer = []

    for layer in range(layers + 1):
        layer_hexagons = []
        # 只生成当前层的六边形（而不是从中心到当前层的所有六边形）
        if layer == 0:
            # 中心六边形
            layer_hexagons.append(create_hexagon(radius))
        else:
            # 对于每一层，只生成位于该层边界上的六边形
            for q in range(-layer, layer + 1):
                for r in range(-layer, layer + 1):
                    if abs(q + r) == layer:  # 改为 == 而不是 <=
                        x_offset = radius * 3 / 2 * q
                        y_offset = radius * np.sqrt(3) * (r + q / 2)
                        layer_hexagons.append(create_hexagon(radius) + [x_offset, y_offset])
        
        hexagons_by_layer.append(layer_hexagons)

    return hexagons_by_layer


def visualize_colored_hexagonal_tiling(hexagons_by_layer):
    """Visualize the hexagonal tiling with different colors for each layer."""
    # 创建更大的图形,增加DPI以提高清晰度
    plt.figure(figsize=(10, 10), dpi=300)
    
    # 使用更专业的配色方案
    colors = plt.cm.RdYlBu(np.linspace(0, 1, len(hexagons_by_layer)))

    # 绘制六边形
    for layer_idx, layer_hexagons in enumerate(hexagons_by_layer):
        for hexagon in layer_hexagons:
            plt.fill(hexagon[:, 0], hexagon[:, 1], 
                    color=colors[layer_idx],
                    edgecolor='black',
                    linewidth=0.8,
                    alpha=0.8)  # 添加透明度

    # 设置坐标轴
    plt.axis('equal')
    plt.axis('off')
    
    # 添加标题和说明
    plt.title('Hexagonal Tiling Pattern', 
              fontsize=16, 
              pad=20,
              fontweight='bold')
    
    # 添加图例
    legend_elements = [plt.Rectangle((0, 0), 1, 1, 
                                   facecolor=colors[i], 
                                   edgecolor='black',
                                   alpha=0.8,
                                   label=f'Layer {i+1}') 
                      for i in range(len(hexagons_by_layer))]
    plt.legend(handles=legend_elements, 
              loc='center left', 
              bbox_to_anchor=(1, 0.5),
              title='Layer Distribution',
              title_fontsize=12,
              fontsize=10)
    
    # 调整布局以适应图例
    plt.tight_layout()
    
    # 保存高质量图片
    plt.savefig('hexagonal_tiling.png', 
                dpi=300, 
                bbox_inches='tight',
                pad_inches=0.1)
    
    plt.show()


# 生成六边形平铺图案
radius = 1
layers = 10  # 层数
hexagons_by_layer = generate_colored_hexagonal_tiling(radius, layers)

# 可视化结果
visualize_colored_hexagonal_tiling(hexagons_by_layer)
