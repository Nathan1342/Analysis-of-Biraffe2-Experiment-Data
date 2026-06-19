import numpy as np
import pandas as pd
import os
from scipy.signal import butter, filtfilt, find_peaks
from glob import glob

# =====================================================
# CONFIG
# =====================================================
BIOSIG_DIR = r"C:\Pulpit\BIRAFFE2-biosigs"
PROC_DIR    = r"C:\Pulpit\BIRAFFE2-procedure"

FS = 1000
BASELINE_MS = 60 * 1000

# =====================================================
# FILTER
# =====================================================
def butter_filter(data, low=None, high=None, fs=1000, order=4):
    nyq = 0.5 * fs

    if low and high:
        b, a = butter(order, [low / nyq, high / nyq], btype='band')
    elif low:
        b, a = butter(order, low / nyq, btype='high')
    elif high:
        b, a = butter(order, high / nyq, btype='low')
    else:
        return data

    # keep peaks at correct positions
    return filtfilt(b, a, data)


# =====================================================
# FEATURE EXTRACTION
# =====================================================
def extract_features(biosig_path, proc_path):

    # loading data to pd dataframes
    biosig = pd.read_csv(biosig_path, low_memory=False)
    proc = pd.read_csv(proc_path, sep=';', low_memory=False)

    # converting timestamps into numeric values
    biosig["TIMESTAMP"] = pd.to_numeric(biosig["TIMESTAMP"], errors="coerce")
    proc["TIMESTAMP"] = pd.to_numeric(proc["TIMESTAMP"], errors="coerce")

    baseline_events = proc[proc["EVENT"].str.contains("baseline", case=False, na=False)]
    if len(baseline_events) == 0:
        return None

    start = baseline_events["TIMESTAMP"].iloc[0]
    end = start + BASELINE_MS

    window = biosig[
        (biosig["TIMESTAMP"] >= start) &
        (biosig["TIMESTAMP"] <= end)
    ]

    # guard: empty window
    if len(window) < FS * 10:
        return None

    ecg = window["ECG"].values
    eda = window["EDA"].values

    # =================================================
    # ECG PROCESSING (improved)
    # =================================================
    ecg_f = butter_filter(ecg, low=0.5, high=40, fs=FS)

    # enhance QRS -> peak of ecg heartbeat
    # taking derivative -> highlighting rapid changes
    ecg_f = np.diff(ecg_f, prepend=ecg_f[0])
    # squaring to make peaks dominate
    ecg_f = ecg_f ** 2

    # adaptive treshold for finding peaks (more stable)
    # higher noise -> higher treshold for peaks
    prom = 0.5 * np.std(ecg_f)

    peaks, _ = find_peaks(
        ecg_f,
        distance=int(0.35 * FS),
        prominence=prom
    )

    # computing rr peaks -> time between heartbeat
    rr = np.diff(peaks) / FS

    # physiological filtering
    rr = rr[(rr > 0.3) & (rr < 2.0)]

    # guard: too few valid beats
    if len(rr) < 8:
        mean_hr = np.nan
        sdnn = np.nan
        rmssd = np.nan
        pnn50 = np.nan
    else:
        # converting rr in second to rr in miliseconds
        rr_ms = rr * 1000.0

        # calculating heartbeats per minute
        mean_hr = 60.0 / np.mean(rr)

        # HRV time-domain features
        # Standard deviation of time intervals between consecutive heartbeats.
        sdnn = np.std(rr_ms, ddof=1)
        # Measures short-term variability between adjacent heartbeats.
        rmssd = np.sqrt(np.mean(np.diff(rr_ms) ** 2))

        diff_rr = np.abs(np.diff(rr_ms))
        # Percentage of successive heartbeat intervals that differ by more than 50 ms.
        pnn50 = (np.sum(diff_rr > 50) / len(diff_rr)) * 100 if len(diff_rr) > 0 else np.nan
    # quality flag (more informative)
    quality_flag = (
        "OK" if len(rr) >= 20 and np.std(rr * 1000) < 300
        else "CHECK"
    )

    # =================================================
    # EDA PROCESSING
    # =================================================
    eda_f = butter_filter(eda, high=1.0, fs=FS)
    # tonic eda -> background slowly changing baseline -> drift
    tonic = butter_filter(eda_f, high=0.05, fs=FS)
    # phasic eda -> short-term rapid spikes (SCR)
    phasic = eda_f - tonic

    thr = np.mean(phasic) + 2.5 * np.std(phasic)

    scr_peaks, _ = find_peaks(
        phasic,
        height=thr,
        distance=int(1.5 * FS)
    )

    scr_count = len(scr_peaks)
    scr_amp = np.mean(phasic[scr_peaks]) if scr_count > 0 else 0.0

    scl_mean = np.mean(tonic)
    scl_slope = np.polyfit(np.arange(len(tonic)), tonic, 1)[0]

    subject_id = os.path.basename(biosig_path).split("-")[0].replace("SUB", "")

    return {
        "ID": subject_id,
        "mean_HR_bpm": mean_hr,
        "SDNN_ms": sdnn,
        "RMSSD_ms": rmssd,
        "pNN50": pnn50,
        "SCL_mean": scl_mean,
        "SCL_slope": scl_slope,
        "SCR_count": scr_count,
        "SCR_mean_amp": scr_amp,
        "quality_flag": quality_flag
    }


# =====================================================
# BATCH RUN
# =====================================================
biosig_files = sorted(glob(os.path.join(BIOSIG_DIR, "SUB*-BioSigs.csv")))

results = []

for bfile in biosig_files:
    sid = os.path.basename(bfile).split("-")[0]
    pfile = os.path.join(PROC_DIR, f"{sid}-Procedure.csv")

    if not os.path.exists(pfile):
        continue

    feat = extract_features(bfile, pfile)
    if feat:
        results.append(feat)


# =====================================================
# SAVE
# =====================================================
df = pd.DataFrame(results)
df.to_csv("ALL_SUBJECTS_FEATURES.csv", index=False)

print("Saved → ALL_SUBJECTS_FEATURES.csv")