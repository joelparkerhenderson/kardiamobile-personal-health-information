# KardiaMobile personal health information

KardiaMobile personal health information for me that I'm making public for research purposes.

## KardiMobile 1L

The PDF contains a 1-lead ECG.

ECG trace is on page 2 as vector graphics.

1. Extract the vector path data from the PDF.

2. Convert to voltage/time series.

3. Save as EDF.

Files:

- [kardiamobile-1l-ecg.pdf](kardiamobile-1l-ecg.pdf) is the PDF export from Kardia

- [kardiamobile-1l-ecg.edf](kardiamobile-1l-ecg.edf) is the PDF converted to EDF

## KardiMobile 6L

[KardiaMobile 6L ECG: convert PDF to EDF](https://github.com/joelparkerhenderson/kardiamobile-6l-ecg-convert-pdf-to-edf)

The PDF contains a 6-lead ECG (I, II, III, aVR, aVL, aVF).

ECG traces span pages 2-5 as vector graphics.

1. Extract the vector path data from the PDF.

2. Convert to voltage/time series.

3. Save as EDF.

Files:

- [kardiamobile-6l-ecg.pdf](kardiamobile-6l-ecg.pdf) is the PDF export from Kardia

- [kardiamobile-6l-ecg.edf](kardiamobile-6l-ecg.edf) is the PDF converted to EDF

## About the example data files

The example data files are my real patient health information.

- I'm sharing this with the public for research purposes.

## How to convert from PDF to EDF

We are researching how to convert the data file format from PDF to EDF, for the purpose of interoperability with other programs.

We are doing work in progress on two implementations: o

- A Python script that is intended to be easy to read and edit

- A Rust crate that is intended to be faster and more efficience

Comparison:

┌───────────────────┬───────────────────────────────┬──────────────────────────────────────────────────────────────────────┐
│ Component │ Python (pymupdf + pyedflib) │ Rust (lopdf + manual EDF) │
├───────────────────┼───────────────────────────────┼──────────────────────────────────────────────────────────────────────┤
│ PDF parsing │ pymupdf.get_drawings() │ lopdf::Content::decode() with manual operator parsing │
├───────────────────┼───────────────────────────────┼──────────────────────────────────────────────────────────────────────┤
│ Path extraction │ High-level drawing dict │ Parse m/l/S operators, track w (line width) via graphics state stack │
├───────────────────┼───────────────────────────────┼──────────────────────────────────────────────────────────────────────┤
│ Coordinate system │ PyMuPDF returns screen coords │ Raw PDF ops inside 1 0 0 -1 0 792 cm are already screen coords │
├───────────────────┼───────────────────────────────┼──────────────────────────────────────────────────────────────────────┤
│ EDF writing │ pyedflib.EdfWriter │ Manual EDF header + 16-bit LE data records │
└───────────────────┴───────────────────────────────┴──────────────────────────────────────────────────────────────────────┘

## Finally

Notes:

- Use this work at your own risk.

- Constructive feedback welcome.

These repositories are all related work:

- [kardiamobile-personal-health-information](https://github.com/joelparkerhenderson/kardiamobile-personal-health-information)

- [kardiamobile-1l-ecg-convert-pdf-to-edf-python](https://github.com/joelparkerhenderson/kardiamobile-1l-ecg-convert-pdf-to-edf-python)

- [kardiamobile-1l-ecg-convert-pdf-to-edf-rust-crate](https://github.com/joelparkerhenderson/kardiamobile-1l-ecg-convert-pdf-to-edf-rust-crate)

- [kardiamobile-6l-ecg-convert-pdf-to-edf-python](https://github.com/joelparkerhenderson/kardiamobile-1l-ecg-convert-pdf-to-edf-python)

- [kardiamobile-6l-ecg-convert-pdf-to-edf-rust-crate](https://github.com/joelparkerhenderson/kardiamobile-6l-ecg-convert-pdf-to-edf-rust-crate)

Disclaimers:

- This work is independent for the purpose of interoperability with other programs.

- This work is not by the company AliveCor, makers of the Karida devices, apps, and services.

- AliveCor and Kardia are trademarks of AliveCor, Inc. in the United States and other countries.

Tracking:

- Package: kardiamobile-personal-health-information
- Version: 0.1.0
- Created: 2026-02-23T22:41:21Z
- Updated: 2026-02-23T22:41:21Z
- License: MIT or Apache-2.0 or GPL-2.0 or GPL-3.0 or contact us for more
- Contact: Joel Parker Henderson <joel@joelparkerhenderson.com>
