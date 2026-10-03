# 📈 Graph Plotter

A desktop graphing calculator built with Python and Tkinter, with a dark theme and no third-party dependencies. Plot several functions at once, draw inequalities and implicit curves, restrict domains, tweak parameters with sliders, and compute definite integrals, all from a single window.

## ✨ Features

- **Multiple expressions**: add or remove rows with **+ Add** / **✕**. Each row gets its own color, and the toolbar inserts into whichever row is active.
- **Plain functions** `f(x)`: for example `x^2`, `log(x)`, `sin(x)/x`.
- **Domain restrictions**: append `{condition}` to limit where a function is drawn, e.g. `floor(x) {-1<=x<=5}`. Combine conditions with `and` / `or`.
- **Inequalities and implicit equations** in `x` and `y`:
  - `y < x^2` shades the region
  - `x^2 + y^2 = 25` draws the curve
  - `x > 2` shades the vertical strip where it holds
- **Parameter sliders** `a`, `b`, `c`, `k` (range −10 to 10): use them in any expression, e.g. `a*sin(b*x + c)`, and the graph updates live.
- **Analysis toggles** (apply to plain-function rows):
  - **Roots**: marks where the curve crosses zero
  - **Extrema**: marks local maxima and minima
  - **Inters**: marks intersections between curves
  - **f'(x)**: overlays a dashed derivative curve
- **Definite integral**: enter bounds **A** and **B** and click **Compute** to get the area under the first plain function (trapezoidal rule).
- **Domain and range readout** next to each row.
- **Pan and zoom**: drag to pan, scroll to zoom around the cursor.
- **Live coordinates** in the status bar as you move the mouse.
- **Symbol toolbar**: one-click trig, inverse trig, `log`, `ln`, `abs`, `sqrt`, `floor`, `frac`, braces, comparison operators, `and` / `or`, and variables.
- **Settings and export**: toggle the background grid, and save a snapshot of the canvas.

## 🛠️ Requirements

- Python 3.6 or newer
- Tkinter (bundled with most Python installs)

Only the standard library is used (`tkinter`, `math`, `re`), so there is nothing to `pip install`.

> **Linux:** if Tkinter is missing, run `sudo apt install python3-tk` (Debian/Ubuntu) or `sudo dnf install python3-tkinter` (Fedora).

## 🚀 Getting Started

```bash
git clone https://github.com/Anik-Kumar29/Graph-Plotter-.git
cd Graph-Plotter-
git checkout Graph_Plotter     # the main code lives on this branch
python graph_plotter.py
```

The app opens with three example rows: `x^2`, `log(x)` and `floor(x) {-1<=x<=5}`.

## 📖 Usage

1. Type an expression into a row and press **Enter** (or click a toolbar button, which inserts text and replots).
2. Use **+ Add** for more rows and **✕** to delete one.
3. Drag the `a`, `b`, `c`, `k` sliders to animate parameters.
4. Tick **Roots**, **Extrema**, **Inters** or **f'(x)** for analysis overlays.
5. Set **A** and **B**, then click **Compute** for the integral.
6. **Reset** restores the default view and slider values.

### Example expressions

| Type this | You get |
|---|---|
| `x^2` | Parabola |
| `a*sin(b*x + c)` | Sine wave controlled by the sliders |
| `sqrt(x) {x>=0}` | Square root on its domain |
| `ln(x)` | Natural logarithm |
| `log(x)` | Base-10 logarithm |
| `floor(x) {-1<=x<=5}` | Step function limited to [−1, 5] |
| `x {x<0 or x>2}` | Line with a gap between 0 and 2 |
| `x^2 + y^2 = 25` | Circle of radius 5 |
| `y < x^2` | Shaded region below the parabola |
| `x > 2` | Shaded strip to the right of x = 2 |

## 🧮 Syntax Notes

| Item | Details |
|---|---|
| Power | `^` or `**` (`x^2` and `x**2` both work) |
| `log(x)` | **Base 10** |
| `ln(x)` | Natural logarithm |
| Trig | `sin`, `cos`, `tan`, `cot`, `sec`, `csc` (radians) |
| Inverse trig | `asin`, `acos`, `atan`, `acot`, `asec`, `acsc` |
| Rounding | `floor(x)`, `ceil(x)`, `frac(x)` = x − ⌊x⌋ |
| Other | `abs`, `sqrt`, `pow`, `min`, `max`, `exp`, and everything in Python's `math` module |
| Constants | `pi`, `e`, `tau` |
| Parameters | `a`, `b`, `c`, `k` (sliders) |
| Restrictions | `{x>=0}`, `{-1<=x<=5}`, `{x<0 or x>2}` |
| Relations | `<`, `>`, `<=`, `>=`, `=` |

## 🖱️ Controls

| Action | Effect |
|---|---|
| Scroll wheel | Zoom in/out at the cursor |
| Click and drag | Pan the view |
| Mouse move | Shows `X` / `Y` in the status bar |
| Enter | Replot the current row |

## 📁 Project Structure

```
Graph-Plotter-/
├── graph_plotter.py   # Complete application (UI, parsing, plotting, analysis)
└── README.md
```

## ⚠️ Known Limitations

- **Export** writes an `.eps` snapshot to a fixed path (`/mnt/user-data/outputs/graph_export.eps`), which will not exist on most machines. Change `path` in `_export_canvas` to a location on your computer.
- The toolbar's **GIF** button is a placeholder: animated GIF export is not available in this Tkinter-only build.
- Roots, extrema, intersections, the derivative overlay and the integral work on plain `f(x)` rows only, not on inequalities or implicit curves.
- Implicit curves and inequality shading are drawn on a pixel grid, so they are approximate and can be slow on very large windows.
- Expressions are evaluated with Python's `eval` using a restricted namespace. That is fine for personal use, but do not expose it to untrusted input.

## 🤝 Contributing

Issues and pull requests are welcome. Fork the repo, create a branch, and open a PR.

## 📄 License

No license has been specified yet. Consider adding one, such as [MIT](https://choosealicense.com/licenses/mit/).

## 👤 Author

**Anik Kumar**: [@Anik-Kumar29](https://github.com/Anik-Kumar29)
