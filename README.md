# 📈 Graph Plotter

A lightweight desktop graphing calculator built with Python and Tkinter. Type a function, hit **Plot**, and explore it with zoom and pan. No third-party libraries required.

## ✨ Features

- **Plot any function of `x`**: type expressions like `x**2`, `sin(x)/x`, or `exp(-x**2)`.
- **Multiple graphs at once**: separate functions with commas (e.g. `sin(x), cos(x), x**2`). Each gets its own color and a legend entry.
- **Polynomial Builder**: choose a degree (0–10) and enter coefficients instead of typing the expression by hand. Quick buttons for Linear, Quadratic, Cubic and Quartic.
- **Trig and inverse trig buttons**: insert `sin`, `cos`, `tan`, `cot`, `sec`, `csc` and `asin`, `acos`, `atan`, `acot`, `asec`, `acsc` with one click.
- **Interactive canvas**:
  - Scroll to zoom in/out around the cursor
  - Click and drag to pan
  - **Reset View** to return to the default window
- **Adaptive grid**: grid lines and axis labels adjust automatically as you zoom.
- **Graceful handling of discontinuities**: asymptotes (e.g. `tan(x)`, `1/x`) are broken into separate segments rather than drawn as a vertical line.
- **Error feedback**: invalid expressions are flagged with `(error)` in the legend, and invalid ranges show a dialog.
- **Restricted `eval` namespace**: expressions are evaluated with builtins disabled, exposing only math functions.

## 🛠️ Requirements

- Python 3.6 or newer
- Tkinter (included with most Python installations)

Uses only the standard library (`tkinter`, `math`), so there is nothing to `pip install`.

> **Linux users:** if Tkinter is missing, install it with  
> `sudo apt install python3-tk` (Debian/Ubuntu) or `sudo dnf install python3-tkinter` (Fedora).

## 🚀 Getting Started

```bash
# Clone the repository
git clone https://github.com/Anik-Kumar29/Graph-Plotter-.git
cd Graph-Plotter-

# The main code lives on the Graph_Plotter branch
git checkout Graph_Plotter

# Run the app
python graph_plotter.py
```

## 📖 Usage

1. Enter one or more functions in the **f(x) =** box, separated by commas.
2. Optionally set **X min** and **X max** to change the horizontal range.
3. Press **Enter** or click **Plot**.
4. Zoom with the mouse wheel, pan by dragging, and click **Reset View** to start over.
5. Use the tabs below the input bar to build polynomials or insert trig functions. Clicking a button appends it to the current expression.

### Example expressions

| Expression | What it draws |
|---|---|
| `x**2` | Parabola |
| `2*x**3 - 4*x + 1` | Cubic polynomial |
| `sin(x), cos(x)` | Sine and cosine together |
| `tan(x)` | Tangent with visible asymptotes |
| `sqrt(x)` | Square root (defined for x ≥ 0) |
| `log(x)` | Natural logarithm |
| `exp(-x**2)` | Gaussian bell curve |
| `abs(x)` | Absolute value |

## 🧮 Supported Functions and Constants

| Category | Available |
|---|---|
| Operators | `+`, `-`, `*`, `/`, `**` (power), parentheses |
| Trigonometric | `sin`, `cos`, `tan`, `cot`, `sec`, `csc` |
| Inverse trig | `asin`, `acos`, `atan`, `acot`, `asec`, `acsc` |
| Hyperbolic | `sinh`, `cosh`, `tanh`, `asinh`, `acosh`, `atanh` |
| Exponential / log | `exp`, `log`, `log10`, `log2`, `sqrt` |
| Other | `abs`, `pow`, `min`, `max`, `floor`, `ceil`, `factorial`, `gamma`, ... |
| Constants | `pi`, `e`, `tau`, `inf` |

Everything in Python's [`math`](https://docs.python.org/3/library/math.html) module is available. Trig functions work in **radians**.

> **Note:** use `**` for powers (`x**2`), not `^`.

## 📁 Project Structure

```
Graph-Plotter-/
├── graph_plotter.py   # Complete application (GUI + plotting logic)
└── README.md
```

## ⚙️ How It Works

- The visible window is mapped to canvas pixels through `_to_screen` / `_to_math` coordinate helpers.
- Each function is sampled at roughly one point per horizontal pixel (minimum 300 samples).
- Points that raise errors or return `NaN`/`inf`/complex values are skipped, which splits the line into segments.
- A sudden jump larger than 1.5× the canvas height is treated as an asymptote and the line is broken.
- Grid spacing uses a "nice step" algorithm (1, 2, 5 × 10ⁿ) to keep labels readable at any zoom level.

## 🔮 Ideas for Future Improvements

- Independent Y-range inputs
- Export the graph as an image
- Trace mode to read values under the cursor
- Support for implicit equations and parametric curves
- Degrees/radians toggle

## 🤝 Contributing

Contributions, issues and feature requests are welcome. Fork the repo, create a branch, and open a pull request.

## 📄 License

No license has been specified yet. Consider adding one (such as [MIT](https://choosealicense.com/licenses/mit/)) so others know how they can use this project.

## 👤 Author

**Anik Kumar**: [@Anik-Kumar29](https://github.com/Anik-Kumar29)
