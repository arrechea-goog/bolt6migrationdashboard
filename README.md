# Bolt6 AWS-to-GCP Cloud TCO Architectural Assessment (`app.py`)

An interactive **Python Streamlit web application** designed to provide an executive architectural re-evaluation of the cloud infrastructure scenarios in `EXTERNAL-Bolt6-Cloud-Comparison.xlsx`. The application incorporates official **AWS and Google Cloud Platform (GCP)** vector logos across all charts, scorecard headings, and engineering benchmarks.

---

## ✨ Executive Summary: Expanding the Value Beyond the Preliminary $24K Delta

The preliminary comparison report estimated a **$23,624 ($24k)** annual savings gap between **AWS Structurally Optimized ($912,466/yr)** and **GCP Hybrid ($888,842/yr)**—falling within an internal **$50,000 evaluation window**.

By incorporating Bolt6's actual workload telemetry and modern GPU capabilities, this dashboard illustrates three structural value opportunities that widen the annual savings advantage on GCP:

### 1. Opportunity #1: High-Density GPU Mapping (`g4-standard` RTX 6000 Pro vs. Preliminary `g2`)
- **Preliminary Top-Down Model:** Evaluated GCP `g2-standard` (L4) instances at standard list price.
- **Production Architectural Model (`bolt6 - GPU Pricing Model`):** Maps optical tracking workloads to **GCP `g4-standard` (RTX 6000 Pro)** and **`g7e` Multi-Instance GPU (MIG)** series.
- **Value Impact:** GCP `g4-standard` delivers **120 TFLOPS FP32**—**3.85x higher throughput** than AWS A10G (`31.2 TFLOPS`) at a **63% lower cost per TFLOP**, unlocking **+$148,604/yr** in consolidation efficiency.

### 2. Opportunity #2: Dynamic GPU Partitioning & Cloud Run GPUs for Peak Tournaments
- **Preliminary Top-Down Model:** Annualized the January 2026 Australian Open peak ($439,274 burst) across the recurring baseline. On AWS, static 24/7 EC2 GPU provisioning generated a **$439k single-month spend**.
- **The GCP Cloud Run GPU Advantage:** By switching to **Cloud Run Serverless L4 GPUs**, compute scales to 0 ($0.00/sec) outside active match broadcast hours, dropping the January tournament cost from **$439,274 to $138,500**—a **$300,774 (68.5%) cost reduction in a single month**.
- **MIG Hardware Slicing:** Google Cloud's **Multi-Instance GPU (MIG)** technology slices physical L4 and RTX 6000 GPUs into isolated hardware slices (`1/2`, `1/4`, `1/8`), right-sizing peak workload demand and reclaiming **+$110,532/yr** in broadcast headroom.

### 3. Opportunity #3: Serverless & Container GPU Autoscaling (Cloud Run & GKE Autopilot)
- **The Challenge:** Sports broadcasts occur in highly episodic windows (~2–4 hour live events). Static AWS EC2 VMs bill 24/7 during off-peak hours.
- **Cloud Run (Serverless NVIDIA L4):** Scales down to **0 instances ($0.00/hr)** between live matches, billing strictly per second during active HTTP/gRPC frame requests.
- **GKE Autopilot GPU Autoscaling:** Integrates Horizontal Pod Autoscaling (HPA) with Google Kubernetes Engine to dynamically scale container workloads based on traffic demand during live match windows.
- **Value Impact:** Match-window GPU autoscaling reclaims an additional **+$135,000/yr** in off-peak operating spend.

### 4. Refined Executive Scorecard & Waterfall Path
When all three architectural levers are enabled in the sidebar, the annual GCP savings advantage expands from **$23,624 ($24k)** to **$417,760 per year**—**8.4x greater than the $50K evaluation threshold**.

---

## 🚀 Launching the Interactive Web App

```bash
cd /usr/local/google/home/arrechea/Bolt6migration
pip install -r requirements.txt
streamlit run app.py
```
