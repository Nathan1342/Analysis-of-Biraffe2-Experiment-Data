# Personality and Baseline Physiological Responses

## Overview

This project investigates whether personality traits are associated with physiological activity during the baseline phase of the BIRAFFE2 experiment.

The analysis combines:

* Electrocardiography (ECG) signals
* Electrodermal Activity (EDA) signals
* Big Five personality trait scores

Physiological features are extracted from the first 60 seconds of the baseline period for each participant and merged with personality questionnaire data. The resulting dataset is used to explore relationships between individual differences in personality and autonomic nervous system activity.

---

## Research Question

**Does personality influence physiological responses during the initial baseline phase of an experiment?**

More specifically:

* Do individuals with different personality profiles exhibit different heart rate patterns?
* Are there differences in heart rate variability (HRV)?
* Are certain personality traits associated with higher or lower electrodermal activity?

---

## Dataset

The project uses two data sources for each participant:

### BioSignals

Continuous physiological recordings:

* ECG (Electrocardiography)
* EDA (Electrodermal Activity)

### Procedure Logs

Experimental event markers used to identify the beginning of the baseline period.

Only the first 60 seconds following the baseline event are analyzed.

---

## Signal Processing Pipeline

### 1. Baseline Extraction

The program:

1. Loads physiological recordings.
2. Finds the first event containing the word `"baseline"`.
3. Extracts a 60-second analysis window.

Participants with missing baseline events or insufficient signal length are excluded.

---

## ECG Processing

### Filtering

ECG signals are band-pass filtered between:

* 0.5 Hz
* 40 Hz

using a 4th-order Butterworth filter.

This removes:

* Baseline drift
* High-frequency noise

while preserving cardiac activity.

---

### R-Peak Detection

To identify heartbeats:

1. The ECG signal is differentiated.
2. The result is squared.
3. Peaks are detected using an adaptive prominence threshold.

This procedure enhances QRS complexes and improves heartbeat detection.

---

### RR Intervals

RR intervals represent the time between consecutive heartbeats.

Only physiologically plausible intervals are retained:

* Minimum: 300 ms
* Maximum: 2000 ms

---

## ECG Features

### Mean Heart Rate (mean_HR_bpm)

Average heart rate during baseline.

Formula:

HR = 60 / mean(RR)

Units:

* Beats per minute (bpm)

Interpretation:

* Higher values may indicate greater physiological activation.
* Lower values often reflect a more relaxed resting state.

---

### SDNN (SDNN_ms)

Standard deviation of all normal RR intervals.

Formula:

SDNN = SD(RR intervals)

Units:

* Milliseconds (ms)

Measures:

* Overall heart rate variability.

Interpretation:

* Higher SDNN generally reflects greater flexibility of autonomic regulation.
* Lower SDNN may indicate reduced physiological adaptability.

---

### RMSSD (RMSSD_ms)

Root Mean Square of Successive Differences between adjacent RR intervals.

Formula:

RMSSD = sqrt(mean(diff(RR)^2))

Units:

* Milliseconds (ms)

Measures:

* Short-term heart rate variability.

Interpretation:

* Strongly associated with parasympathetic (vagal) activity.
* Higher RMSSD typically reflects stronger vagal regulation and better recovery capacity.

---

### pNN50

Percentage of adjacent RR intervals differing by more than 50 ms.

Formula:

pNN50 = (Number of RR differences > 50 ms / Total RR differences) × 100

Units:

* Percent (%)

Measures:

* Beat-to-beat variability.

Interpretation:

* Higher values indicate greater short-term variability.
* Often considered another marker of parasympathetic influence.

---

## ECG Quality Control

A recording receives:

### OK

when:

* At least 20 valid RR intervals exist
* RR interval standard deviation < 300 ms

### CHECK

otherwise.

This helps identify recordings that may contain excessive noise or peak detection errors.

---

## EDA Processing

Electrodermal Activity reflects changes in skin conductance caused by sweat gland activity and sympathetic nervous system activation.

### Filtering

EDA signals are low-pass filtered at:

* 1 Hz

to remove high-frequency noise.

---

### Tonic Component

A second low-pass filter (0.05 Hz) is applied to estimate the slowly changing baseline level.

This component is called:

**Skin Conductance Level (SCL)**

and represents general physiological arousal.

---

### Phasic Component

The phasic component is obtained by:

Phasic = EDA − Tonic

This isolates rapid fluctuations known as Skin Conductance Responses (SCRs).

---

## EDA Features

### SCL_mean

Average tonic skin conductance during baseline.

Measures:

* Overall sympathetic arousal.

Interpretation:

* Higher values suggest higher baseline physiological activation.
* Lower values indicate lower resting arousal.

---

### SCL_slope

Linear trend of tonic skin conductance over time.

Measures:

* Whether arousal increases or decreases during baseline.

Interpretation:

* Positive slope → increasing arousal.
* Negative slope → decreasing arousal or adaptation.

---

### SCR_count

Number of detected Skin Conductance Responses.

Detection threshold:

Mean(phasic) + 2.5 × SD(phasic)

Measures:

* Frequency of sympathetic activation events.

Interpretation:

* Higher counts suggest more spontaneous autonomic reactions.

---

### SCR_mean_amp

Average amplitude of detected SCR peaks.

Measures:

* Strength of electrodermal responses.

Interpretation:

* Larger amplitudes indicate stronger sympathetic activation.

---

## Personality Variables

The analysis uses the Big Five personality dimensions:

* Openness
* Conscientiousness
* Extraversion
* Agreeableness
* Neuroticism

These variables are examined in relation to physiological measures.

---

## Exploratory Data Analysis

The project includes:

### Dataset Overview

* Gender distribution
* Personality score distributions

### Correlation Analysis

Heatmaps showing associations between:

* Personality traits
* ECG features
* EDA features

### Trait-by-Trait Visualization

Regression plots for every combination of:

* Personality trait
* Physiological measure

including Pearson correlation coefficients.

### Sex Differences

Boxplots and individual participant distributions for:

* RMSSD
* SCL

to explore potential physiological differences between male and female participants.

---

## Technologies Used

* Python
* NumPy
* Pandas
* SciPy
* Seaborn
* Matplotlib

---

## Output

The feature extraction pipeline generates:

`ALL_SUBJECTS_FEATURES.csv`

containing one row per participant and the extracted physiological features.

The visualization pipeline produces exploratory figures used for hypothesis generation and interpretation.

---

## Disclaimer

This project is intended as an exploratory analysis of psychophysiological data. Observed correlations should not be interpreted as causal relationships. Statistical significance testing and replication would be required to draw strong scientific conclusions.
