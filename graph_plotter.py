import re
import math
import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
# evaluation 
SAFE_NAMES = {name: getattr(math, name) for name in dir(math) if not name.startswith("_")}
def cot(x):
    return 1.0 / math.tan(x)

def sec(x):
    return 1.0 / math.cos(x)


def csc(x):
    return 1.0 / math.sin(x)


def acot(x):
    return math.pi / 2 if x == 0 else math.atan(1.0 / x)


def asec(x):
    return math.acos(1.0 / x)


def acsc(x):
    return math.asin(1.0 / x)


def frac(x):
    """Fractional part function: frac(x) = x - floor(x)."""
    return x - math.floor(x)


SAFE_NAMES.update({
    "abs": abs, "pow": pow, "min": min, "max": max,
    "cot": cot, "sec": sec, "csc": csc,
    "acot": acot, "asec": asec, "acsc": acsc,
    "frac": frac,})

#color
BG = "#1a1a2e"
PANEL = "#22223a"
GRID_COLOR = "#33334d"
AXIS_COLOR = "#c9c9d9"
TEXT_COLOR = "#e6e6f0"
ENTRY_BG = "#2a2a45"
ROW_COLORS = ["#4aa8ff", "#c17bff", "#ff7a7a", "#5be3a4", "#ffcc55",
              "#ff9f4a", "#5bc8ff", "#f26cd8"]


def preprocess(expr):
    e = expr.strip()
    e = e.replace("^", "**")
    e = re.sub(r"\bln\(", "\uE000(", e)      # protect ln(
    e = re.sub(r"\blog\(", "log10(", e)      #   log() is base-10
    e = e.replace("\uE000(", "log(")         # ln() -> natural log
    return e


def classify_and_split(text):
    #Return (lhs, op, rhs). op is None for a plain expression.
    for op in ("<=", ">=", "=="):
        if op in text:
            i = text.index(op)
            return text[:i], op, text[i + len(op):]
    for op in ("=", "<", ">"):
        if op in text:
            i = text.index(op)
            return text[:i], op, text[i + len(op):]
    return text, None, None


def extract_domain_restriction(text):
    m = re.search(r"\{(.*)\}", text)
    if not m:
        return text.strip(), None
    restriction = m.group(1).strip()
    main = (text[:m.start()] + text[m.end():]).strip()
    return main, (restriction if restriction else None)


def preprocess_restriction(expr):
    e = preprocess(expr)
    e = re.sub(r"(?<![<>=!])=(?!=)", "==", e)
    return e


class GraphPlotter(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Graph Plotter")
        self.geometry("1200x780")
        self.minsize(900, 600)
        self.configure(bg=BG)

        self.x_min, self.x_max = -10.0, 10.0
        self.y_min, self.y_max = -6.0, 6.0
        self._drag_start = None
        self.show_grid_flag = True
        self.active_entry = None

        self.slider_vars = {
            "a": tk.DoubleVar(value=1.0),
            "b": tk.DoubleVar(value=1.0),
            "c": tk.DoubleVar(value=0.0),
            "k": tk.DoubleVar(value=1.0),
        }
        self.opt_roots = tk.BooleanVar(value=False)
        self.opt_extrema = tk.BooleanVar(value=False)
        self.opt_inters = tk.BooleanVar(value=False)
        self.opt_fprime = tk.BooleanVar(value=False)

        self.expr_rows = []  # list of dicts: color, var, frame, entry

        self._setup_style()
        self._build_ui()
        self._add_row("x^2")
        self._add_row("log(x)")
        self._add_row("floor(x) {-1<=x<=5}")
        self._plot()

    # -------------------------------------------------------------- style
    def _setup_style(self):
        style = ttk.Style(self)
        try:
            style.theme_use("clam")
        except tk.TclError:
            pass
        style.configure("TFrame", background=PANEL)
        style.configure("TLabel", background=PANEL, foreground=TEXT_COLOR)
        style.configure("TButton", background="#33334d", foreground=TEXT_COLOR, padding=4)
        style.map("TButton", background=[("active", "#44446a")])
        style.configure("Add.TButton", background="#2fbf71", foreground="#0c1a12")
        style.map("Add.TButton", background=[("active", "#3fd684")])
        style.configure("Del.TButton", background="#e5484d", foreground="#2a0a0a")
        style.map("Del.TButton", background=[("active", "#ff6b70")])
        style.configure("TCheckbutton", background=PANEL, foreground=TEXT_COLOR)
        style.map("TCheckbutton", background=[("active", PANEL)])
        style.configure("Horizontal.TScale", background=PANEL)

    # ---------------------------------------------------------------- UI
    def _build_ui(self):
        # ---- expression list ----
        self.expr_container = ttk.Frame(self, padding=6)
        self.expr_container.pack(side=tk.TOP, fill=tk.X)

        add_bar = ttk.Frame(self, padding=(6, 0, 6, 4))
        add_bar.pack(side=tk.TOP, fill=tk.X)
        ttk.Button(add_bar, text="+ Add", style="Add.TButton",
                   command=lambda: self._add_row("")).pack(side=tk.LEFT)
        ttk.Button(add_bar, text="Reset", command=self._reset_all).pack(side=tk.LEFT, padx=4)
        ttk.Button(add_bar, text="Settings", command=self._open_settings).pack(side=tk.LEFT, padx=4)
        ttk.Button(add_bar, text="Export", command=self._export_canvas).pack(side=tk.LEFT, padx=4)

        ttk.Checkbutton(add_bar, text="Roots", variable=self.opt_roots,
                         command=self._plot).pack(side=tk.LEFT, padx=(20, 4))
        ttk.Checkbutton(add_bar, text="Extrema", variable=self.opt_extrema,
                         command=self._plot).pack(side=tk.LEFT, padx=4)
        ttk.Checkbutton(add_bar, text="Inters", variable=self.opt_inters,
                         command=self._plot).pack(side=tk.LEFT, padx=4)
        ttk.Checkbutton(add_bar, text="f'(x)", variable=self.opt_fprime,
                         command=self._plot).pack(side=tk.LEFT, padx=4)

        # ---- sliders a b c k ----
        slider_bar = ttk.Frame(self, padding=(6, 2, 6, 4))
        slider_bar.pack(side=tk.TOP, fill=tk.X)
        for name in ("a", "b", "c", "k"):
            ttk.Label(slider_bar, text=f"{name}:").pack(side=tk.LEFT, padx=(10, 2))
            val_lbl = ttk.Label(slider_bar, text=f"{self.slider_vars[name].get():.2f}", width=5)
            scale = ttk.Scale(slider_bar, from_=-10, to=10, orient="horizontal",
                               variable=self.slider_vars[name], length=160,
                               command=lambda v, n=name, l=val_lbl: self._on_slider(n, v, l))
            scale.pack(side=tk.LEFT, padx=2)
            val_lbl.pack(side=tk.LEFT)

        # ---- integral A / B ----
        integ_bar = ttk.Frame(self, padding=(6, 0, 6, 4))
        integ_bar.pack(side=tk.TOP, fill=tk.X)
        ttk.Label(integ_bar, text="\u222b Area from A:").pack(side=tk.LEFT)
        self.a_bound_var = tk.StringVar(value="0")
        ttk.Entry(integ_bar, textvariable=self.a_bound_var, width=6).pack(side=tk.LEFT, padx=(2, 8))
        ttk.Label(integ_bar, text="to B:").pack(side=tk.LEFT)
        self.b_bound_var = tk.StringVar(value="3")
        ttk.Entry(integ_bar, textvariable=self.b_bound_var, width=6).pack(side=tk.LEFT, padx=2)
        ttk.Button(integ_bar, text="Compute", command=self._plot).pack(side=tk.LEFT, padx=8)
        self.integral_lbl = ttk.Label(integ_bar, text="\u222b = --", foreground="#5be3a4")
        self.integral_lbl.pack(side=tk.LEFT, padx=8)

        # ---- symbol toolbar ----
        toolbar = ttk.Frame(self, padding=(6, 0, 6, 6))
        toolbar.pack(side=tk.TOP, fill=tk.X)
        buttons = [
            ("sin", "sin()"), ("cos", "cos()"), ("tan", "tan()"),
            ("cot", "cot()"), ("sec", "sec()"), ("csc", "csc()"),
            ("sin\u207b\u00b9", "asin()"), ("cos\u207b\u00b9", "acos()"), ("tan\u207b\u00b9", "atan()"),
            ("cot\u207b\u00b9", "acot()"), ("sec\u207b\u00b9", "asec()"), ("csc\u207b\u00b9", "acsc()"),
            ("log", "log()"), ("ln", "ln()"), ("GIF", None),
            ("|x|", "abs()"), ("\u221a", "sqrt()"), ("x\u00b2", "**2"),
            ("\u230ax\u230b", "floor()"), ("{x}", "frac()"),
            ("{", "{"), ("}", "}"), ("\u2264", "<="), ("\u2265", ">="),
            ("and", " and "), ("or", " or "), ("a", "a"), ("b", "b"),
            ("x", "x"), ("y", "y"), ("=", "="),
        ]
        for label, payload in buttons:
            cmd = (lambda p=payload: self._insert(p)) if payload is not None else self._gif_stub
            ttk.Button(toolbar, text=label, width=5, command=cmd).pack(side=tk.LEFT, padx=1)

        # ---- canvas ----
        self.canvas = tk.Canvas(self, bg=BG, highlightthickness=0)
        self.canvas.pack(fill=tk.BOTH, expand=True, padx=6, pady=(0, 0))
        self.canvas.bind("<Configure>", lambda e: self._plot())
        self.canvas.bind("<ButtonPress-1>", self._on_press)
        self.canvas.bind("<B1-Motion>", self._on_drag)
        self.canvas.bind("<Motion>", self._on_motion)
        self.canvas.bind("<MouseWheel>", self._on_scroll)
        self.canvas.bind("<Button-4>", self._on_scroll)
        self.canvas.bind("<Button-5>", self._on_scroll)

        # ---- status bar ----
        status = ttk.Frame(self, padding=(6, 2))
        status.pack(side=tk.BOTTOM, fill=tk.X)
        self.status_var = tk.StringVar(value="X = -- | Y = --")
        ttk.Label(status, textvariable=self.status_var).pack(side=tk.LEFT)

    # ------------------------------------------------------- expr rows UI
    def _add_row(self, initial_text):
        idx = len(self.expr_rows)
        color = ROW_COLORS[idx % len(ROW_COLORS)]
        row = tk.Frame(self.expr_container, bg=PANEL)
        row.pack(fill=tk.X, pady=2)

        dot = tk.Canvas(row, width=18, height=18, bg=PANEL, highlightthickness=0)
        dot.create_oval(2, 2, 16, 16, fill=color, outline="")
        dot.pack(side=tk.LEFT, padx=(0, 6))

        var = tk.StringVar(value=initial_text)
        entry = tk.Entry(row, textvariable=var, bg=ENTRY_BG, fg=TEXT_COLOR,
                          insertbackground=TEXT_COLOR, relief="flat", font=("TkFixedFont", 11))
        entry.pack(side=tk.LEFT, fill=tk.X, expand=True, ipady=4)
        entry.bind("<Return>", lambda e: self._plot())
        entry.bind("<FocusIn>", lambda e, en=entry: self._set_active(en))

        row_ref = {"color": color, "var": var, "frame": row, "entry": entry}

        del_btn = ttk.Button(row, text="\u2715", style="Del.TButton", width=3,
                              command=lambda r=row_ref: self._remove_row(r))
        del_btn.pack(side=tk.LEFT, padx=(6, 0))

        range_lbl = tk.Label(row, text="", bg=PANEL, fg="#8fd3ff",
                              font=("TkDefaultFont", 9), width=30, anchor="w")
        range_lbl.pack(side=tk.LEFT, padx=(8, 0))
        row_ref["range_lbl"] = range_lbl

        self.expr_rows.append(row_ref)
        self.active_entry = entry
        return row_ref

    def _remove_row(self, row_ref):
        row_ref["frame"].destroy()
        self.expr_rows.remove(row_ref)
        if self.active_entry is row_ref["entry"]:
            self.active_entry = self.expr_rows[-1]["entry"] if self.expr_rows else None
        self._plot()

    def _set_active(self, entry):
        self.active_entry = entry

    def _insert(self, text):
        entry = self.active_entry
        if entry is None and self.expr_rows:
            entry = self.expr_rows[0]["entry"]
        if entry is None:
            return
        entry.insert(tk.INSERT, text)
        if text.endswith("()"):
            pos = entry.index(tk.INSERT)
            entry.icursor(pos - 1)
        entry.focus_set()
        self._plot()

    def _gif_stub(self):
        messagebox.showinfo("export",
                             "Animated GIF export isn't available in this tkinter-only build.\n"
                             "Use Export to save a static snapshot instead.")

    # ------------------------------------------------------------ sliders
    def _on_slider(self, name, value, label_widget):
        label_widget.config(text=f"{float(value):.2f}")
        self._plot()

    def _slider_vals(self):
        return {k: v.get() for k, v in self.slider_vars.items()}

    def _reset_all(self):
        self.x_min, self.x_max = -10.0, 10.0
        self.y_min, self.y_max = -6.0, 6.0
        for name, default in (("a", 1.0), ("b", 1.0), ("c", 0.0), ("k", 1.0)):
            self.slider_vars[name].set(default)
        self._plot()

    def _open_settings(self):
        answer = messagebox.askyesno("Settings", "Show background grid?",
                                      default="yes" if self.show_grid_flag else "no")
        self.show_grid_flag = answer
        self._plot()

    def _export_canvas(self):
        path = "/mnt/user-data/outputs/graph_export.eps"
        try:
            self.canvas.postscript(file=path, colormode="color")
            messagebox.showinfo("Exported", f"Snapshot saved to:\n{path}\n"
                                             "(Postscript/EPS — open with an image viewer or convert to PNG.)")
        except Exception as exc:
            messagebox.showerror("Export failed", str(exc))

    # ------------------------------------------------------- coord helpers
    def _to_screen(self, x, y, w, h):
        sx = (x - self.x_min) / (self.x_max - self.x_min) * w
        sy = h - (y - self.y_min) / (self.y_max - self.y_min) * h
        return sx, sy

    def _to_math(self, sx, sy, w, h):
        x = self.x_min + sx / w * (self.x_max - self.x_min)
        y = self.y_min + (h - sy) / h * (self.y_max - self.y_min)
        return x, y

    # -------------------------------------------------------------- events
    def _on_press(self, event):
        self._drag_start = (event.x, event.y)

    def _on_drag(self, event):
        if self._drag_start is None:
            return
        w, h = self.canvas.winfo_width(), self.canvas.winfo_height()
        dx = event.x - self._drag_start[0]
        dy = event.y - self._drag_start[1]
        mx = dx / w * (self.x_max - self.x_min)
        my = dy / h * (self.y_max - self.y_min)
        self.x_min -= mx
        self.x_max -= mx
        self.y_min += my
        self.y_max += my
        self._drag_start = (event.x, event.y)
        self._plot()

    def _on_scroll(self, event):
        delta = event.delta if event.delta else (120 if event.num == 4 else -120)
        factor = 0.9 if delta > 0 else 1.1
        w, h = self.canvas.winfo_width(), self.canvas.winfo_height()
        mx, my = self._to_math(event.x, event.y, w, h)
        self.x_min = mx + (self.x_min - mx) * factor
        self.x_max = mx + (self.x_max - mx) * factor
        self.y_min = my + (self.y_min - my) * factor
        self.y_max = my + (self.y_max - my) * factor
        self._plot()

    def _on_motion(self, event):
        w, h = self.canvas.winfo_width(), self.canvas.winfo_height()
        mx, my = self._to_math(event.x, event.y, w, h)
        self.status_var.set(f"X = {mx:.4f} | Y = {my:.4f}")

    # ---------------------------------------------------------------- core
    def _nice_step(self, span, target_ticks=10):
        if span <= 0:
            return 1.0
        raw = span / target_ticks
        magnitude = 10 ** math.floor(math.log10(raw))
        for m in (1, 2, 5, 10):
            step = m * magnitude
            if step >= raw:
                return step
        return 10 * magnitude

    def _eval(self, expr, x=None, y=None):
        env = {**SAFE_NAMES, **self._slider_vals()}
        if x is not None:
            env["x"] = x
        if y is not None:
            env["y"] = y
        return eval(expr, {"__builtins__": {}}, env)

    def _plot(self):
        w = self.canvas.winfo_width() or 1100
        h = self.canvas.winfo_height() or 550
        self.canvas.delete("all")

        if self.show_grid_flag:
            self._draw_grid(w, h)
        self._draw_axes(w, h)

        plain_curves = []  # (xs, ys, color) for roots/extrema/inters/derivative
        for row in self.expr_rows:
            text = row["var"].get().strip()
            if not text:
                row["range_lbl"].config(text="")
                continue
            try:
                result = self._render_expression(text, row["color"], w, h)
            except Exception:
                row["range_lbl"].config(text="error")
                continue
            if result is not None:
                xs, ys = result
                plain_curves.append((xs, ys, row["color"]))
                valid_ys = [v for v in ys if v is not None]
                _, restriction = extract_domain_restriction(text)
                dom_part = f"Domain: {{{restriction}}}  " if restriction else ""
                if valid_ys:
                    row["range_lbl"].config(
                        text=f"{dom_part}Range: [{min(valid_ys):.3g}, {max(valid_ys):.3g}]")
                else:
                    row["range_lbl"].config(text=f"{dom_part}Range: --")
            else:
                row["range_lbl"].config(text="")

        if self.opt_fprime.get():
            for xs, ys, color in plain_curves:
                self._draw_derivative(xs, ys, w, h, color)
        if self.opt_roots.get():
            for xs, ys, _ in plain_curves:
                self._mark_roots(xs, ys, w, h)
        if self.opt_extrema.get():
            for xs, ys, _ in plain_curves:
                self._mark_extrema(xs, ys, w, h)
        if self.opt_inters.get() and len(plain_curves) >= 2:
            for i in range(len(plain_curves)):
                for j in range(i + 1, len(plain_curves)):
                    self._mark_intersections(plain_curves[i], plain_curves[j], w, h)

        self._update_integral()

    # -------------------------------------------------- expression render
    def _render_expression(self, text, color, w, h):
        main_text, restriction = extract_domain_restriction(text)
        restriction_p = preprocess_restriction(restriction) if restriction else None

        lhs, op, rhs = classify_and_split(main_text)
        lhs_p = preprocess(lhs)

        if op is None:
            return self._draw_plain_function(lhs_p, w, h, color, restriction_p)

        rhs_p = preprocess(rhs)
        has_y = ("y" in lhs_p) or ("y" in rhs_p)

        if not has_y:
            self._draw_x_only_relation(lhs_p, op, rhs_p, w, h, color, restriction_p)
            return None

        if op in ("=", "=="):
            self._draw_implicit_curve(lhs_p, rhs_p, w, h, color, restriction_p)
        else:
            self._draw_inequality_region(lhs_p, op, rhs_p, w, h, color, restriction_p)
        return None

    def _draw_plain_function(self, expr, w, h, color, restriction=None):
        samples = max(300, w)
        xs, ys = [], []
        points = []
        prev_sy = None
        for i in range(samples + 1):
            x = self.x_min + (self.x_max - self.x_min) * i / samples
            try:
                if restriction is not None and not self._eval(restriction, x=x):
                    raise ValueError("outside domain")
                y = float(self._eval(expr, x=x))
                if math.isnan(y) or math.isinf(y):
                    raise ValueError
            except Exception:
                xs.append(x)
                ys.append(None)
                if len(points) > 1:
                    self.canvas.create_line(points, fill=color, width=2)
                points, prev_sy = [], None
                continue

            sx, sy = self._to_screen(x, y, w, h)
            if prev_sy is not None and abs(sy - prev_sy) > h * 1.5:
                if len(points) > 1:
                    self.canvas.create_line(points, fill=color, width=2)
                points = []
            points.append((sx, sy))
            prev_sy = sy
            xs.append(x)
            ys.append(y)

        if len(points) > 1:
            self.canvas.create_line(points, fill=color, width=2)
        return xs, ys

    def _draw_x_only_relation(self, lhs, op, rhs, w, h, color, restriction=None):
        cmp = {"<=": lambda a, b: a <= b, ">=": lambda a, b: a >= b,
               "<": lambda a, b: a < b, ">": lambda a, b: a > b,
               "=": lambda a, b: False, "==": lambda a, b: False}[op]
        step = 4
        for gx in range(0, w, step):
            mx, _ = self._to_math(gx + step / 2.0, 0, w, h)
            try:
                if restriction is not None and not self._eval(restriction, x=mx):
                    continue
                lv = self._eval(lhs, x=mx)
                rv = self._eval(rhs, x=mx)
                if cmp(lv, rv):
                    self.canvas.create_rectangle(gx, 0, gx + step, h, fill=color,
                                                  outline="", stipple="gray50")
            except Exception:
                continue

    def _draw_inequality_region(self, lhs, op, rhs, w, h, color, restriction=None):
        cmp = {"<=": lambda a, b: a <= b, ">=": lambda a, b: a >= b,
               "<": lambda a, b: a < b, ">": lambda a, b: a > b}[op]
        step = 6
        for gy in range(0, h, step):
            for gx in range(0, w, step):
                mx, my = self._to_math(gx + step / 2.0, gy + step / 2.0, w, h)
                try:
                    if restriction is not None and not self._eval(restriction, x=mx, y=my):
                        continue
                    lv = self._eval(lhs, x=mx, y=my)
                    rv = self._eval(rhs, x=mx, y=my)
                    if cmp(lv, rv):
                        self.canvas.create_rectangle(gx, gy, gx + step, gy + step,
                                                      fill=color, outline="", stipple="gray50")
                except Exception:
                    continue

    def _draw_implicit_curve(self, lhs, rhs, w, h, color, restriction=None):
        step = 4

        def F(mx, my):
            try:
                if restriction is not None and not self._eval(restriction, x=mx, y=my):
                    return None
                return self._eval(lhs, x=mx, y=my) - self._eval(rhs, x=mx, y=my)
            except Exception:
                return None

        xs = list(range(0, w + step, step))
        ys = list(range(0, h + step, step))
        vals = {}
        for gx in xs:
            for gy in ys:
                mx, my = self._to_math(gx, gy, w, h)
                vals[(gx, gy)] = F(mx, my)

        for i in range(len(xs) - 1):
            for j in range(len(ys) - 1):
                gx, gy = xs[i], ys[j]
                corners = [vals[(gx, gy)], vals[(gx + step, gy)],
                           vals[(gx + step, gy + step)], vals[(gx, gy + step)]]
                if any(c is None for c in corners):
                    continue
                if min(corners) < 0 < max(corners):
                    cx, cy = gx + step / 2.0, gy + step / 2.0
                    self.canvas.create_oval(cx - 1.5, cy - 1.5, cx + 1.5, cy + 1.5,
                                             fill=color, outline=color)

    # -------------------------------------------- roots / extrema / f'x etc.
    def _draw_marker(self, mx, my, w, h, color, label=True):
        sx, sy = self._to_screen(mx, my, w, h)
        self.canvas.create_oval(sx - 4, sy - 4, sx + 4, sy + 4, outline=color, width=2)
        if label:
            self.canvas.create_text(sx, sy - 12, text=f"({mx:.2f}, {my:.2f})",
                                     fill=color, font=("TkDefaultFont", 8))

    def _mark_roots(self, xs, ys, w, h):
        for i in range(len(xs) - 1):
            y1, y2 = ys[i], ys[i + 1]
            if y1 is None or y2 is None:
                continue
            if y1 == 0:
                self._draw_marker(xs[i], 0, w, h, "#ffffff")
            elif y1 * y2 < 0:
                t = y1 / (y1 - y2)
                rx = xs[i] + t * (xs[i + 1] - xs[i])
                self._draw_marker(rx, 0, w, h, "#ffffff")

    def _mark_extrema(self, xs, ys, w, h):
        for i in range(1, len(xs) - 1):
            if ys[i - 1] is None or ys[i] is None or ys[i + 1] is None:
                continue
            d1 = ys[i] - ys[i - 1]
            d2 = ys[i + 1] - ys[i]
            if (d1 > 0 and d2 < 0) or (d1 < 0 and d2 > 0):
                self._draw_marker(xs[i], ys[i], w, h, "#ffd166")

    def _mark_intersections(self, curve_a, curve_b, w, h):
        xs_a, ys_a, _ = curve_a
        xs_b, ys_b, _ = curve_b
        n = min(len(xs_a), len(xs_b))
        for i in range(n - 1):
            y1a, y2a = ys_a[i], ys_a[i + 1]
            y1b, y2b = ys_b[i], ys_b[i + 1]
            if None in (y1a, y2a, y1b, y2b):
                continue
            d1 = y1a - y1b
            d2 = y2a - y2b
            if d1 == 0:
                self._draw_marker(xs_a[i], y1a, w, h, "#ffffff")
            elif d1 * d2 < 0:
                t = d1 / (d1 - d2)
                ix = xs_a[i] + t * (xs_a[i + 1] - xs_a[i])
                iy = y1a + t * (y2a - y1a)
                self._draw_marker(ix, iy, w, h, "#ffffff")

    def _draw_derivative(self, xs, ys, w, h, color):
        points = []
        n = len(xs)
        for i in range(1, n - 1):
            if ys[i - 1] is None or ys[i + 1] is None:
                if len(points) > 1:
                    self.canvas.create_line(points, fill=color, width=1, dash=(4, 2))
                points = []
                continue
            dx = xs[i + 1] - xs[i - 1]
            if dx == 0:
                continue
            dy = (ys[i + 1] - ys[i - 1]) / dx
            if math.isnan(dy) or math.isinf(dy):
                continue
            sx, sy = self._to_screen(xs[i], dy, w, h)
            points.append((sx, sy))
        if len(points) > 1:
            self.canvas.create_line(points, fill=color, width=1, dash=(4, 2))

    # ------------------------------------------------------------ itegral
    def _update_integral(self):
        try:
            A = float(self.a_bound_var.get())
            B = float(self.b_bound_var.get())
        except ValueError:
            self.integral_lbl.config(text="\u222b = --")
            return

        expr = None
        for row in self.expr_rows:
            text = row["var"].get().strip()
            if not text:
                continue
            lhs, op, _ = classify_and_split(text)
            if op is None:
                expr = preprocess(lhs)
                break

        if expr is None or A == B:
            self.integral_lbl.config(text="\u222b = --")
            return

        n = 600
        step = (B - A) / n
        total = 0.0
        diverged = False
        for i in range(n + 1):
            x = A + i * step
            try:
                y = float(self._eval(expr, x=x))
                if math.isnan(y) or math.isinf(y):
                    diverged = True
                    break
            except Exception:
                diverged = True
                break
            weight = 0.5 if i == 0 or i == n else 1.0
            total += weight * y
        if diverged:
            self.integral_lbl.config(text="\u222b = Infinity")
        else:
            self.integral_lbl.config(text=f"\u222b = {total * step:.4f}")

    # -------------------------------------------------------------- drawing
    def _draw_grid(self, w, h):
        x_step = self._nice_step(self.x_max - self.x_min)
        y_step = self._nice_step(self.y_max - self.y_min)

        x = math.ceil(self.x_min / x_step) * x_step
        while x <= self.x_max:
            sx, _ = self._to_screen(x, 0, w, h)
            self.canvas.create_line(sx, 0, sx, h, fill=GRID_COLOR)
            if abs(x) > x_step / 1000:
                self.canvas.create_text(sx, h - 10, text=f"{x:g}",
                                         font=("TkDefaultFont", 8), fill=AXIS_COLOR)
            x += x_step

        y = math.ceil(self.y_min / y_step) * y_step
        while y <= self.y_max:
            _, sy = self._to_screen(0, y, w, h)
            self.canvas.create_line(0, sy, w, sy, fill=GRID_COLOR)
            if abs(y) > y_step / 1000:
                self.canvas.create_text(25, sy, text=f"{y:g}",
                                         font=("TkDefaultFont", 8), fill=AXIS_COLOR)
            y += y_step

    def _draw_axes(self, w, h):
        if self.y_min <= 0 <= self.y_max:
            _, sy0 = self._to_screen(0, 0, w, h)
            self.canvas.create_line(0, sy0, w, sy0, fill=AXIS_COLOR, width=2)
        if self.x_min <= 0 <= self.x_max:
            sx0, _ = self._to_screen(0, 0, w, h)
            self.canvas.create_line(sx0, 0, sx0, h, fill=AXIS_COLOR, width=2)
if __name__ == "__main__":
    app = GraphPlotter()
    app.mainloop()
