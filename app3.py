import streamlit as st
import subprocess
import json
import shutil
import statistics
import time

# Optional fallback library
try:
    import speedtest as speedtest_lib  # speedtest-cli (python)
except ImportError:
    speedtest_lib = None

st.set_page_config(page_title="Accurate Internet Speed Test", page_icon="⚡", layout="centered")
st.title("⚡ Accurate Internet Speed Test")

# -------------------- Settings / Controls --------------------
col1, col2, col3 = st.columns(3)
passes = col1.number_input("Number of passes", 1, 5, 2)
warmup = col2.checkbox("Do 1 warm-up run (discard)", value=True)
auto_filter = col3.checkbox("Filter unrealistic spikes", value=True)

use_cli_only = st.checkbox("Force official CLI only (fail if missing)", value=False)

st.caption(
    "This tool prefers Ookla official CLI (more accurate). "
    "If unavailable, it falls back to Python speedtest-cli unless 'Force CLI' is enabled."
)

run_btn = st.button("Run Test")

# -------------------- Helper Functions --------------------
def human(mbps: float) -> str:
    return f"{mbps:.2f} Mbps ({(mbps/8):.2f} MB/s)"

def find_cli():
    return shutil.which("speedtest")  # returns path or None

def run_cli_once():
    """
    Run official CLI once, return dict with download_mbps, upload_mbps, ping_ms, server, isp.
    """
    cli_path = find_cli()
    if not cli_path:
        raise FileNotFoundError("Official speedtest CLI not found in PATH.")
    # -f json for machine output
    proc = subprocess.run([cli_path, "-f", "json"], capture_output=True, text=True)
    if proc.returncode != 0:
        raise RuntimeError(f"CLI error: {proc.stderr.strip()}")
    data = json.loads(proc.stdout)
    # Newer CLI JSON format fields:
    dl_bps = data["download"]["bandwidth"] * 8  # 'bandwidth' is bytes/second, convert to bits/sec
    ul_bps = data["upload"]["bandwidth"] * 8
    ping_ms = data["ping"]["latency"]
    server_name = data["server"].get("name")
    isp = data.get("isp")
    return {
        "download_mbps": dl_bps / 1_000_000,
        "upload_mbps": ul_bps / 1_000_000,
        "ping_ms": ping_ms,
        "server": server_name,
        "isp": isp,
        "source": "cli"
    }

def run_lib_once():
    """
    Run python speedtest-cli library once.
    """
    if speedtest_lib is None:
        raise RuntimeError("speedtest-cli library not installed and CLI not available.")
    stt = speedtest_lib.Speedtest()
    stt.get_best_server()
    dl = stt.download() / 1_000_000  # bits/s -> Mbps
    ul = stt.upload() / 1_000_000
    ping = stt.results.ping
    server = stt.results.server.get("name")
    isp = stt.results.client.get("isp")
    return {
        "download_mbps": dl,
        "upload_mbps": ul,
        "ping_ms": ping,
        "server": server,
        "isp": isp,
        "source": "python-lib"
    }

def sanitize(values, threshold_factor=2.2):
    """
    Remove obvious spikes (e.g., one pass double the median).
    """
    if len(values) < 3:
        return values  # need at least 3 to sensibly filter
    dls = [v["download_mbps"] for v in values]
    median_dl = statistics.median(dls)
    filtered = [v for v in values if v["download_mbps"] <= median_dl * threshold_factor]
    return filtered if filtered else values  # don't empty everything

# -------------------- Execution --------------------
if run_btn:
    results = []
    cli_available = find_cli() is not None

    if use_cli_only and not cli_available:
        st.error("Official CLI not found. Install it or uncheck 'Force CLI only'.")
    else:
        method = "CLI" if cli_available else "Python speedtest-cli library"
        st.info(f"Using: **{method}**")
        placeholder = st.empty()

        total_runs = passes + (1 if warmup else 0)
        for i in range(total_runs):
            label = "Warm-up" if warmup and i == 0 else f"Pass {i if not warmup else i}"
            placeholder.write(f"Running {label}...")
            t_start = time.time()
            try:
                single = run_cli_once() if cli_available else run_lib_once()
                single["elapsed_s"] = time.time() - t_start
                # If warm-up and flagged, discard
                if warmup and i == 0:
                    placeholder.write("Warm-up complete. Discarded.")
                else:
                    results.append(single)
                    st.write(
                        f"**{label}** → Download: {single['download_mbps']:.2f} Mbps | "
                        f"Upload: {single['upload_mbps']:.2f} Mbps | "
                        f"Ping: {single['ping_ms']:.1f} ms"
                    )
            except Exception as e:
                st.error(f"{label} failed: {e}")
                break

        if results:
            raw_results = results.copy()

            if auto_filter:
                filtered = sanitize(results)
            else:
                filtered = results

            if auto_filter and len(filtered) != len(results):
                st.warning(
                    f"Filtered {len(results) - len(filtered)} spike(s) out of {len(results)} passes."
                )
                results = filtered

            avg_down = statistics.mean([r["download_mbps"] for r in results])
            avg_up = statistics.mean([r["upload_mbps"] for r in results])
            avg_ping = statistics.mean([r["ping_ms"] for r in results])

            st.subheader("Averages")
            st.write(f"**Average Download:** {human(avg_down)}")
            st.write(f"**Average Upload:** {human(avg_up)}")
            st.write(f"**Average Ping:** {avg_ping:.1f} ms")

            # Simple sanity flag
            if avg_down > 1000 and avg_down > 2 * avg_up:
                st.warning(
                    "Download speed looks unusually high ( >1000 Mbps ). "
                    "Verify with an external test (e.g., speedtest.net in a browser)."
                )

            meta = results[0]
            st.caption(
                f"Server: {meta.get('server', 'N/A')} | ISP: {meta.get('isp','N/A')} | "
                f"Method: {meta.get('source')} | Passes used: {len(results)}"
            )

            with st.expander("Raw JSON Results"):
                st.json(raw_results)
        else:
            st.error("No successful results to display.")
else:
    st.info("Set your options and click **Run Test** to begin.")
