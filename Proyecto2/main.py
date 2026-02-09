# En funciones.py - generate_chart()
fig, ax = plt.subplots(figsize=(14, 10))  # Crear figura y ejes para gráfica principal
bars = ax.barh(y_pos, counts, color=colors, alpha=0.8, height=0.7)  # Barras horizontales para palabras
ax.set_yticks(y_pos)  # Configurar posición de ticks en eje Y
ax.set_yticklabels(words, fontsize=11)  # Etiquetas de palabras en eje Y
ax.text(width, bar.get_y(), f'{count:,}', ha='left', va='center')  # Mostrar valores en barras