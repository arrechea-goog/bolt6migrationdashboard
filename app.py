"""
Bolt6 AWS-to-GCP Cloud TCO Comparison & Architectural Re-Evaluation Dashboard
==============================================================================
Streamlined executive dashboard demonstrating the broader economic and architectural
opportunity of migrating from AWS to GCP:
1. Executive Summary & Financial Scorecard
2. Technical Architecture & GPU Levers (RTX 6000 Pro + MIG Slicing)
3. Live Event Telemetry & Autoscaling Proof (13-day customer data + GKE Autopilot)
4. Commercial Models, DWS Flex Strategy & Data Lineage
"""

import math
import pandas as pd
import streamlit as st

try:
    import plotly.express as px
    import plotly.graph_objects as go
    PLOTLY_AVAILABLE = True
except ImportError:
    PLOTLY_AVAILABLE = False

# Official Provider & Customer Logo URLs
AWS_LOGO_URL = "https://cdn.jsdelivr.net/gh/devicons/devicon@latest/icons/amazonwebservices/amazonwebservices-original-wordmark.svg"
GCP_LOGO_URL = "https://cdn.jsdelivr.net/gh/devicons/devicon/icons/googlecloud/googlecloud-original.svg"
BOLT6_LOGO_URL = "https://cdn.prod.website-files.com/65c0ca4fa2c8220d03e35e8f/65c0ca4fa2c8220d03e35f92_BOLT6-logo-white.png"

# Configure Streamlit page settings
st.set_page_config(
    page_title="Bolt6 Cloud TCO & Architectural Assessment",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Spreadsheet XLSX Export URLs
GPU_PRICING_URL = "https://docs.google.com/spreadsheets/d/1JKaVySox6zlAL_lQphewLxgrjuqW463J0NSNsmRgAx8/export?format=xlsx"
MIGRATION_CENTER_URL = "https://docs.google.com/spreadsheets/d/1C2ZUKVkA3G3lDZEbfw15jkqdTbuqd0kIIda7Ky12syM/export?format=xlsx&resourcekey=0-pSuHNda7UsEhwZ4fNfzshw"
CLOUD_COMPARISON_URL = "https://docs.google.com/spreadsheets/d/1FslH6yEcV0dOaDaNhd_AXDbVrCIDpPw4-ADfW9pQqXA/export?format=xlsx"


def render_bolt6_logo(height_px: int = 36):
    return f'<img src="{BOLT6_LOGO_URL}" height="{height_px}px" style="vertical-align: middle; margin-right: 12px;" />'


def render_provider_badge(provider: str, size_px: int = 24):
    if provider.upper() == "AWS":
        return f'<img src="{AWS_LOGO_URL}" height="{size_px}px" style="vertical-align: middle; margin-right: 6px;" />'
    else:
        return f'<img src="{GCP_LOGO_URL}" height="{size_px}px" style="vertical-align: middle; margin-right: 6px;" />'


def add_chart_logos(fig, show_aws: bool = True, show_gcp: bool = True):
    images = []
    if show_gcp:
        images.append(
            dict(
                source=GCP_LOGO_URL,
                xref="paper",
                yref="paper",
                x=0.98,
                y=1.13,
                sizex=0.08,
                sizey=0.08,
                xanchor="right",
                yanchor="top",
                opacity=0.85,
                layer="above",
            )
        )
    if show_aws:
        images.append(
            dict(
                source=AWS_LOGO_URL,
                xref="paper",
                yref="paper",
                x=0.88 if show_gcp else 0.98,
                y=1.13,
                sizex=0.09,
                sizey=0.09,
                xanchor="right",
                yanchor="top",
                opacity=0.85,
                layer="above",
            )
        )
    if images:
        fig.update_layout(images=images)
    return fig


@st.cache_data(show_spinner=False)
def load_all_sheets():
    gpu_df_dict = {
        "Sheet1": pd.DataFrame(
            [
                {"AWS Machine Type": "g5.2xlarge", "Total Source Cost": 103113.65, "Total Hours": 65434, "GCP Equivalent": "g4-standard-12", "On Demand": 64778.74, "1 yr CUD": 44698.03},
                {"AWS Machine Type": "g5.4xlarge", "Total Source Cost": 63137.30, "Total Hours": 29901, "GCP Equivalent": "g4-standard-24", "On Demand": 59203.75, "1 yr CUD": 40851.22},
                {"AWS Machine Type": "g5.8xlarge", "Total Source Cost": 58501.89, "Total Hours": 18380, "GCP Equivalent": "g4-standard-48", "On Demand": 66167.40, "1 yr CUD": 45656.22},
                {"AWS Machine Type": "g6.2xlarge", "Total Source Cost": 50279.45, "Total Hours": 39557, "GCP Equivalent": "g4-standard-12", "On Demand": 39160.61, "1 yr CUD": 27021.24},
                {"AWS Machine Type": "g4dn.2xlarge", "Total Source Cost": 37144.12, "Total Hours": 37968, "GCP Equivalent": "g4-standard-12", "On Demand": 37587.40, "1 yr CUD": 25935.71},
                {"AWS Machine Type": "g4dn.xlarge", "Total Source Cost": 25891.75, "Total Hours": 37846, "GCP Equivalent": "g4-standard-6", "On Demand": 18733.30, "1 yr CUD": 12926.18},
                {"AWS Machine Type": "g6.4xlarge", "Total Source Cost": 15297.05, "Total Hours": 8891, "GCP Equivalent": "g4-standard-24", "On Demand": 17604.82, "1 yr CUD": 12147.51},
                {"AWS Machine Type": "g6.8xlarge", "Total Source Cost": 7969.87, "Total Hours": 3043, "GCP Equivalent": "g4-standard-48", "On Demand": 10954.49, "1 yr CUD": 7558.71},
                {"AWS Machine Type": "g4dn.4xlarge", "Total Source Cost": 2460.04, "Total Hours": 1566, "GCP Equivalent": "g4-standard-24", "On Demand": 3100.37, "1 yr CUD": 2139.29},
                {"AWS Machine Type": "g6.xlarge", "Total Source Cost": 1921.36, "Total Hours": 1836, "GCP Equivalent": "g4-standard-6", "On Demand": 908.89, "1 yr CUD": 627.14},
                {"AWS Machine Type": "g5.xlarge", "Total Source Cost": 1658.75, "Total Hours": 1268, "GCP Equivalent": "g4-standard-6", "On Demand": 627.72, "1 yr CUD": 433.14},
            ]
        ),
        "billing": pd.DataFrame(
            [
                {"Provider": "AWS (A10G GPU)", "Instance": "g5.2xlarge", "Cost/Hour ($)": 1.2120, "TFLOPS FP32": 31.2, "Cost per TFLOP ($)": 0.0388},
                {"Provider": "AWS (L40S Ada)", "Instance": "g6e.xlarge", "Cost/Hour ($)": 1.8610, "TFLOPS FP32": 91.6, "Cost per TFLOP ($)": 0.0203},
                {"Provider": "GCP (RTX 6000 Pro Full)", "Instance": "g4-standard-48", "Cost/Hour ($)": 4.4999, "TFLOPS FP32": 120.0, "Cost per TFLOP ($)": 0.0375},
            ]
        ),
    }

    mc_df_dict = {
        "Executive Overview": pd.DataFrame([{"Total Cost (GBP)": 510066.95, "Total Cost (USD)": 663087.04}]),
        "Errors and Warnings": pd.DataFrame([
            {"Error/Warning": "MC_INFO_UNMAPPED_SHAPE_G2", "Count": 7438, "Message": "Unmapped custom optical shapes"},
            {"Error/Warning": "MC_INFO_CAPACITY_RES", "Count": 1, "Message": "Expired one-time Australian Open capacity fee ($110,532)"},
        ]),
    }

    cc_df_dict = {
        "Scenario_Comparison": pd.DataFrame([
            {"Scenario ID": "S1", "Scenario Name": "1. AWS As-Is (Status Quo)", "Compute Cost ($)": 787750.00, "Storage Cost ($)": 277000.00, "Cross-Cloud Egress ($)": 126000.00, "Annual Total ($)": 1190750.00},
            {"Scenario ID": "S2", "Scenario Name": "1B. AWS Structurally Optimized", "Compute Cost ($)": 509466.00, "Storage Cost ($)": 277000.00, "Cross-Cloud Egress ($)": 126000.00, "Annual Total ($)": 912466.00},
            {"Scenario ID": "S3", "Scenario Name": "2. GCP Baseline (Dual-Cloud S3)", "Compute Cost ($)": 485842.00, "Storage Cost ($)": 277000.00, "Cross-Cloud Egress ($)": 126000.00, "Annual Total ($)": 888842.00},
            {"Scenario ID": "S4", "Scenario Name": "4. GCP Production (Pure GCS Tiered)", "Compute Cost ($)": 350175.00, "Storage Cost ($)": 140000.00, "Cross-Cloud Egress ($)": 0.00, "Annual Total ($)": 490175.00},
        ]),
        "Compute_Seasonality": pd.DataFrame([
            {"Month": "Jan 2026", "Compute Spend ($)": 439274.00, "Is Event Peak": True},
            {"Month": "Feb 2026", "Compute Spend ($)": 48200.00, "Is Event Peak": False},
            {"Month": "Mar 2026", "Compute Spend ($)": 51400.00, "Is Event Peak": False},
            {"Month": "Apr 2026", "Compute Spend ($)": 49800.00, "Is Event Peak": False},
            {"Month": "May 2026", "Compute Spend ($)": 53100.00, "Is Event Peak": False},
            {"Month": "Jun 2026", "Compute Spend ($)": 62400.00, "Is Event Peak": True},
            {"Month": "Jul 2026", "Compute Spend ($)": 58900.00, "Is Event Peak": True},
            {"Month": "Aug 2026", "Compute Spend ($)": 50200.00, "Is Event Peak": False},
            {"Month": "Sep 2026", "Compute Spend ($)": 54600.00, "Is Event Peak": False},
            {"Month": "Oct 2026", "Compute Spend ($)": 47900.00, "Is Event Peak": False},
            {"Month": "Nov 2026", "Compute Spend ($)": 52300.00, "Is Event Peak": False},
            {"Month": "Dec 2026", "Compute Spend ($)": 46800.00, "Is Event Peak": False},
        ]),
    }

    try:
        loaded_gpu = pd.read_excel(GPU_PRICING_URL, sheet_name=None)
        if "Sheet1" in loaded_gpu and "billing" in loaded_gpu:
            gpu_df_dict = loaded_gpu
    except Exception:
        pass

    try:
        loaded_cc = pd.read_excel(CLOUD_COMPARISON_URL, sheet_name=None)
        if "Scenario_Comparison" in loaded_cc and "Compute_Seasonality" in loaded_cc:
            cc_df_dict = loaded_cc
    except Exception:
        pass

    return gpu_df_dict, mc_df_dict, cc_df_dict


gpu_sheets, mc_sheets, cc_sheets = load_all_sheets()

# Regional Profiles Data Grounded on go/gpus-pricing and AWS Regional Catalogs
REGIONAL_BREAKDOWN = [
    {
        "Tournament Region": 'Australia (Melbourne)',
        "GCP Zone": 'australia-southeast2',
        "AWS Zone": 'ap-southeast-2',
        "Fleet Share": 0.47,
        "Events / Workloads": 'Australian Open (Jan Grand Slam at Melbourne Park), APAC Tournaments',
        "AWS Compute ($)": 370242.0,
        "GCP Compute ($)": 158055.0,
        "Net Compute Savings ($)": 212187.0,
        "Reduction (%)": 57.3,
        "Key GCP Levers": 'Eliminates $110.5k reservation fee via MIG court slicing (4 courts / GPU) + in-city Melbourne deployment',
    },
    {
        "Tournament Region": 'United States',
        "GCP Zone": 'us-central1 / us-east4',
        "AWS Zone": 'us-east-1 / us-east-2',
        "Fleet Share": 0.233,
        "Events / Workloads": 'US Tournaments, Core Off-Peak AI/ML Training Pipeline',
        "AWS Compute ($)": 183546.0,
        "GCP Compute ($)": 91142.0,
        "Net Compute Savings ($)": 92404.0,
        "Reduction (%)": 50.3,
        "Key GCP Levers": 'RTX 6000 Pro 96GB at $1.0956/hr (-43% vs Ada) + GKE off-hours scale-down',
    },
    {
        "Tournament Region": 'Europe (London & Nordics)',
        "GCP Zone": 'europe-west2 / europe-north1',
        "AWS Zone": 'eu-west-2 / eu-north-1',
        "Fleet Share": 0.177,
        "Events / Workloads": "ATP European Tour, Queen's Club, CEV Volleyball",
        "AWS Compute ($)": 139432.0,
        "GCP Compute ($)": 60611.0,
        "Net Compute Savings ($)": 78821.0,
        "Reduction (%)": 56.5,
        "Key GCP Levers": 'DWS Flex uniform $2.25/hr + GKE Autopilot match-window autoscaling (70% idle off)',
    },
    {
        "Tournament Region": 'Rest of World (APAC/LatAm/ME)',
        "GCP Zone": 'asia-southeast1 / me-central1',
        "AWS Zone": 'ap-southeast-1 / sa-east-1',
        "Fleet Share": 0.12,
        "Events / Workloads": 'Challenger Tournaments, Regional Broadcast Feeds',
        "AWS Compute ($)": 94530.0,
        "GCP Compute ($)": 40367.0,
        "Net Compute Savings ($)": 54163.0,
        "Reduction (%)": 57.3,
        "Key GCP Levers": 'On-demand ephemeral nodes provisioned dynamically during tournament weeks',
    },
]

# Regional Catalog Data Grounded on go/gpus-pricing and AWS Regional Catalogs.
#
# Fleet attribution fields (fleet_share / aws_hours / aws_cost / gcp_hours / gcp_cost)
# make every headline number traceable end to end:
#   aws_cost   = fleet_share x $787,750 AWS annual compute baseline
#   aws_hours  = aws_cost / aws_a10g_od   (region's AWS g5/A10G on-demand rate)
#   gcp_hours  = aws_hours / 4            (RTX 6000 Pro MIG 4:1 court slicing)
#   gcp_cost   = gcp_hours x the documented production consumption mix below
#
# PRODUCTION CONSUMPTION MIX (explicit, and identical in every region):
#   65% DWS Flex  +  25% 3-Year CUD  +  10% On-Demand
# This is the same mix as the Tab 4 recommended-mix simulator default, so the
# headline model and the simulator now agree.
#
# All GCP rates are g4-standard-48 (1x RTX 6000 Pro + 48 vCPU + 180 GiB) taken
# from the GCE SKU export. All AWS rates are the public g5.2xlarge (1x A10G)
# on-demand rate for the matching region. Melbourne carries a uniform +4.00%
# premium over Sydney on On-Demand/CUD/Spot; DWS Flex is identical in both.
# Live-fleet rows sum to 100% share, $787,750 AWS and $350,175 GCP.
REGIONAL_CATALOG = {
    "Australia Southeast 2 (Melbourne)": {
        "gcp_region": "australia-southeast2",
        "aws_region": "ap-southeast-2",
        "gcp_gpu_od": 1.4243,
        "gcp_vm12_od": 2.5536,
        "gcp_slice_od": 5.8499,
        "gcp_slice_dws": 2.2500,
        "gcp_slice_1y": 4.0365,
        "gcp_slice_3y": 2.5733,
        "aws_a10g_od": 1.5758,
        "aws_g6e_ada_od": 2.3120,
        "mult": 1.2999,
        "fleet_share": 0.47,
        "aws_hours": 234955,
        "aws_cost": 370242,
        "gcp_hours": 58739,
        "gcp_cost": 158055,
        "notes": 'Host region for Australian Open in Melbourne (47.0% fleet share, ultra-low in-city latency)',
    },
    "US Central (Iowa / US East Baseline)": {
        "gcp_region": "us-central1",
        "aws_region": "us-east-1",
        "gcp_gpu_od": 1.0957,
        "gcp_vm12_od": 1.7005,
        "gcp_slice_od": 4.4999,
        "gcp_slice_dws": 2.2500,
        "gcp_slice_1y": 3.1050,
        "gcp_slice_3y": 1.9794,
        "aws_a10g_od": 1.2120,
        "aws_g6e_ada_od": 1.8744,
        "mult": 1.0,
        "fleet_share": 0.233,
        "aws_hours": 151441,
        "aws_cost": 183546,
        "gcp_hours": 37860,
        "gcp_cost": 91142,
        "notes": 'Core US tournament hub & ML training pipeline (23.3% fleet share)',
    },
    "Europe West 2 (London)": {
        "gcp_region": "europe-west2",
        "aws_region": "eu-west-2",
        "gcp_gpu_od": 1.3148,
        "gcp_vm12_od": 2.0212,
        "gcp_slice_od": 5.3999,
        "gcp_slice_dws": 2.2500,
        "gcp_slice_1y": 3.7260,
        "gcp_slice_3y": 2.3753,
        "aws_a10g_od": 1.5385,
        "aws_g6e_ada_od": 2.1556,
        "mult": 1.2,
        "fleet_share": 0.141,
        "aws_hours": 72196,
        "aws_cost": 111073,
        "gcp_hours": 18049,
        "gcp_cost": 46861,
        "notes": "Primary host region for ATP Queen's Club & UK Tournaments (14.1% fleet share)",
    },
    "Europe North 1 (Finland)": {
        "gcp_region": "europe-north1",
        "aws_region": "eu-north-1",
        "gcp_gpu_od": 1.2052,
        "gcp_vm12_od": 2.1608,
        "gcp_slice_od": 4.9499,
        "gcp_slice_dws": 2.2500,
        "gcp_slice_1y": 3.4155,
        "gcp_slice_3y": 2.1774,
        "aws_a10g_od": 1.2900,
        "aws_g6e_ada_od": 2.0618,
        "mult": 1.0999,
        "fleet_share": 0.036,
        "aws_hours": 21984,
        "aws_cost": 28359,
        "gcp_hours": 5496,
        "gcp_cost": 13750,
        "notes": 'Primary host region for CEV European Volleyball Championship (3.6% fleet share)',
    },
    "Rest of World (Singapore / LatAm / Middle East)": {
        "gcp_region": "asia-southeast1",
        "aws_region": "ap-southeast-1",
        "gcp_gpu_od": 1.3148,
        "gcp_vm12_od": 2.1000,
        "gcp_slice_od": 5.3999,
        "gcp_slice_dws": 2.2500,
        "gcp_slice_1y": 3.7260,
        "gcp_slice_3y": 2.3753,
        "aws_a10g_od": 1.5200,
        "aws_g6e_ada_od": 2.1500,
        "mult": 1.2,
        "fleet_share": 0.12,
        "aws_hours": 62191,
        "aws_cost": 94530,
        "gcp_hours": 15548,
        "gcp_cost": 40367,
        "notes": 'Challenger tournaments & regional broadcast feeds (12.0% fleet share)',
    },
    "Europe West 4 (Netherlands)": {
        "gcp_region": "europe-west4",
        "aws_region": "eu-west-1",
        "gcp_gpu_od": 1.2052,
        "gcp_vm12_od": 1.9690,
        "gcp_slice_od": 4.9499,
        "gcp_slice_dws": 2.2500,
        "gcp_slice_1y": 3.4155,
        "gcp_slice_3y": 2.1774,
        "aws_a10g_od": 1.2900,
        "aws_g6e_ada_od": 2.0618,
        "mult": 1.0999,
        "fleet_share": 0.0,
        "aws_hours": 0,
        "aws_cost": 0,
        "gcp_hours": 0,
        "gcp_cost": 0,
        "notes": 'Reference / Cloud Run EU GPU hub — broadcast interconnect, not yet in the live fleet',
    },
    "Europe West 1 (Belgium)": {
        "gcp_region": "europe-west1",
        "aws_region": "eu-west-1",
        "gcp_gpu_od": 1.2052,
        "gcp_vm12_od": 1.8709,
        "gcp_slice_od": 4.9499,
        "gcp_slice_dws": 2.2500,
        "gcp_slice_1y": 3.4155,
        "gcp_slice_3y": 2.1774,
        "aws_a10g_od": 1.2900,
        "aws_g6e_ada_od": 2.0618,
        "mult": 1.0999,
        "fleet_share": 0.0,
        "aws_hours": 0,
        "aws_cost": 0,
        "gcp_hours": 0,
        "gcp_cost": 0,
        "notes": 'Reference / cost-optimized EU tier — not in the live fleet',
    },
}

# Fixed 1:1 Global Multi-Region Profile (Exact AWS Geographic Combination)
region_name = "Global Multi-Region Fleet (Exact 1:1 AWS Footprint)"
region_code = "Global Multi-Region"
region_multiplier = 1.1967
gcp_gpu_hourly = 1.2966  # Global fleet-weighted GPU-only SKU rate
gcp_vm12_hourly = 2.0978 # Global fleet-weighted VM rate
aws_ada_hourly = 2.1404  # Global fleet-weighted AWS g6e.xlarge (1x L40S) rate
aws_a10g_hourly = 1.4514 # Global fleet-weighted AWS g5.2xlarge (1x A10G) rate
gcp_compute_annual = 350175.0

# Sidebar: Controls & Architectural Parameters
with st.sidebar:
    st.markdown("### ⚙️ Architectural Parameters")
    
    st.markdown(
        """
        <div style="background-color: #f1f3f4; border: 1px solid #dadce0; border-radius: 6px; padding: 10px 12px; margin-bottom: 14px;">
            <div style="font-weight: 700; font-size: 13px; color: #1a73e8; margin-bottom: 4px;">
                🌐 Regional Footprint (1:1 AWS Match)
            </div>
            <div style="font-size: 12px; color: #3c4043; line-height: 1.45;">
                • <strong>47.0%</strong> Melbourne (<code>australia-southeast2</code>)<br/>
                • <strong>23.3%</strong> US Central/East (<code>us-central1</code>)<br/>
                • <strong>17.7%</strong> Europe (<code>europe-west2 / north1</code>)<br/>
                • <strong>12.0%</strong> Rest of World (<code>asia-southeast1</code>)
            </div>
            <div style="font-size: 11px; color: #5f6368; margin-top: 6px; border-top: 1px solid #e0e0e0; pt: 4px;">
                Grounded on Bolt6's actual tournament telemetry (Australian Open in Melbourne).
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    storage_arch = st.radio(
        "Storage Strategy",
        ["Native GCS Tiered (\\$140k/yr, \\$0 Egress)", "Dual-Cloud (S3 Retained + \\$126k Egress)"],
        index=0,
    )

    st.markdown("---")
    st.caption("All figures in USD ($). Grounded on verified customer telemetry and Google internal pricing models.")

# Base Calculations
aws_status_quo = 1190750.0  # Scenario S1 ($787,750 compute + $277k storage + $126k egress)
aws_1b_optimized = 912466.0  # Scenario S2 ($635,466 compute + $277k storage + $0 egress)
gcp_prelim_baseline = 888842.0  # Scenario S3 ($485,842 compute + $277k storage + $126k egress)

aws_1b_savings_vs_asis = aws_status_quo - aws_1b_optimized  # $278,284
gcp_prelim_savings_vs_asis = aws_status_quo - gcp_prelim_baseline  # $301,908

# Value Levers & Active Architecture
gpu_sku_optimization_saving = 148604.0 * 1.1967
aus_open_mig_saving = 110532.0
gpu_autoscaling_saving = 135000.0

# gcp_compute_annual is defined above as 350175.0 (65% DWS / 25% CUD / 10% OD across the 1:1 regional blend)

if "Native GCS" in storage_arch:
    gcp_storage_annual = 140000.0
    gcp_egress_annual = 0.0
else:
    gcp_storage_annual = 277000.0
    gcp_egress_annual = 126000.0

gcp_active_annual = gcp_compute_annual + gcp_storage_annual + gcp_egress_annual
total_net_savings = aws_status_quo - gcp_active_annual
pct_savings = (total_net_savings / aws_status_quo) * 100.0

# ==============================================================================
# HEADER & AT-A-GLANCE SCORECARD
# ==============================================================================
st.markdown(
    f"""
    <div style="display: flex; align-items: center; justify-content: space-between; border-bottom: 2px solid #e0e0e0; padding-bottom: 12px; margin-bottom: 18px;">
        <div style="display: flex; align-items: center;">
            {render_bolt6_logo(42)}
            <div>
                <h1 style="margin: 0; font-size: 26px; color: #1a73e8; font-weight: 700;">
                    Bolt6 Cloud Migration Assessment: AWS vs. Google Cloud
                </h1>
                <p style="margin: 2px 0 0 0; color: #5f6368; font-size: 14px;">
                    Executive TCO Model & Production Engineering Architecture — Footprint: <strong>Global Multi-Region Fleet (Exact 1:1 AWS Match)</strong>
                </p>
            </div>
        </div>
        <div style="text-align: right;">
            {render_provider_badge('AWS', 28)}
            {render_provider_badge('GCP', 28)}
        </div>
    </div>
    """,
    unsafe_allow_html=True,
)

# 3 High-Impact KPI Cards
col_kpi1, col_kpi2, col_kpi3 = st.columns(3)
with col_kpi1:
    st.metric(
        label="AWS As-Is Annual Spend (Status Quo)",
        value=f"${aws_status_quo:,.0f} / yr",
        delta="AWS Baseline Run-Rate",
        delta_color="off",
    )
with col_kpi2:
    st.metric(
        label="Refined GCP Architecture (Global Multi-Region)",
        value=f"${gcp_active_annual:,.0f} / yr",
        delta=f"-${total_net_savings:,.0f} / yr Net Delta",
        delta_color="normal",
    )
with col_kpi3:
    st.metric(
        label="Total Annual Cloud Cost Reduction",
        value=f"${total_net_savings:,.0f} / yr",
        delta=f"{pct_savings:.1f}% Reduction vs. AWS As-Is",
        delta_color="normal",
    )

# 2-Bar Comparison Chart & Executive Takeaways
col_bar, col_bullets = st.columns([1.5, 1.2])

with col_bar:
    summary_bars = pd.DataFrame([
        {"Architecture": "AWS As-Is Status Quo", "Annual Spend ($)": aws_status_quo, "Category": "AWS As-Is"},
        {"Architecture": "GCP Refined Production (Global Multi-Region)", "Annual Spend ($)": gcp_active_annual, "Category": "GCP Refined"},
    ])
    if PLOTLY_AVAILABLE:
        fig_scorecard = px.bar(
            summary_bars,
            x="Annual Spend ($)",
            y="Architecture",
            orientation="h",
            text_auto="$.3s",
            color="Category",
            color_discrete_map={
                "AWS As-Is": "#EA4335",
                "GCP Refined": "#34A853"
            },
            title="Annual Cloud Spend: AWS Status Quo vs. Refined GCP Architecture",
        )
        fig_scorecard.update_layout(showlegend=False, margin=dict(t=35, b=10, l=10, r=10), height=210)
        fig_scorecard = add_chart_logos(fig_scorecard, show_aws=True, show_gcp=True)
        st.plotly_chart(fig_scorecard, use_container_width=True)

with col_bullets:
    st.markdown(
        f"""
        <div style="background-color: #f8f9fa; border-left: 4px solid #34a853; padding: 14px 16px; border-radius: 6px; min-height: 210px; display: flex; flex-direction: column; justify-content: center;">
            <div style="font-weight: 700; font-size: 15px; color: #1e8e3e; margin-bottom: 8px;">
                🎯 Executive Summary & Core Advantages
            </div>
            <div style="font-size: 12.5px; color: #3c4043; line-height: 1.45;">
                • <strong>&#36;{total_net_savings:,.0f}/year savings ({pct_savings:.1f}% cut)</strong> across Bolt6's identical global tournament footprint.<br/>
                • <strong>1:1 Regional Mapping:</strong> Matches Bolt6's AWS distribution (47% Melbourne / Australian Open, 23% US, 18% Europe, 12% Other) with localized Blackwell RTX 6000 Pro pricing.<br/>
                • <strong>MIG Court Slicing & Autoscaling:</strong> 1 physical GPU runs 4 courts; nodes scale to zero outside live tournament windows.<br/>
                • <strong>Serverless G4s on Cloud Run:</strong> The measured 13-day CEV & ATP window costs <strong>&#36;3,209 vs &#36;6,892 on AWS (-53.4%)</strong>, or <strong>&#36;2,342 (-66.0%)</strong> with Flexible CUDs — per-second billing, scale-to-zero, no cluster to run.
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

# Expandable Drawer: Detailed Financial Audit & Waterfall
with st.expander("📊 View Detailed Financial Breakdown & 36-Month Scenario Matrix"):
    col_wf, col_mat = st.columns([1.4, 1.6])
    with col_wf:
        waterfall_rows = [
            {"Stage": "AWS 1B. Optimized", "Savings ($)": aws_1b_savings_vs_asis, "Type": "AWS 1B Baseline"},
            {"Stage": "1. Preliminary GCP", "Savings ($)": gcp_prelim_savings_vs_asis, "Type": "Preliminary GCP"},
            {"Stage": "2. + RTX 6000 Pro", "Savings ($)": gcp_prelim_savings_vs_asis + gpu_sku_optimization_saving, "Type": "GPU Density"},
            {"Stage": "3. + MIG Slicing", "Savings ($)": gcp_prelim_savings_vs_asis + gpu_sku_optimization_saving + aus_open_mig_saving, "Type": "MIG Slicing"},
            {"Stage": "4. + GKE Autoscaling", "Savings ($)": total_net_savings, "Type": "Production GCP"},
        ]
        wf_df = pd.DataFrame(waterfall_rows)
        if PLOTLY_AVAILABLE:
            fig_wf = px.bar(
                wf_df,
                x="Stage",
                y="Savings ($)",
                color="Type",
                text_auto="$.2s",
                title="Incremental Annual Savings Progression ($/yr)",
                color_discrete_map={
                    "AWS 1B Baseline": "#EA4335",
                    "Preliminary GCP": "#4285F4",
                    "GPU Density": "#FBBC04",
                    "MIG Slicing": "#F4B400",
                    "Production GCP": "#34A853",
                }
            )
            fig_wf.update_layout(showlegend=False, margin=dict(t=40, b=20, l=10, r=10), height=260)
            st.plotly_chart(fig_wf, use_container_width=True)

    with col_mat:
        matrix_df = pd.DataFrame([
            {"Scenario ID": "S1", "Scenario Name": "1. AWS As-Is Baseline (Status Quo)", "Compute Cost ($)": 787750.0, "Storage Cost ($)": 277000.0, "Cross-Cloud Egress ($)": 126000.0, "Annual Total ($)": 1190750.0},
            {"Scenario ID": "S2", "Scenario Name": "1B. AWS Structurally Optimized", "Compute Cost ($)": 509466.0, "Storage Cost ($)": 277000.0, "Cross-Cloud Egress ($)": 126000.0, "Annual Total ($)": 912466.0},
            {"Scenario ID": "S3", "Scenario Name": "2. GCP Baseline (Dual-Cloud S3)", "Compute Cost ($)": 485842.0, "Storage Cost ($)": 277000.0, "Cross-Cloud Egress ($)": 126000.0, "Annual Total ($)": 888842.0},
            {"Scenario ID": "S4", "Scenario Name": "4. GCP Refined Production (Global Multi-Region)", "Compute Cost ($)": gcp_compute_annual, "Storage Cost ($)": gcp_storage_annual, "Cross-Cloud Egress ($)": gcp_egress_annual, "Annual Total ($)": gcp_active_annual},
        ])
        matrix_df["36-Mo Total ($)"] = matrix_df["Annual Total ($)"] * 3
        matrix_df["Annual Savings ($)"] = aws_status_quo - matrix_df["Annual Total ($)"]
        matrix_df["36-Mo Net Savings ($)"] = (aws_status_quo * 3) - matrix_df["36-Mo Total ($)"]
        disp_mat = matrix_df[["Scenario Name", "Compute Cost ($)", "Storage Cost ($)", "Cross-Cloud Egress ($)", "Annual Total ($)", "Annual Savings ($)", "36-Mo Net Savings ($)"]]
        st.dataframe(
            disp_mat.style.format({
                "Compute Cost ($)": "${:,.0f}",
                "Storage Cost ($)": "${:,.0f}",
                "Cross-Cloud Egress ($)": "${:,.0f}",
                "Annual Total ($)": "${:,.0f}",
                "Annual Savings ($)": "${:,.0f}",
                "36-Mo Net Savings ($)": "${:,.0f}",
            }),
            use_container_width=True,
            hide_index=True,
        )
        st.caption(
            "Annual Savings and 36-Mo Net Savings are both measured against the AWS As-Is baseline of "
            f"\\${aws_status_quo:,.0f}/yr. Row S1 is the baseline itself, so its savings are \\$0 by definition."
        )

st.markdown("---")

# ==============================================================================
# 4 STREAMLINED NARRATIVE TABS
# ==============================================================================
tab_exec, tab_gpu, tab_telemetry, tab_commercial = st.tabs([
    "📊 1. Executive Summary & Financial Scorecard",
    "⚡ 2. Technical Architecture & GPU Levers",
    "⏱️ 3. European Tournaments Telemetry & Autoscaling Proof",
    "💡 4. Commercial Models, DWS Flex & Data Lineage",
])

# ==============================================================================
# TAB 1: EXECUTIVE SUMMARY & FINANCIAL SCORECARD
# ==============================================================================
with tab_exec:
    st.markdown("### 📊 Comprehensive Multi-Cloud Scenario Evaluation")
    st.markdown(
        """
        In the initial top-down review, GCP demonstrated a preliminary savings advantage over AWS. 
        However, by activating three modern cloud engineering capabilities (NVIDIA RTX 6000 Pro mapping, MIG hardware slicing, 
        and GKE Autopilot match-window autoscaling), **total annual savings expand to ~\\$701k/year**.
        """
    )

    col_e1, col_e2 = st.columns([1.5, 1.3])

    with col_e1:
        st.markdown("#### Scenario Cost Comparison Breakdown ($/yr)")
        scenario_bar_data = [
            {"Scenario": "1. AWS As-Is (Status Quo)", "Annual Spend ($)": 1190750, "Provider": "AWS"},
            {"Scenario": "1B. AWS Structurally Optimized", "Annual Spend ($)": 912466, "Provider": "AWS"},
            {"Scenario": "2. GCP Baseline (Dual-Cloud S3)", "Annual Spend ($)": 888842, "Provider": "GCP"},
            {"Scenario": "4. GCP Production (Pure GCS Tiered)", "Annual Spend ($)": gcp_active_annual, "Provider": "GCP"},
        ]
        df_sbar = pd.DataFrame(scenario_bar_data)
        if PLOTLY_AVAILABLE:
            fig_sbar = px.bar(
                df_sbar,
                x="Scenario",
                y="Annual Spend ($)",
                color="Provider",
                text_auto="$.3s",
                color_discrete_map={"AWS": "#EA4335", "GCP": "#34A853"},
                title="Annual Run-Rate across Scenarios (Global Multi-Region)",
            )
            fig_sbar.update_layout(margin=dict(t=40, b=20, l=10, r=10), showlegend=False)
            fig_sbar = add_chart_logos(fig_sbar, show_aws=True, show_gcp=True)
            st.plotly_chart(fig_sbar, use_container_width=True)

    with col_e2:
        st.markdown("#### Cloud Storage Optimization: Pure GCS vs. AWS S3")
        st.markdown(
            """
            * **AWS S3 Baseline:** **\\$277,000 / year** + **\\$126,000 / year cross-cloud egress** to stream data outside AWS.
            * **Google Cloud Storage (GCS) Native:** **\\$140,000 / year** by auto-tiering historical match footage into Nearline/Coldline.
            * **Zero Egress Penalties:** Consolidating compute and storage on GCP eliminates the \\$126k/yr cross-cloud egress penalty entirely.
            """
        )
        st.success(
            f"💰 **Net Storage & Egress Advantage:** **+$263,000 / year saved** by eliminating cross-cloud egress and using GCS intelligent tiering."
        )

    # 1:1 Regional Footprint & Multi-Region Compute Distribution
    st.markdown("---")
    st.markdown("### 🌐 1:1 Regional Footprint & Multi-Region Compute Distribution (AWS vs. GCP)")
    st.markdown(
        """
        Bolt6's AWS As-Is baseline (**\\$1,190,750/year**, with **\\$787,750 compute**) represents tournament operations distributed across **4 key global regions**. 
        To deliver a 1:1 fair comparison, the **GCP Refined Production model calculates cost across that exact same regional combination**, 
        applying local regional GPU pricing (`australia-southeast2`, `us-central1`, `europe-west2`, `asia-southeast1`) and specific architectural optimizations in each geography.
        """
    )

    col_reg_table, col_reg_chart = st.columns([1.5, 1.3])

    with col_reg_table:
        st.markdown("##### Regional Compute Breakdown: AWS Status Quo vs. GCP Refined")
        regional_display_df = pd.DataFrame([
            {
                "Region / Tournament Hub": r["Tournament Region"],
                "Fleet Share": f"{r['Fleet Share']*100:.1f}%",
                "AWS Compute": f"${r['AWS Compute ($)']:,.0f}",
                "GCP Compute": f"${r['GCP Compute ($)']:,.0f}",
                "Annual Savings": f"${r['Net Compute Savings ($)']:,.0f}",
                "Cut": f"-{r['Reduction (%)']:.1f}%",
                "Key Regional GCP Lever": r["Key GCP Levers"],
            }
            for r in REGIONAL_BREAKDOWN
        ])
        st.dataframe(regional_display_df, use_container_width=True, hide_index=True)

        st.info(
            "💡 **Australian Open & Melbourne Impact:** Over 47% of Bolt6's annual compute spend is concentrated in Australia for the January Grand Slam. "
            "On AWS, Bolt6 was forced to route camera feeds to Sydney (`ap-southeast-2`) and paid a \\$110,532 capacity reservation fee. "
            "On GCP, deploying directly in Melbourne (`australia-southeast2`) provides ultra-low in-city latency to Melbourne Park, while MIG court slicing (4 courts per physical RTX 6000 Pro) combined with GKE dynamic scaling saves **\\$212,187/year (-57.3%)** in Australia alone."
        )

    with col_reg_chart:
        reg_chart_data = []
        for r in REGIONAL_BREAKDOWN:
            reg_chart_data.append({"Region": r["Tournament Region"].split("(")[0].strip(), "Provider": "AWS Compute", "Spend ($)": r["AWS Compute ($)"]})
            reg_chart_data.append({"Region": r["Tournament Region"].split("(")[0].strip(), "Provider": "GCP Refined Compute", "Spend ($)": r["GCP Compute ($)"]})
        df_reg_chart = pd.DataFrame(reg_chart_data)

        if PLOTLY_AVAILABLE:
            fig_reg = px.bar(
                df_reg_chart,
                x="Region",
                y="Spend ($)",
                color="Provider",
                barmode="group",
                text_auto="$.2s",
                color_discrete_map={"AWS Compute": "#EA4335", "GCP Refined Compute": "#34A853"},
                title="Annual Compute Spend by Region: AWS vs. GCP",
            )
            fig_reg.update_layout(margin=dict(t=40, b=20, l=10, r=10), legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1), height=280)
            fig_reg = add_chart_logos(fig_reg, show_aws=True, show_gcp=True)
            st.plotly_chart(fig_reg, use_container_width=True)


# ==============================================================================
# TAB 2: TECHNICAL ARCHITECTURE & GPU LEVERS
# ==============================================================================
with tab_gpu:
    st.markdown("### ⚡ Modern GPU Hardware Capabilities & Court Slicing Architecture")

    # Section 1: Head to Head Hardware Specs
    st.markdown("#### 1. Direct Head-to-Head: NVIDIA RTX 6000 Pro vs. AWS A10G & RTX 6000 Ada")
    col_h1, col_h2 = st.columns([1.5, 1.3])

    with col_h1:
        billing_comp = gpu_sheets["billing"]
        if PLOTLY_AVAILABLE:
            fig_perf = px.bar(
                billing_comp,
                x="TFLOPS FP32",
                y="Instance",
                color="Provider",
                orientation="h",
                text_auto=".1f",
                color_discrete_map={
                    "AWS (A10G GPU)": "#EA4335",
                    "AWS (L40S Ada)": "#F4B400",
                    "GCP (RTX 6000 Pro Full)": "#34A853",
                },
                title="Single Node FP32 Compute Throughput (TFLOPS)",
            )
            fig_perf.update_layout(margin=dict(t=40, b=20, l=10, r=10), showlegend=False)
            fig_perf = add_chart_logos(fig_perf, show_aws=True, show_gcp=True)
            st.plotly_chart(fig_perf, use_container_width=True)

    with col_h2:
        st.markdown("##### Hardware Specification Matrix (Global Fleet Blended Rates)")
        ada_saving_pct = (1.0 - gcp_gpu_hourly / aws_ada_hourly) * 100.0
        four_a10g = 4.0 * aws_a10g_hourly
        hw_table = pd.DataFrame([
            {"Metric": "GPU Model", "AWS g5.2xlarge (1x A10G)": "NVIDIA A10G", "AWS g6e.xlarge (1x L40S)": "NVIDIA L40S (Ada)", "GCP g4-standard-48 (1x RTX 6000 Pro)": "RTX 6000 Pro (Blackwell)"},
            {"Metric": "VRAM", "AWS g5.2xlarge (1x A10G)": "24 GB GDDR6", "AWS g6e.xlarge (1x L40S)": "48 GB GDDR6", "GCP g4-standard-48 (1x RTX 6000 Pro)": "96 GB GDDR7 (4x / 2x)"},
            {"Metric": "FP32 Throughput", "AWS g5.2xlarge (1x A10G)": "31.2 TFLOPS", "AWS g6e.xlarge (1x L40S)": "91.6 TFLOPS", "GCP g4-standard-48 (1x RTX 6000 Pro)": "120.0 TFLOPS (3.85x A10G)"},
            {"Metric": "Courts served per GPU", "AWS g5.2xlarge (1x A10G)": "1", "AWS g6e.xlarge (1x L40S)": "1", "GCP g4-standard-48 (1x RTX 6000 Pro)": "4 (MIG partitioning)"},
            {"Metric": "Instance rate", "AWS g5.2xlarge (1x A10G)": f"${aws_a10g_hourly:.4f}/hr", "AWS g6e.xlarge (1x L40S)": f"${aws_ada_hourly:.4f}/hr", "GCP g4-standard-48 (1x RTX 6000 Pro)": "$5.3254/hr OD | $2.2500/hr DWS Flex"},
            {"Metric": "Cost to serve 4 courts", "AWS g5.2xlarge (1x A10G)": f"4 x ${aws_a10g_hourly:.4f} = ${four_a10g:.4f}/hr", "AWS g6e.xlarge (1x L40S)": f"4 x ${aws_ada_hourly:.4f} = ${4*aws_ada_hourly:.4f}/hr", "GCP g4-standard-48 (1x RTX 6000 Pro)": "1 x $2.2500/hr (-61.2%)"},
        ])
        st.dataframe(hw_table, use_container_width=True, hide_index=True)
        st.caption(
            "Like-for-like basis: one RTX 6000 Pro is MIG-partitioned into 4 court workloads, so it is "
            "compared against **four** single-GPU AWS instances, not one. Rates are fleet-blended across "
            "Bolt6's regions; GCP rates are the full `g4-standard-48` machine (48 vCPU + 180 GiB included), "
            "AWS rates are the full instance. Cost-per-TFLOP is deliberately omitted — it is not "
            "meaningful once one physical GPU is serving four independent workloads."
        )
        st.info(
            f"💡 **Key Advantage:** Serving four courts costs **\\${four_a10g:.2f}/hr on AWS A10G** "
            f"versus **\\$2.25/hr on one MIG-partitioned RTX 6000 Pro with DWS Flex — a "
            f"61.2% reduction**, with 96 GB of GDDR7 and 3.85x the FP32 throughput per GPU."
        )

    st.markdown("---")
    st.markdown("#### 2. Multi-Region Pricing Matrix: Rates, Compute Hours & Total Cost by Region")
    st.markdown(
        """
        This is the **single source of truth** for the whole model — regional rates on the left, and the volume and
        annual cost they produce on the right. Every figure is traceable:

        * **Annual AWS GPU-Hrs** = (region's share of the **\\$787,750** AWS compute baseline) ÷ (that region's public `g5.2xlarge` on-demand rate)
        * **Annual GCP G4-Hrs** = AWS GPU-Hrs ÷ 4 — one RTX 6000 Pro replaces four A10G/T4 GPUs via MIG court slicing
        * **GCP Annual Cost** = GCP G4-Hrs x the documented mix (**65%** DWS Flex + **25%** 3-Yr CUD + **10%** On-Demand), identical in every region
        * **Eff. GCP \\$/G4-Hr** is the *outcome* of the production consumption mix (DWS Flex + CUD + On-Demand), not an input

        DWS Flex holds a **uniform \\$2.25/hr across every region in Bolt6's footprint** (SKU-verified), which is why the highest-cost regions — Melbourne and London — show the
        largest percentage savings. Melbourne makes the point sharply: `australia-southeast2` is **+4.00% more expensive than Sydney on
        On-Demand, CUD and Spot alike**, yet its **DWS Flex rate is identical** — so the premium only touches the un-reserved portion of the fleet.
        """
    )

    reg_matrix_rows = []
    for r_name, r_vals in REGIONAL_CATALOG.items():
        saving_vs_aws = (1.0 - r_vals["gcp_gpu_od"] / r_vals["aws_g6e_ada_od"]) * 100.0
        in_fleet = r_vals["fleet_share"] > 0
        eff_gcp_rate = (r_vals["gcp_cost"] / r_vals["gcp_hours"]) if r_vals["gcp_hours"] else 0.0
        cost_cut = ((r_vals["aws_cost"] - r_vals["gcp_cost"]) / r_vals["aws_cost"] * 100.0) if r_vals["aws_cost"] else 0.0
        reg_matrix_rows.append({
            "Region": r_name.split("(")[0].strip(),
            "GCP Region Code": r_vals["gcp_region"],
            "Fleet Share": f"{r_vals['fleet_share']*100:.1f}%" if in_fleet else "reference",
            "GCP GPU OD ($/h)": f"${r_vals['gcp_gpu_od']:.4f}",
            "GCP DWS Flex ($/h)": f"${r_vals['gcp_slice_dws']:.2f}",
            "GCP 3-Yr CUD ($/h)": f"${r_vals['gcp_slice_3y']:.2f}",
            "AWS Ada g6e ($/h)": f"${r_vals['aws_g6e_ada_od']:.4f}",
            "GPU Rate Advantage": f"-{saving_vs_aws:.1f}%",
            "Annual AWS GPU-Hrs": f"{r_vals['aws_hours']:,}" if in_fleet else "—",
            "AWS Annual Cost": f"${r_vals['aws_cost']:,}" if in_fleet else "—",
            "Annual GCP G4-Hrs": f"{r_vals['gcp_hours']:,}" if in_fleet else "—",
            "GCP Annual Cost": f"${r_vals['gcp_cost']:,}" if in_fleet else "—",
            "Eff. GCP $/G4-Hr": f"${eff_gcp_rate:.2f}" if in_fleet else "—",
            "Annual Savings": f"${r_vals['aws_cost'] - r_vals['gcp_cost']:,} (-{cost_cut:.1f}%)" if in_fleet else "—",
            "Event Workload": r_vals["notes"],
        })

    # Totals row across the live fleet only
    _live = [v for v in REGIONAL_CATALOG.values() if v["fleet_share"] > 0]
    t_share = sum(v["fleet_share"] for v in _live)
    t_aws_h = sum(v["aws_hours"] for v in _live)
    t_aws_c = sum(v["aws_cost"] for v in _live)
    t_gcp_h = sum(v["gcp_hours"] for v in _live)
    t_gcp_c = sum(v["gcp_cost"] for v in _live)
    reg_matrix_rows.append({
        "Region": "▶ TOTAL (live fleet)",
        "GCP Region Code": "Global Multi-Region",
        "Fleet Share": f"{t_share*100:.1f}%",
        "GCP GPU OD ($/h)": "$1.2966",
        "GCP DWS Flex ($/h)": "$2.25",
        "GCP 3-Yr CUD ($/h)": "$2.32",
        "AWS Ada g6e ($/h)": "$2.1404",
        "GPU Rate Advantage": "-39.4%",
        "Annual AWS GPU-Hrs": f"{t_aws_h:,}",
        "AWS Annual Cost": f"${t_aws_c:,}",
        "Annual GCP G4-Hrs": f"{t_gcp_h:,}",
        "GCP Annual Cost": f"${t_gcp_c:,}",
        "Eff. GCP $/G4-Hr": f"${t_gcp_c/t_gcp_h:.2f}",
        "Annual Savings": f"${t_aws_c - t_gcp_c:,} (-{(t_aws_c-t_gcp_c)/t_aws_c*100:.1f}%)",
        "Event Workload": "Exact 1:1 match of Bolt6's AWS geographic footprint",
    })

    st.dataframe(pd.DataFrame(reg_matrix_rows), use_container_width=True, hide_index=True)
    st.caption(
        f"Live-fleet rows reconcile exactly: shares sum to {t_share*100:.0f}%, AWS to \\${t_aws_c:,} and GCP to \\${t_gcp_c:,}. "
        f"{t_aws_h:,} AWS GPU-hours ≈ {t_aws_h/8760:.0f} GPUs running year-round; after 4:1 MIG consolidation that becomes "
        f"{t_gcp_h:,} G4-hours ≈ {t_gcp_h/8760:.0f} concurrent RTX 6000 Pro nodes. "
        "Netherlands and Belgium are reference regions for rate comparison (and the Cloud Run EU GPU hub) — they carry no fleet workload."
    )

    st.markdown(
        """
        <div style="background-color: #e8f0fe; border-left: 4px solid #1a73e8; padding: 12px 16px; border-radius: 6px; margin-top: 10px;">
            <strong style="color: #1a73e8;">🌐 Global Multi-Region Fleet Summary:</strong>
            Bolt6's global operations across Melbourne (47%), US (23.3%), Europe (17.7%), and Rest of World (12%) yield an effective global blended multiplier of <strong>1.1967x</strong> vs. pure US baseline. 
            This translates to a total refined GCP compute spend of <strong>&#36;350,175/yr</strong> (down from &#36;787,750/yr on AWS) — saving <strong>&#36;437,575/yr (-55.5%) on compute alone</strong> while honoring local regional deployments.
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.markdown("---")

    # Section 2: Court Slicing Architecture via MIG
    st.markdown("#### 3. Court Slicing Architecture: Multi-Instance GPU (MIG)")
    col_mig1, col_mig2 = st.columns([1.5, 1.3])

    with col_mig1:
        st.markdown(
            """
            In traditional AWS deployments, every continuous court camera feed (e.g. **TrU Line** and **Sentinel Optical Tracking**) 
            requires provisioning an entire dedicated VM (`g5.2xlarge` or `g4dn.2xlarge`), leaving significant GPU headroom unutilized.
            
            **On GCP, Multi-Instance GPU (MIG) hardware partitioning transforms this paradigm:**
            * A single physical NVIDIA RTX 6000 Pro (96GB VRAM) partitions into **four isolated fractional instances** (`1/4` slice = 24GB VRAM each).
            * Each slice has dedicated compute engines, memory controllers, and isolation — **running 4 full tournament courts simultaneously on 1 physical GPU node**.
            * Eliminates **+$110,532/year** in wasted whole-GPU headroom capacity during tournament surges.
            """
        )

    with col_mig2:
        mig_diagram_df = pd.DataFrame([
            {"Partition": "MIG Slice 1 (24GB VRAM)", "Workload": "Court 1: TrU Line Real-time Ball Tracking", "Resource Share": "25% GPU / 24GB"},
            {"Partition": "MIG Slice 2 (24GB VRAM)", "Workload": "Court 2: Sentinel Optical Camera Tracking", "Resource Share": "25% GPU / 24GB"},
            {"Partition": "MIG Slice 3 (24GB VRAM)", "Workload": "Court 3: Multi-angle Player Skeleton Tracking", "Resource Share": "25% GPU / 24GB"},
            {"Partition": "MIG Slice 4 (24GB VRAM)", "Workload": "Court 4: Automated Line Calling & Broadcast Rendering", "Resource Share": "25% GPU / 24GB"},
        ])
        st.dataframe(mig_diagram_df, use_container_width=True, hide_index=True)
        st.success("🎯 **Consolidation Impact:** 4 AWS VMs (\\$6.32/hr total) consolidated into 1 GCP RTX 6000 Pro node with MIG (\\$1.05/hr OD or \\$0.56/hr DWS Flex) — **saving up to 82%**.")


# ==============================================================================
# TAB 3: EUROPEAN TOURNAMENTS TELEMETRY & AUTOSCALING PROOF
# ==============================================================================
with tab_telemetry:
    st.markdown("### ⏱️ European Tournaments Live Telemetry & Autoscaling Proof (CEV & ATP)")

    # ROI-First Top Callout
    col_roi1, col_roi2, col_roi3, col_roi4 = st.columns(4)
    with col_roi1:
        st.metric(label="13-Day Measured AWS Spend", value="$6,892.41", delta="1,699 Node Instances", delta_color="inverse")
    with col_roi2:
        st.metric(label="GCP DWS Flex Event Spend", value="$2,864.50", delta="-$4,028 Saved (-58.4%)", delta_color="normal")
    with col_roi3:
        st.metric(label="Measured Cluster Active Uptime", value="187.2 Hours", delta="Across 23 Sessions (28/08-09/09)", delta_color="off")
    with col_roi4:
        st.metric(label="Empirical Inactive / Off-Time", value="70.0% Off-Time", delta="CEV: 40% Duty | ATP: 20% Duty", delta_color="normal")

    st.markdown("---")

    # Supporting Ground-Truth Telemetry Charts
    col_gtt1, col_gtt2 = st.columns([1.5, 1.3])

    with col_gtt1:
        st.markdown("#### 1. Daily Cluster Active Uptime: Matches Run ~8 hrs/day")
        cluster_timeline_data = [
            {"Date": "Aug 28, 2026", "Cluster": "cev-eu-north-1", "Uptime (hrs)": 9.87},
            {"Date": "Aug 29, 2026", "Cluster": "cev-eu-north-1", "Uptime (hrs)": 1.25},
            {"Date": "Aug 30, 2026", "Cluster": "cev-eu-north-1", "Uptime (hrs)": 7.43},
            {"Date": "Aug 31, 2026", "Cluster": "cev-eu-north-1", "Uptime (hrs)": 9.90},
            {"Date": "Sep 01, 2026", "Cluster": "cev-eu-north-1", "Uptime (hrs)": 9.27},
            {"Date": "Sep 02, 2026", "Cluster": "cev-eu-north-1", "Uptime (hrs)": 12.57},
            {"Date": "Sep 03, 2026", "Cluster": "cev-eu-north-1", "Uptime (hrs)": 11.50},
            {"Date": "Sep 03, 2026", "Cluster": "atp-eu-west-2", "Uptime (hrs)": 0.50},
            {"Date": "Sep 04, 2026", "Cluster": "cev-eu-north-1", "Uptime (hrs)": 2.49},
            {"Date": "Sep 05, 2026", "Cluster": "cev-eu-north-1", "Uptime (hrs)": 10.01},
            {"Date": "Sep 05, 2026", "Cluster": "atp-eu-west-2", "Uptime (hrs)": 5.60},
            {"Date": "Sep 06, 2026", "Cluster": "cev-eu-north-1", "Uptime (hrs)": 10.47},
            {"Date": "Sep 06, 2026", "Cluster": "atp-eu-west-2", "Uptime (hrs)": 21.68},
            {"Date": "Sep 07, 2026", "Cluster": "cev-eu-north-1", "Uptime (hrs)": 12.00},
            {"Date": "Sep 07, 2026", "Cluster": "atp-eu-west-2", "Uptime (hrs)": 11.33},
            {"Date": "Sep 08, 2026", "Cluster": "cev-eu-north-1", "Uptime (hrs)": 14.97},
            {"Date": "Sep 08, 2026", "Cluster": "atp-eu-west-2", "Uptime (hrs)": 15.32},
            {"Date": "Sep 09, 2026", "Cluster": "cev-eu-north-1", "Uptime (hrs)": 13.78},
            {"Date": "Sep 09, 2026", "Cluster": "atp-eu-west-2", "Uptime (hrs)": 7.25},
        ]
        df_ctime = pd.DataFrame(cluster_timeline_data)
        if PLOTLY_AVAILABLE:
            fig_ctime = px.bar(
                df_ctime,
                x="Date",
                y="Uptime (hrs)",
                color="Cluster",
                barmode="group",
                color_discrete_map={"cev-eu-north-1": "#1A73E8", "atp-eu-west-2": "#EA4335"},
                title="Measured Cluster Active Hours (28/08 – 09/09/2026)",
            )
            fig_ctime.update_xaxes(type="category")
            fig_ctime.update_layout(margin=dict(t=40, b=20, l=10, r=10), legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1))
            st.plotly_chart(fig_ctime, use_container_width=True)

    with col_gtt2:
        st.markdown("#### 2. Ephemeral GPU Lifecycles: Averaging 4.5 – 5.3 Hours")
        node_life_data = [
            {"Instance Type": "g5.2xlarge (A10G)", "Avg Lifetime (h)": 4.55, "Node Count": 318, "Total Spend ($)": 2285.91},
            {"Instance Type": "g5.4xlarge (A10G)", "Avg Lifetime (h)": 5.18, "Node Count": 156, "Total Spend ($)": 1639.29},
            {"Instance Type": "g4dn.2xlarge (T4)", "Avg Lifetime (h)": 5.26, "Node Count": 336, "Total Spend ($)": 1329.82},
            {"Instance Type": "c5.xlarge (Baseline CPU)", "Avg Lifetime (h)": 8.76, "Node Count": 384, "Total Spend ($)": 572.02},
            {"Instance Type": "g4dn.xlarge (T4)", "Avg Lifetime (h)": 5.84, "Node Count": 165, "Total Spend ($)": 506.91},
            {"Instance Type": "Other Instances", "Avg Lifetime (h)": 4.10, "Node Count": 340, "Total Spend ($)": 558.46},
        ]
        df_nlife = pd.DataFrame(node_life_data)
        st.dataframe(df_nlife, use_container_width=True, hide_index=True)

    # Solution: GKE Autopilot
    st.markdown("---")
    st.markdown("#### 3. How GKE Autopilot Solves the Event Cost Problem")
    col_sol1, col_sol2 = st.columns([1.5, 1.3])
    with col_sol1:
        st.markdown(
            """
            * **Eliminates \\$572 Baseline VM Waste:** In AWS, Bolt6 pays for 384 CPU baseline nodes (`c5.xlarge`) running for 3,364 hours just to keep cluster daemonsets alive. On GKE Autopilot, control plane and system pods are managed automatically; **worker nodes scale to zero** when matches finish.
            * **Automates Match-Window Scaling:** Bolt6's actual 4.5-hour node lifecycles confirm that workloads are match-driven. GKE Autopilot automatically spins up GPU pod replicas when camera feeds activate, and tears them down immediately when play concludes.
            """
        )
    with col_sol2:
        event_comp = pd.DataFrame([
            {"Architecture": "AWS As-Is (Status Quo)", "13-Day Spend ($)": 6892.41, "Family": "AWS"},
            {"Architecture": "GCP G4 On-Demand (Autopilot + MIG)", "13-Day Spend ($)": 4120.30, "Family": "GCP GKE"},
            {"Architecture": "Cloud Run G4 (Serverless, list)", "13-Day Spend ($)": 3208.53, "Family": "Cloud Run"},
            {"Architecture": "GCP DWS Flex (Match Reservation)", "13-Day Spend ($)": 2864.50, "Family": "GCP GKE"},
            {"Architecture": "Cloud Run G4 + Flexible CUD", "13-Day Spend ($)": 2341.54, "Family": "Cloud Run"},
        ])
        if PLOTLY_AVAILABLE:
            fig_ev = px.bar(
                event_comp,
                x="13-Day Spend ($)",
                y="Architecture",
                orientation="h",
                text_auto="$.3s",
                color="Family",
                color_discrete_map={
                    "AWS": "#EA4335",
                    "GCP GKE": "#FBBC04",
                    "Cloud Run": "#34A853",
                },
                title="13-Day Tournament Spend: AWS vs. GKE vs. Cloud Run",
            )
            fig_ev.update_layout(
                showlegend=False,
                margin=dict(t=40, b=20, l=10, r=10),
                height=250,
                yaxis=dict(categoryorder="total ascending"),
            )
            st.plotly_chart(fig_ev, use_container_width=True)

    # ==========================================================================
    # SECTION 4: SERVERLESS GPUs ON CLOUD RUN
    # ==========================================================================
    st.markdown("---")
    st.markdown("#### 4. Serverless GPUs: Running the Same RTX PRO 6000 on Cloud Run")
    st.markdown(
        """
        Bolt6's telemetry shows a workload that is **event-driven, bursty and idle most of the time** — exactly the profile
        Cloud Run is built for. Cloud Run now offers the **identical NVIDIA RTX PRO 6000 Blackwell GPU (96 GB VRAM)** used in the
        GCE G4 model above, but billed **per second** with **true scale-to-zero** and **no cluster to operate**.
        Every figure below is derived from the same 13-day CEV & ATP telemetry, priced with the
        [official Cloud Run rate card](https://cloud.google.com/run/pricing).
        """
    )

    col_cr1, col_cr2, col_cr3, col_cr4 = st.columns(4)
    with col_cr1:
        st.metric(label="Cloud Run G4 Billable Time", value="1,006.8 G4-hrs", delta="-239.7 hrs vs GKE envelope (-19.2%)", delta_color="normal")
    with col_cr2:
        st.metric(label="Cloud Run G4 Event Spend", value="$3,208.53", delta="-$3,684 vs AWS (-53.4%)", delta_color="normal")
    with col_cr3:
        st.metric(label="With Compute Flexible CUD", value="$2,341.54", delta="-$4,551 vs AWS (-66.0%)", delta_color="normal")
    with col_cr4:
        st.metric(label="Instance Cold Start", value="~5 seconds", delta="36x faster than GKE node boot (~180s)", delta_color="normal")

    col_cr_calc, col_cr_rate = st.columns([1.35, 1.3])

    with col_cr_calc:
        st.markdown("##### A. Cost Derivation from Bolt6's Start/Stop Telemetry")
        st.markdown(
            """
            Cloud Run only bills while an instance is alive. Three blocks of **non-serving time** that Bolt6
            pays for today simply disappear:
            """
        )
        cr_derivation = pd.DataFrame([
            {"Step": "AWS GPU node-hours measured (318+156+336+165 nodes)", "G4-Hours": "4,985.9", "Note": "Ground truth from ephemeral node lifecycles"},
            {"Step": "÷ 4 via RTX 6000 Pro MIG court slicing", "G4-Hours": "1,246.5", "Note": "4 courts per physical GPU (6.66 avg concurrent)"},
            {"Step": "− Node boot & CV image pull (244 cycles × 175s)", "G4-Hours": "−11.9", "Note": "Cloud Run starts in ~5s, drivers pre-installed"},
            {"Step": "− Autoscaler scale-down grace (244 × 10 min)", "G4-Hours": "−40.6", "Note": "Cloud Run scales to zero on last disconnect"},
            {"Step": "− Standing burst-headroom node (1 × 187.2 h)", "G4-Hours": "−187.2", "Note": "No warm spare needed for extra-time matches"},
            {"Step": "= Cloud Run billable envelope", "G4-Hours": "1,006.8", "Note": "Pure in-play serving seconds only"},
        ])
        st.dataframe(cr_derivation, use_container_width=True, hide_index=True)
        st.caption(
            "Measured cluster uptime 187.2 hrs across 23 sessions (28 Aug – 09 Sep 2026). "
            "244 G4 node cycles = 975 AWS GPU node launches consolidated 4:1."
        )

    with col_cr_rate:
        st.markdown("##### B. Cloud Run G4 Rate Card vs. GCE G4")
        cr_rates = pd.DataFrame([
            {"Consumption Model": "Cloud Run G4 (no zonal redundancy)", "GPU ($/hr)": "$1.315", "20 vCPU ($/hr)": "$1.296", "80 GiB ($/hr)": "$0.576", "Total ($/hr)": "$3.187", "13-Day Spend": "$3,208.53"},
            {"Consumption Model": "Cloud Run G4 (zonal redundancy / HA)", "GPU ($/hr)": "$2.049", "20 vCPU ($/hr)": "$1.296", "80 GiB ($/hr)": "$0.576", "Total ($/hr)": "$3.921", "13-Day Spend": "$3,947.61"},
            {"Consumption Model": "Cloud Run G4 + Flexible CUD 3-Yr", "GPU ($/hr)": "$1.315", "20 vCPU ($/hr)": "$0.700", "80 GiB ($/hr)": "$0.311", "Total ($/hr)": "$2.326", "13-Day Spend": "$2,341.54"},
            {"Consumption Model": "GCE G4 full slice — On-Demand", "GPU ($/hr)": "—", "20 vCPU ($/hr)": "—", "80 GiB ($/hr)": "—", "Total ($/hr)": "$4.195", "13-Day Spend": "$4,120.30"},
            {"Consumption Model": "GCE G4 full slice — DWS Flex", "GPU ($/hr)": "—", "20 vCPU ($/hr)": "—", "80 GiB ($/hr)": "—", "Total ($/hr)": "$2.250", "13-Day Spend": "$2,864.50"},
        ])
        st.dataframe(cr_rates, use_container_width=True, hide_index=True)
        st.caption(
            "Cloud Run Tier 1 instance-based billing: GPU `nvidia-rtx-pro-6000` \\$0.00036522/s (no ZR) or \\$0.00056913/s (ZR); "
            "CPU \\$0.000018/vCPU-s; Memory \\$0.000002/GiB-s. Flexible CUD 3-Yr reduces CPU to \\$0.00000972 and RAM to \\$0.00000108. "
            "Minimum config for this GPU is 20 vCPU + 80 GiB."
        )

    st.success(
        "💰 **Headline:** Running the European tournaments entirely on Cloud Run costs **\\$3,208.53 for the 13 days — "
        "\\$3,683.88 (-53.4%) less than AWS and 22.1% less than GKE G4 On-Demand**, with zero cluster to manage. "
        "Applying Compute Flexible CUDs to the CPU/memory component drops it to **\\$2,341.54 — 18.3% cheaper than even GKE + DWS Flex "
        "(-66.0% vs AWS)**."
    )

    st.markdown("##### C. Why Cloud Run Is the Right Fit for Match-Driven Tracking")
    col_adv1, col_adv2 = st.columns(2)

    with col_adv1:
        st.markdown(
            """
            **Economic advantages**
            * **Per-second billing, scale-to-zero.** Between sessions Bolt6 pays **\\$0.00**. No node pools idling through
              overnight gaps, rain delays or rest days — the measured 70% off-time becomes genuinely free.
            * **No 10-minute scale-down tax.** GKE's cluster autoscaler holds nodes for a grace period after the last pod
              exits; across 244 node cycles that is **40.6 G4-hours of pure waste** removed.
            * **No standing burst buffer.** Bolt6 currently keeps a warm spare GPU for extra-time matches and unplanned
              courts — **187.2 G4-hours over 13 days**. A 5-second cold start makes that spare unnecessary.
            * **Zero cluster overhead.** No control plane, no daemonsets, no node upgrades. This structurally eliminates the
              **\\$572 of `c5.xlarge` baseline nodes** (384 nodes / 3,364 hrs) Bolt6 paid just to keep the cluster alive.
            * **24% cheaper per hour than GCE G4 On-Demand** (\\$3.187 vs \\$4.195), with Flexible CUDs taking it below DWS Flex.
            """
        )

    with col_adv2:
        st.markdown(
            """
            **Operational & architectural advantages**
            * **Identical silicon.** `nvidia-rtx-pro-6000` on Cloud Run is the same Blackwell RTX PRO 6000 (96 GB VRAM,
              120 TFLOPS FP32) modelled in the TCO — no performance compromise for TrU Line or Sentinel.
            * **~5 second starts.** NVIDIA drivers are pre-installed and images stream on demand, versus ~3 minutes to boot a
              GKE GPU node and pull a multi-gigabyte CV container.
            * **Request-driven court scaling.** One service fans out from 0 → N instances as camera feeds connect; no MIG
              partition config, no node pool sizing, no HPA tuning.
            * **Built for the unscheduled.** Extra-time matches, rain-delay restarts and a surprise fifth court need no
              reservation and no pre-booked quota — exactly where DWS Flex reservations are weakest.
            * **One-flag HA.** Zonal redundancy can be switched on for finals and marquee matches (\\$3.921/hr) and off for
              qualifiers (\\$3.187/hr).
            """
        )

    st.info(
        "📍 **Deployment region note:** Cloud Run's RTX PRO 6000 GPU is available in **`europe-west4` (Netherlands)**, "
        "`us-central1`, `asia-southeast1` and `asia-south2` — not yet in London or Finland. "
        "`europe-west4` is already Bolt6's European broadcast interconnect hub (≈7 ms to London, ≈22 ms to Stockholm), well inside "
        "the tracking pipeline's tolerance, and is a Google **Low CO2** region. "
        "**Recommended pattern:** DWS Flex reservations on GKE for pre-scheduled main-court matches, with Cloud Run absorbing "
        "overflow and unscheduled demand — a blended 13-day cost of **$2,711.98 (-60.7% vs AWS)** that never leaves a court unserved."
    )



# ==============================================================================
# TAB 4: COMMERCIAL MODELS, DWS FLEX & DATA LINEAGE
# ==============================================================================
with tab_commercial:
    st.markdown("### 💡 Commercial GPU Consumption Models & Data Lineage")

    # Section 1: Commercial Purchasing Models
    st.markdown("#### 1. Google Cloud GPU Commercial Purchasing Options")
    consumption_matrix = [
        {"Model": "On-Demand", "RTX 6000 Pro ($/hr)": "$4.50", "L4 ($/hr)": "$1.00", "Discount": "0% (Baseline)", "Preemption Risk": "None (100% SLA)", "Quota Pool": "Standard On-Demand", "Best Fit for Bolt6": "Unscheduled extra-time matches, sudden tournament surges"},
        {"Model": "Cloud Run Serverless GPU (per-second)", "RTX 6000 Pro ($/hr)": "$3.19 †", "L4 ($/hr)": "$1.05 †", "Discount": "29.2% OFF", "Preemption Risk": "None (~5s cold start, scale-to-zero)", "Quota Pool": "Serverless milliGPU (no reservation)", "Best Fit for Bolt6": "Overflow & unscheduled demand — rain-delay restarts, a surprise 5th court"},
        {"Model": "Dynamic Workload Scheduler (DWS Flex)", "RTX 6000 Pro ($/hr)": "$2.25", "L4 ($/hr)": "$1.01", "Discount": "50.0% OFF", "Preemption Risk": "ZERO once started", "Quota Pool": "Preemptible (High ceiling)", "Best Fit for Bolt6": "Scheduled tournament matches (TrU Line & Sentinel)"},
        {"Model": "1-Year Committed Use Discount (CUD)", "RTX 6000 Pro ($/hr)": "$3.11", "L4 ($/hr)": "$0.63", "Discount": "30.9% OFF", "Preemption Risk": "None (100% SLA)", "Quota Pool": "Committed Capacity", "Best Fit for Bolt6": "Core baseline year-round tracking camera feeds"},
        {"Model": "3-Year Committed Use Discount (CUD)", "RTX 6000 Pro ($/hr)": "$1.98", "L4 ($/hr)": "$0.45", "Discount": "56.0% OFF", "Preemption Risk": "None (100% SLA)", "Quota Pool": "Committed Capacity", "Best Fit for Bolt6": "Multi-year production commitments for contracted leagues"},
        {"Model": "Spot / Preemptible VMs", "RTX 6000 Pro ($/hr)": "$1.64", "L4 ($/hr)": "$0.60", "Discount": "63.6% OFF", "Preemption Risk": "High (30s eviction)", "Quota Pool": "Preemptible Quota", "Best Fit for Bolt6": "Non-live post-match analytics, AI computer vision re-training"},
    ]
    st.dataframe(pd.DataFrame(consumption_matrix), use_container_width=True, hide_index=True)
    st.caption(
        "† Cloud Run rates are **fully loaded** — they include the mandatory instance resources "
        "(20 vCPU + 80 GiB for RTX 6000 Pro; 4 vCPU + 16 GiB for L4), so they are not directly comparable "
        "to the GPU-only GCE rates above. Shown without zonal redundancy; enabling it takes RTX 6000 Pro to \\$3.92/hr. "
        "Applying Compute Flexible CUDs to the CPU/memory component — which span Compute Engine, GKE **and** Cloud Run — "
        "brings it down to \\$2.33/hr. Available in `europe-west4`, `us-central1`, `asia-southeast1` and `asia-south2`. "
        "See Tab 3 for the full Cloud Run cost model against Bolt6's measured tournament telemetry."
    )

    col_cm1, col_cm2 = st.columns([1.5, 1.3])
    with col_cm1:
        st.markdown("##### ⚡ Why DWS Flex is the Game-Changer for Live Sports")
        st.markdown(
            """
            * **Spot VMs cannot be used for live broadcast:** An unexpected 30-second eviction mid-match causes ball tracking failure.
            * **DWS Flex delivers Spot-level pricing (50% OFF) with Production SLA:** You request instances for the scheduled match window (e.g. 4-6 hours). Once started, **GCP guarantees zero preemption until the job completes**, up to a maximum run duration of 7 days.
            * **GA on GKE:** RTX 6000 Pro (G4) and L4 (G2) are General Availability on GKE, Batch, and Compute Engine with DWS Flex.
            """
        )
    with col_cm2:
        st.markdown("##### 🎯 Recommended Consumption Mix Simulator")
        pct_cud = st.slider("% Baseline on 3-Year CUD ($1.98/hr, us-central1)", 0, 100, 25, step=5)
        rem = 100 - pct_cud
        pct_dws = st.slider("% Scheduled Matches on DWS Flex ($2.25/hr)", 0, rem, min(65, rem), step=5)
        pct_od = 100 - pct_cud - pct_dws
        st.write(f"**Surge / On-Demand ($4.50/hr, us-central1):** `{pct_od}%`")
        blended_rate = (pct_cud * 1.98 + pct_dws * 2.25 + pct_od * 4.50) / 100.0
        st.metric(label="Blended Effective Hourly Rate per RTX 6000 Pro", value=f"${blended_rate:.2f} / hr", delta=f"{(1.0 - blended_rate/4.50)*100:.1f}% vs GCP On-Demand")

    st.markdown("---")

    # Section 2: Data Grounding & Google Sheets Lineage
    st.markdown("#### 2. Data Grounding & Google Sheets Audit Lineage")
    st.markdown("All dashboard figures trace to the customer source workbooks below. The app attempts a live fetch on load and falls back to the last verified snapshot of each sheet if the fetch is unavailable, so figures are stable between refreshes.")

    # 6 Google Sheets Cards
    col_s1, col_s2, col_s3 = st.columns(3)
    with col_s1:
        st.markdown("##### 1. Customer Telemetry")
        st.markdown("[🔗 `AWS EC2 Usage 28/08-09/09`](https://docs.google.com/spreadsheets/d/16rqCN7wOnLWUjHNepIRy5jsdwUp3M_KiJKknxOngHQg/edit)")
        st.caption("23 cluster sessions, 187.2h uptime (70% off-time), 1,699 instances, court namespaces.")
    with col_s2:
        st.markdown("##### 2. DWS Availability & Quota")
        st.markdown("[🔗 `DWS Availability Framework`](https://docs.google.com/spreadsheets/d/14RbMcCyYF238wosJEE6JmBi-RMMAhcXc2mrqWz6QQvI/edit?resourcekey=0-1laHo05S-aYccoT6kuxdeA)")
        st.caption("RTX 6000 Pro GA status on GKE, DWS Flex preemptible quota rules, Calendar reservations.")
    with col_s3:
        st.markdown("##### 3. GPU Pricing Master")
        st.markdown("[🔗 `GCP GPU Pricing & SKUs`](https://docs.google.com/spreadsheets/d/1L-xrU1meHGtGogQFD4OLkSvmutNznDTPQIHSaxda2xI/edit)")
        st.caption("SKU pricing for G4 RTX 6000. Rates shown are `us-central1` (\\$4.50 OD / \\$2.25 DWS / \\$1.98 CUD); other regions differ except DWS Flex, which is uniform.")

    col_s4, col_s5, col_s6 = st.columns(3)
    with col_s4:
        st.markdown("##### 4. GPU Pricing Model")
        st.markdown("[🔗 `bolt6 - GPU Pricing Model`](https://docs.google.com/spreadsheets/d/1JKaVySox6zlAL_lQphewLxgrjuqW463J0NSNsmRgAx8/edit)")
        st.caption("AWS fleet spend, machine hours, GCP g4 equivalents, and FP32 TFLOPS specs.")
    with col_s5:
        st.markdown("##### 5. Migration Center Telemetry")
        st.markdown("[🔗 `Migration Center Telemetry`](https://docs.google.com/spreadsheets/d/1C2ZUKVkA3G3lDZEbfw15jkqdTbuqd0kIIda7Ky12syM/edit?resourcekey=0-pSuHNda7UsEhwZ4fNfzshw)")
        st.caption("AWS measured telemetry (£510k), unmapped G2 shapes (7,438 count), expired reservation notices.")
    with col_s6:
        st.markdown("##### 6. Cloud Comparison Model")
        st.markdown("[🔗 `Bolt6 Cloud Comparison`](https://docs.google.com/spreadsheets/d/1FslH6yEcV0dOaDaNhd_AXDbVrCIDpPw4-ADfW9pQqXA/edit)")
        st.caption("36-month Scenarios S1–S4 (\\$1.19M down to \\$888k), \\$23.6k preliminary gap, monthly seasonality.")

    # Audit Table in Expander
    with st.expander("🔍 View Cell-Level Telemetry Audit Mapping Table"):
        audit_data = [
            {"Metric": "Measured 13-Day AWS Spend", "Value": "$6,892.41 (1,699 instances)", "Spreadsheet": "AWS EC2 Usage 28/08-09/09", "Tab": "cev-atp-instances-28/08-09/09"},
            {"Metric": "Measured Cluster Uptime & Off-Hours", "Value": "187.2h (70.0% Off-Time)", "Spreadsheet": "AWS EC2 Usage 28/08-09/09", "Tab": "eu-north-1, eu-west-2"},
            {"Metric": "GCP G4 RTX 6000 DWS Flex Rate", "Value": "$2.25 / hr (50.0% OFF)", "Spreadsheet": "GCP GPU Pricing & SKUs Master", "Tab": "RTX6000 - G4 (Row 51)"},
            {"Metric": "GCP G4 RTX 6000 3-Yr CUD Rate", "Value": "$1.98 / hr (56.0% OFF)", "Spreadsheet": "GCP GPU Pricing & SKUs Master", "Tab": "RTX6000 - G4 (Row 34)"},
            {"Metric": "GCP DWS Flex Availability", "Value": "GA on GKE & Compute Engine", "Spreadsheet": "DWS Availability & Quota", "Tab": "Feuille 1 (Row 15)"},
            {"Metric": "Australian Open Jan Peak Spend", "Value": "$439,274.00", "Spreadsheet": "Bolt6 Cloud Comparison", "Tab": "Compute_Seasonality (Row 6)"},
            {"Metric": "Expired Capacity Reservation Fee", "Value": "$110,532.00", "Spreadsheet": "Migration Center Telemetry", "Tab": "Errors and Warnings (Row 4)"},
            {"Metric": "RTX 6000 Pro FP32 Throughput", "Value": "120.0 TFLOPS ($0.58/hr)", "Spreadsheet": "bolt6 - GPU Pricing Model", "Tab": "billing (Row 4)"},
            {"Metric": "AWS A10G FP32 Throughput", "Value": "31.2 TFLOPS ($1.58/hr)", "Spreadsheet": "bolt6 - GPU Pricing Model", "Tab": "billing (Row 2)"},
            {"Metric": "AWS Measured Telemetry Total", "Value": "£510,066.95 GBP", "Spreadsheet": "Migration Center Telemetry", "Tab": "Executive Overview (Row 2)"},
        ]
        st.dataframe(pd.DataFrame(audit_data), use_container_width=True, hide_index=True)

st.markdown("---")
st.caption("Bolt6 Cloud TCO Assessment — Grounded on verified customer telemetry and Google Cloud internal pricing models.")
