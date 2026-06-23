# A-Mark Absence Escalation & Early Completion Analysis Dashboard
## System Documentation & Walkthrough

This document outlines the full architecture, capabilities, mathematical algorithms, and interactive features of the A-Mark Analysis Dashboard. This dashboard is designed for educational administrators to detect early course completions, study leave spikes, and escalations in student absence dynamics across departments and course sections.

---

## 1. Core System Architecture
The application runs as a lightweight, single-page client-side web app styled with premium glassmorphism design tokens (dark mode, translucent cards, Outfit typography) and relies on the following key libraries:
* **SheetJS (`xlsx.full.min.js`)**: For client-side parsing of uploaded `.csv` student attendance records.
* **Chart.js (`chart.js`)**: For plotting responsive, canvas-rendered lines and bar charts.

---

## 2. Data Processing & Academic Calendar Mapping
The raw sheet contains attendance data aligned to standard calendar weeks. The dashboard refactors this data into a standardized **40-Week Academic Calendar** to ignore scheduled holidays and prevent false positive reports.

### Calendar Exclusions & Mappings
* **Ignored Pre-Term Weeks**: Weeks 1 to 5 (before term starts) are ignored.
* **Excluded Holidays**:
  * **Week 13**: October Half Term
  * **Weeks 21–22**: December/Christmas Break
  * **Week 29**: February Half Term
  * **Weeks 36–37**: Easter Break
  * **Week 43**: May Half Term
* **Two-Way Mapping**: The app establishes `ACADEMIC_TO_CALENDAR` and `CALENDAR_TO_ACADEMIC` arrays to map calendar weeks to consecutive academic weeks (1–40).
* **FT Course Filtering**: Only rows corresponding to Full-Time (FT) courses are analyzed (e.g., matching common codes and headers like `TOTAL A_MARKS`).

---

## 3. Mathematical Algorithms & Analysis

### A. Analysis Cutoff Week
To handle mid-year analysis, an **Analysis Cutoff Week** slider (defaulting to week 46 calendar / week 34 academic) truncates all calculations. Any data points beyond the cutoff are ignored, and line charts stop drawing exactly at this point.

### B. Change-Point Detection Algorithm
The dashboard scans each course's normalized weekly timeline $P_w$ (weekly absences divided by the maximum absences recorded up to the cutoff week) to detect step-up points:
1. **Baseline Average**: Computes the average normalized absence rate over a configured history window ($W_{Baseline}$):
   $$\text{Avg}_{\text{Before}} = \frac{1}{W_{Baseline}} \sum_{j=i-W_{Baseline}}^{i-1} P_j$$
2. **Comparison Average**: Computes the average over a subsequent comparison window ($W_{Comparison}$):
   $$\text{Avg}_{\text{After}} = \frac{1}{W_{Comparison}} \sum_{j=i}^{i+W_{Comparison}-1} P_j$$
3. **Change Score**: Evaluates the difference (escalation score):
   $$\text{Change Score} = \text{Avg}_{\text{After}} - \text{Avg}_{\text{Before}}$$
4. **Step-Up Validation**: A course is flagged if:
   * $\text{Change Score} \ge \text{Min Increase Threshold}$
   * $\text{Avg}_{\text{After}} \ge \text{Post-Increase Level Threshold}$
   * Absences remain at or above a sustained level for a minimum number of weeks within the comparison window.

### C. False Positive Safeguards & Confidence Ratings
Courses matching the change-point criteria are assessed by a confidence logic engine to rule out common false positives (GCSE exam revision, work placements, low student volume):
* **High Confidence**: The change-point remains highly sustained (average $\ge 70\%$ at the end of the year) with no subsequent drops.
* **Medium Confidence**: Sustained at the end of the year, but has brief drop-backs, falls inside the designated academic exam period, or has low maximum absences ($< 3$ absences in a single week).
* **Low Confidence**: Drop-backs exceed 2 weeks, final week absences drop below 50%, the step-up begins very late in the year, or multiple cyclic spikes are detected (cyclical placements).
* **Written Justifications**: Every flagged course is accompanied by clear text explanations detailing the step-up magnitude and specific caution flags.

---

## 4. Visualizations & Interactive Panels

### Tab 1: Flagged Courses & Course Visualizer
1. **Interactive Results Table**:
   * Displays all flagged and unflagged courses with search and sorting controls.
   * Clicking a row displays the course's detail card and plots its timeline on the right-hand panel.
   * **CSV Export**: Provides single-click exporting of filtered flagged tables.
2. **Course Visualizer**:
   * Plots the selected course's absolute weekly absences (bar chart) and its normalized profile against the overall department/section average (line chart).
   * Annotates Term Breaks (Easter, May Half Term) with staggered vertical dashed lines.
   * Provides a "Return to Overview" button to switch back to the aggregate statistics chart.
3. **PDF Export**:
   * Generates a high-quality print-formatted report.
   * If a course is selected: Compiles course metadata, step-up justification logs, false-positive caution checklists, active slider settings, and the course timeline chart.
   * If no course is selected: Compiles division overview statistics, aggregate charts, a full flagged course table, and active slider settings.
   * Generates base64 PNG snapshots of charts client-side and triggers the browser print dialog.

### Tab 2: Absence Trends & Section Insights
1. **Flag Distribution by Week**:
   * Bar chart and table displaying the weeks in which courses transitioned to elevated absences.
   * **Interactivity**: Clicking any bar in the chart or row in the table opens the **Flagged Courses Details Panel** below, showing the list of courses flagged in that week.
   * **Cumulative %**: Replaces simple weekly rates with a cumulative percentage representing the rolling proportion of all courses that have been flagged up to that week.
   * **Cross-Tab Navigation**: Clicking a course in the drill-down panel automatically switches tabs, selects the course, and displays its detail chart.
2. **Section-Level Absence Trends**:
   * Plots the average weekly profile for all course sections.
   * **Legend Isolation**: Clicking a section in the chart legend isolates its line and filters the statistical outlier tests.
3. **Statistical Significance Outlier Testing (Welch's t-test)**:
   * Run at the section level, comparing the selected section against all other sections combined.
   * Evaluates three normalized percentage metrics for fairer comparisons:
     1. **Mean Total Absences (% of Max)**: Sum of absences divided by `maxWeeklyAMarks * Cutoff Weeks`.
     2. **Mean Post-Increase Level (% of Max)**: Average post-step-up absence level.
     3. **Mean Change Score (Escalation %)**: Step-up magnitude.
   * **Welch–Satterthwaite Equation**: Calculates degrees of freedom without assuming equal variances.
   * **Simpson's Rule CDF Integration**: Computes precise two-tailed p-values using Lanczos Gamma approximation to provide color-coded verdicts (`p < 0.05` highlights significantly higher/lower outliers).

---

## 5. Getting Started & Setup
1. **Run Local Server**: Launch a simple Python web server inside the directory:
   ```bash
   python3 serve.py
   ```
2. **Load Web Interface**: Open `http://localhost:8000/amark_analysis.html` in a web browser.
3. **Load Demo Data**: Click **Load Synthetic Demo Data** to populate the dashboard with simulated data representing different absence profiles, or upload your own student attendance CSV.
4. **Drill Down**: Filter sections using the chart legend or dropdowns, and inspect outliers in the statistical testing card.

---

## 6. Theme Settings (Light & Dark Modes)
* **Default Mode**: The dashboard defaults to a clean, bright Light Mode on first load for high visibility in typical office/meeting environments.
* **Theme Switching**: A theme toggle button (featuring moon/sun SVG icons) in the sidebar header switches between Light and the original dark glassmorphism aesthetic.
* **Persistence**: Theme settings are stored in the browser's `localStorage` and read by an inline blocking script immediately below the body tag, eliminating visual page flickering on refresh.
* **Dynamic Chart Color Matching**: Chart.js labels, grid lines, tooltips, and background elements dynamically repaint when the theme changes to ensure optimal contrast in both modes.
