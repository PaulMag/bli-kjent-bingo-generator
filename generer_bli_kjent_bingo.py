import subprocess

import pandas as pd

URL_FINN_PERSON = "https://docs.google.com/spreadsheets/d/1b9KG1c0mX0qJD8iYKNcNwCdNS6uVIizLZZvSsL0fajk/export?format=csv&gid=0"
URL_UTFORDRINGER = "https://docs.google.com/spreadsheets/d/1b9KG1c0mX0qJD8iYKNcNwCdNS6uVIizLZZvSsL0fajk/export?format=csv&gid=235594146"

df = pd.read_csv(URL_FINN_PERSON)
df_utfordringer = pd.read_csv(URL_UTFORDRINGER)

THEME = "tema"
TASK = "oppgave"
N_PAGES = 60
N_TASKS_PER_THEME = 5


def escape_latex(text):
    replacements = {
        "\\": r"\textbackslash{}",
        "&": r"\&",
        "%": r"\%",
        "$": r"\$",
        "#": r"\#",
        "_": r"\_",
        "{": r"\{",
        "}": r"\}",
        "~": r"\textasciitilde{}",
        "^": r"\textasciicircum{}",
    }
    return "".join(replacements.get(c, c) for c in str(text))


def make_page():
    return make_finn_personer_page() + "\n\\newpage\n" + rules_page()


def make_finn_personer_page():
    sampled = pd.concat(
        [
            group.sample(n=min(N_TASKS_PER_THEME, len(group)))
            for _, group in df.groupby(THEME, sort=False)
        ],
        ignore_index=True,
    )
    tasks = (
        sampled["oppgave"]
        .sample(n=min(25, len(sampled)), replace=len(sampled) < 25)
        .tolist()
    )
    tasks = (tasks + ["..."] * 25)[:25]

    rows_latex = []
    for i in range(0, 25, 5):
        cells = " & ".join(
            rf"\parbox[c][2.5cm][c]{{\dimexpr 0.2\textwidth-2\tabcolsep-0.5pt}} {{\Large\bfseries\centering\vspace{{0.3em}}{escape_latex(str(t)[:1].upper() + str(t)[1:])}\vspace{{0.3em}}}}"
            for t in tasks[i : i + 5]
        )
        rows_latex.append(
            cells + r" \\ \arrayrulecolor{lightgray}\hline\arrayrulecolor{black}"
        )
        blank = " & ".join(
            r"\parbox[c][1cm][c]{\dimexpr 0.2\textwidth-2\tabcolsep-0.5pt}{\vspace{1.2em}}"
            for _ in range(5)
        )
        rows_latex.append(blank + r" \\ \hline")

    rows = "\n".join(rows_latex)

    return rf"""
\AddToShipoutPictureBG*{{\includegraphics[width=\paperwidth,height=\paperheight]{{bingobakrunn-uten-sider.png}}}}
\raggedright\Large\bfseries Finn noen som...\vspace{{0.1cm}}

\begin{{tabular}}{{|c|c|c|c|c|}}
\hline
{rows}
\end{{tabular}}
"""


def rules_page():
    return rf"""
\AddToShipoutPictureBG*{{\includegraphics[width=\paperwidth,height=\paperheight]{{bingobakgrunn.png}}}}
\centering\begin{{minipage}}{{0.60\textwidth}}
\vspace{{2.5cm}}
\begin{{center}}{{\Huge\bfseries Bli-kjent-bingo - Julebord 2026}}\end{{center}}
\vspace{{1.0cm}}
Finn kolleger som matcher beskrivelsene i bingokortet og få de til å signere i ruten de matcher.
Alle signaturer må være unike.\\

Det er fem premier, men du kan kun vinne én gang.\\

Når du har fullført et antall kolonner/rader,
kan du velge å løse inn bingokortet for en premie,
eller vente til du har nok til en høyere plassering.\\

\emph{{Husk: Kun én premie per person. Du kan ikke få både 2. og 4. plass.}}\\

1. plass (5 kolonner/rader)\\
2. plass (4 kolonner/rader)\\
3. plass (3 kolonner/rader)\\
4. plass (2 kolonner/rader)\\
5. plass (1 kolonner/rader)\\

Når du får bingo, vis kortet til noen i julebordkomiteen.
\end{{minipage}}
"""


pages = "\n\\newpage\n".join(make_page() for _ in range(N_PAGES))

latex = rf"""\documentclass[a4paper, landscape]{{article}}
\usepackage[utf8]{{inputenc}}
\usepackage[T1]{{fontenc}}
\usepackage[norsk]{{babel}}
\usepackage[margin=1.0cm]{{geometry}}
\usepackage{{longtable}}
\usepackage{{parskip}}
\usepackage{{graphicx}}
\usepackage[table]{{xcolor}}
\usepackage{{eso-pic}}
\renewcommand{{\familydefault}}{{\sfdefault}}
\setlength{{\tabcolsep}}{{4pt}}
\pagestyle{{empty}}
\begin{{document}}
{pages}
\end{{document}}
"""

with open("bli-kjent-bingo.tex", "w", encoding="utf-8") as f:
    f.write(latex)

subprocess.run(
    ["pdflatex", "-interaction=nonstopmode", "bli-kjent-bingo.tex"], check=True
)
