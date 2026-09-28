"""Draw Figure 1 (TQS of all 60 translations as a heatmap) from outputs/figure_1.csv (optional).

    pip install matplotlib
    python analysis/optional/render_figure1.py figure1.png

The figure only displays outputs/figure_1.csv, which 30_figure_tqs.py writes from the MQM sheets;
this script adds nothing to the data. Layout: Comp. in the left panel and
Mix. in the right, passages as rows, models as columns, each cell labelled with its TQS, on
matplotlib's red-yellow-green scale from 0 to 100. Fonts and anti-aliasing vary between machines,
so the image is not checked byte for byte; figure_1.csv is.
"""
import csv
import os
import sys
from pathlib import Path

import matplotlib

matplotlib.use('Agg')
import matplotlib.pyplot as plt  # noqa: E402

OUT = Path(os.environ.get('ANALYSIS_OUT', str(Path(__file__).resolve().parent.parent / 'outputs')))
MODELS = ['Claude', 'Gemini', 'ChatGPT']
YLABEL = 'Chunk'            # the axis label of the figure (a chunk is a passage)

rows = list(csv.DictReader(open(OUT / 'figure_1.csv', encoding='utf-8')))
dest = Path(sys.argv[1]) if len(sys.argv) > 1 else OUT / 'optional' / 'figure_1.png'
dest.parent.mkdir(parents=True, exist_ok=True)

fig, axes = plt.subplots(1, 2, figsize=(10, 8), sharey=True)
for ax, text in zip(axes, ['Comp.', 'Mix.']):
    grid = [[float(r[m]) for m in MODELS] for r in rows if r['Text'] == text]
    im = ax.imshow(grid, cmap='RdYlGn', vmin=0, vmax=100, aspect='auto')
    for i, line in enumerate(grid):
        for j, v in enumerate(line):
            ax.text(j, i, f'{v:.1f}', ha='center', va='center', fontsize=10,
                    color='black' if 25 <= v <= 85 else 'white')
    ax.set_xticks(range(len(MODELS)), MODELS)
    ax.set_yticks(range(10), [str(n) for n in range(1, 11)])
    ax.set_xticks([x - .5 for x in range(1, len(MODELS))], minor=True)
    ax.set_yticks([y - .5 for y in range(1, 10)], minor=True)
    ax.grid(which='minor', color='white', linewidth=2)
    ax.tick_params(which='minor', length=0)
    ax.set_title(text, fontsize=14)
axes[0].set_ylabel(YLABEL, fontsize=12)
fig.colorbar(im, ax=axes, shrink=.7, ticks=[0, 50, 100], label='TQS')
fig.savefig(dest, dpi=225, bbox_inches='tight', metadata={'Software': None})
print(f'wrote {dest}')
