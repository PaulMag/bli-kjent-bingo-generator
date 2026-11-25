import subprocess

import pandas as pd

URL_FINN_PERSON = "https://docs.google.com/spreadsheets/d/1b9KG1c0mX0qJD8iYKNcNwCdNS6uVIizLZZvSsL0fajk/export?format=csv&gid=0"
URL_UTFORDRINGER = "https://docs.google.com/spreadsheets/d/1b9KG1c0mX0qJD8iYKNcNwCdNS6uVIizLZZvSsL0fajk/export?format=csv&gid=235594146"

df_finn_personer = pd.read_csv(URL_FINN_PERSON)
df_utfordringer = pd.read_csv(URL_UTFORDRINGER)

THEME = "tema"
TASK = "oppgave"
N_PAGES = 2
N_TASKS_PER_THEME_FINN_PERSONER = 5


def escape_latex(text):
    replacements = {
        "\\": r"\textbackslash{}",
        "&": r"\&", "%": r"\%", "$": r"\$", "#": r"\#",
        "_": r"\_", "{": r"\{", "}": r"\}",
        "~": r"\textasciitilde{}", "^": r"\textasciicircum{}",
    }
    return "".join(replacements.get(c, c) for c in str(text))


def make_page():
    return make_finn_personer_page() + "\n\\newpage\n" + rules_page()


def make_finn_personer_page():
    sampled = pd.concat(
        [g.sample(n=min(N_TASKS_PER_THEME_FINN_PERSONER, len(g))) for _, g in df_finn_personer.groupby(THEME, sort=False)],
        ignore_index=True,
    )
    tasks = sampled['oppgave'].sample(n=min(25, len(sampled)), replace=len(sampled) < 25).tolist()
    tasks = (tasks + [''] * 25)[:25]

    rows_latex = []
    for i in range(0, 25, 5):
        cells = ' & '.join(rf'\parbox{{\dimexpr 0.18\textwidth-2\tabcolsep}} {{\centering\vspace{{0.3em}}{escape_latex(t)}\vspace{{0.3em}}}}' for t in tasks[i:i+5])
        rows_latex.append(cells + r' \\ \hline')

    rows = '\n'.join(rows_latex)

    return rf"""
\noindent\begin{{minipage}}{{0.75\textwidth}}
\begin{{center}}{{\Huge\bfseries Kartverket - Bli-kjent-bingo}}\end{{center}}
\end{{minipage}}
\begin{{minipage}}{{0.25\textwidth}}
\includegraphics[height=2cm]{{kv-logo.png}}
\end{{minipage}}

\begin{{center}}{{\Large\bfseries Finn personer (1 poeng per)}}\end{{center}}

\begin{{tabular}}{{|c|c|c|c|c|}}
\hline
{rows}
\end{{tabular}}
"""


def rules_page():
    return rf"""
\noindent\begin{{minipage}}{{0.75\textwidth}}
\begin{{center}}{{\Huge\bfseries Kartverket - Bli-kjent-bingo}}\end{{center}}
\end{{minipage}}
\begin{{minipage}}{{0.25\textwidth}}
\includegraphics[height=2cm]{{georg.png}}
\end{{minipage}}

Førstemann til å claime hver premie, men kan kun claime én premie.\\
1. premie (30 poeng)\\
2. premie (25 poeng)\\
3. premie (20 poeng)\\
4. premie (15 poeng)\\
5. premie (10 poeng)\\

\begin{{center}}{{\Large\bfseries Utfordringer (2 poeng per)}}\end{{center}}
"""


pages = "\n\\newpage\n".join(make_page() for _ in range(N_PAGES))

latex = rf"""\documentclass[a4paper, landscape]{{article}}
\usepackage[utf8]{{inputenc}}
\usepackage[T1]{{fontenc}}
\usepackage[norsk]{{babel}}
\usepackage[margin=1.5cm]{{geometry}}
\usepackage{{longtable}}
\usepackage{{parskip}}
\usepackage{{graphicx}}
\renewcommand{{\familydefault}}{{\sfdefault}}
\renewcommand{{\arraystretch}}{{1.6}}
\setlength{{\tabcolsep}}{{4pt}}
\pagestyle{{empty}}
\begin{{document}}
{pages}
\end{{document}}
"""

with open("bli-kjent-bingo.tex", "w", encoding="utf-8") as f:
    f.write(latex)

subprocess.run(["pdflatex", "-interaction=nonstopmode", "bli-kjent-bingo.tex"], check=True)
