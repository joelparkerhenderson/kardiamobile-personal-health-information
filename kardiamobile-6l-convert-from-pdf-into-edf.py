#!/usr/bin/env python3
"""
KardiaMobile 6-lead file format converter from Kardia ECG PDF to EDF.

This script reads the vector path data embedded in the PDF, converts
the path coordinates to voltage values using the known calibration
(10mm/mV, 25mm/s), and writes the result as a standard EDF file.

Metadata extracted from PDF:
  - Patient: Joel Henderson
  - DOB: 5/4/70, Sex: Male, Age: 55
  - Recorded: 2026-02-23 at 18:26:56
  - Heart Rate: 87 BPM
  - Duration: 30s
  - 6 leads: I, II, III, aVR, aVL, aVF
  - Sampling rate: 300 Hz
  - Kardia Determination: Normal Sinus Rhythm
"""

from datetime import datetime

import numpy as np
import pyedflib
import pymupdf


def extract_baselines(page):
    """Extract the baseline y-coordinates for each lead from grid lines."""
    paths = page.get_drawings()
    for path in paths:
        items = path.get("items", [])
        color = path.get("color")
        width = path.get("width", 0)
        # The baseline path has many horizontal lines and width ~0.4
        if (
            color == (0.0, 0.0, 0.0)
            and width is not None
            and 0.35 < width < 0.45
            and len(items) >= 6
        ):
            # Check if all items are horizontal lines spanning the page
            y_values = []
            for item in items:
                if item[0] == "l":
                    p1, p2 = item[1], item[2]
                    if abs(p1.y - p2.y) < 0.01 and abs(p2.x - p1.x) > 500:
                        y_values.append(p1.y)
            if len(y_values) >= 6:
                return y_values[:6]  # First 6 baselines = 6 leads
    return None


def extract_ecg_paths_from_page(page, baselines):
    """Extract ECG waveform points for each lead from a single page.

    Returns dict: lead_index -> list of (x, y) points sorted by x.
    """
    paths = page.get_drawings()
    leads = {i: [] for i in range(6)}

    for path in paths:
        color = path.get("color")
        width = path.get("width", 0)
        items = path.get("items", [])

        # ECG waveform paths: black, width ~0.4, many line segments
        if (
            color != (0.0, 0.0, 0.0)
            or width is None
            or not (0.35 < width < 0.45)
            or len(items) < 50
        ):
            continue

        # Extract points from line segments
        points = []
        for item in items:
            if item[0] == "l":
                p1, p2 = item[1], item[2]
                if (
                    not points
                    or abs(points[-1][0] - p1.x) > 0.001
                    or abs(points[-1][1] - p1.y) > 0.001
                ):
                    points.append((p1.x, p1.y))
                points.append((p2.x, p2.y))

        if not points:
            continue

        # Determine which lead by y-center proximity to baselines
        y_center = np.mean([p[1] for p in points])
        min_dist = float("inf")
        best_lead = -1
        for li, bl in enumerate(baselines):
            dist = abs(y_center - bl)
            if dist < min_dist:
                min_dist = dist
                best_lead = li

        if best_lead >= 0 and min_dist < 50:
            leads[best_lead].extend(points)

    # Sort each lead's points by x-coordinate
    for li in leads:
        leads[li].sort(key=lambda p: p[0])

    return leads


def points_to_voltage(points, baseline_y, cal_pt_per_mv):
    """Convert (x, y) points to voltage values in millivolts.

    In the PDF, y increases downward, so voltage = (baseline - y) / scale.
    """
    voltages = [(baseline_y - y) / cal_pt_per_mv for _, y in points]
    return voltages


def main():
    pdf_path = "/Users/jph/git/joelparkerhenderson/kardiamobile-personal-health-information/kardiamobile-6-lead-ecg.pdf"
    edf_path = "/Users/jph/git/joelparkerhenderson/kardiamobile-personal-health-information/kardiamobile-6-lead-ecg.edf"

    doc = pymupdf.open(pdf_path)

    # Calibration: 1 mV = 28.346 PDF points (10mm at 2.8346 pt/mm)
    CAL_PT_PER_MV = 28.346
    SAMPLE_RATE = 300  # Hz
    LEAD_NAMES = ["I", "II", "III", "aVR", "aVL", "aVF"]

    # Extract baselines from page 2 (index 1)
    baselines = extract_baselines(doc[1])
    if not baselines:
        raise RuntimeError("Could not find baseline grid lines in PDF")

    print(f"Baselines (PDF y-coordinates): {[f'{b:.3f}' for b in baselines]}")

    # Extract waveforms from all ECG pages (pages 2-5, indices 1-4)
    all_leads = {i: [] for i in range(6)}
    for pg_idx in range(1, 5):
        page = doc[pg_idx]
        page_leads = extract_ecg_paths_from_page(page, baselines)
        for li in range(6):
            all_leads[li].extend(page_leads[li])

    doc.close()

    # Convert to voltage arrays
    lead_voltages = {}
    for li in range(6):
        points = all_leads[li]
        # Remove duplicate x-coordinates (boundary points between segments)
        deduped = [points[0]]
        for i in range(1, len(points)):
            if abs(points[i][0] - deduped[-1][0]) > 0.01:
                deduped.append(points[i])
        voltages = points_to_voltage(deduped, baselines[li], CAL_PT_PER_MV)
        lead_voltages[li] = np.array(voltages, dtype=np.float64)
        print(
            f"Lead {LEAD_NAMES[li]:3s}: {len(voltages)} samples, "
            f"range [{min(voltages):.3f}, {max(voltages):.3f}] mV"
        )

    # Ensure all leads have the same length (trim to shortest)
    min_len = min(len(lead_voltages[li]) for li in range(6))
    for li in range(6):
        lead_voltages[li] = lead_voltages[li][:min_len]

    duration_sec = min_len / SAMPLE_RATE
    print(f"\nTotal samples per lead: {min_len}")
    print(f"Duration: {duration_sec:.2f} seconds")
    print(f"Sampling rate: {SAMPLE_RATE} Hz")

    # Write EDF file
    n_channels = 6
    edf_writer = pyedflib.EdfWriter(
        edf_path, n_channels, file_type=pyedflib.FILETYPE_EDFPLUS
    )

    # Patient and recording info
    edf_writer.setPatientName("Joel_Henderson")
    edf_writer.setSex(1)  # 1 = male
    edf_writer.setBirthdate(datetime(1970, 5, 4).date())
    edf_writer.setStartdatetime(datetime(2026, 2, 23, 18, 26, 56))
    edf_writer.setEquipment("KardiaMobile_6L")
    edf_writer.setRecordingAdditional("Normal_Sinus_Rhythm_HR_87_BPM")

    # Configure channels
    for li in range(n_channels):
        edf_writer.setLabel(li, f"EKG {LEAD_NAMES[li]}")
        edf_writer.setPhysicalDimension(li, "mV")
        edf_writer.setSamplefrequency(li, SAMPLE_RATE)
        edf_writer.setTransducer(li, "KardiaMobile 6L electrode")
        edf_writer.setPrefilter(li, "Enhanced Filter, 50Hz mains")

        # Set physical min/max from actual data with margin
        phys_min = float(np.min(lead_voltages[li])) - 0.1
        phys_max = float(np.max(lead_voltages[li])) + 0.1
        edf_writer.setPhysicalMinimum(li, phys_min)
        edf_writer.setPhysicalMaximum(li, phys_max)
        edf_writer.setDigitalMinimum(li, -32768)
        edf_writer.setDigitalMaximum(li, 32767)

    # Write data
    edf_writer.writeSamples([lead_voltages[li] for li in range(n_channels)])
    edf_writer.close()

    print(f"\nEDF file written: {edf_path}")
    print(f"File size: {__import__('os').path.getsize(edf_path):,} bytes")


if __name__ == "__main__":
    main()
