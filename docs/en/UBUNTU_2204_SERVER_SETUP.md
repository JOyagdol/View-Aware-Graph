# Ubuntu 22.04 Server Setup

Last updated: 2026-05-28

## Target

This document describes the recommended Ubuntu 22.04 Server VM setup for local View-Aware Graph VLM inference.

Target VM:

```text
OS: Ubuntu 22.04 Server LTS
RAM: 64 GiB
Swap: 8 GiB
Disk: 64 GiB
GPU: RTX 5090 passthrough, preferably one GPU first
Runtime: Ollama local inference
Python: system Python is acceptable for this dedicated VM
```

This setup is for inference-only prompt engineering, not model training.

## Proxmox Notes

If the GPUs are passed through to the Ubuntu VM, install NVIDIA drivers inside the Ubuntu guest.

Do not bind the passed-through GPU to the NVIDIA driver on the Proxmox host. The host should reserve the GPU for passthrough, typically through `vfio-pci`.

Start with one GPU passed through. After `nvidia-smi` and Ollama work reliably, add the second GPU.

## Driver Recommendation

Use NVIDIA driver branch `570` or newer.

Reason:

- NVIDIA Linux driver `570.86.16` added official GeForce RTX 5090 support.
- Ubuntu Server documentation recommends the `ubuntu-drivers` tool for command-line driver installation.
- For server/compute use, Ubuntu documents Enterprise Ready Driver packages with the `-server` suffix.

Recommended first attempt on Ubuntu 22.04 Server:

```bash
sudo apt update
sudo apt upgrade -y
sudo reboot
```

After reboot:

```bash
sudo apt install -y ubuntu-drivers-common
sudo ubuntu-drivers list --gpgpu
```

If a 570 server package is available:

```bash
sudo ubuntu-drivers install --gpgpu nvidia:570-server
sudo apt install -y nvidia-utils-570-server
sudo reboot
```

If Ubuntu recommends a newer branch such as 580 or 590 for the RTX 5090, use the recommended newer branch instead:

```bash
sudo ubuntu-drivers install --gpgpu
sudo reboot
```

Avoid older 535/550 branches for RTX 5090.

## Driver Verification

After reboot:

```bash
nvidia-smi
cat /proc/driver/nvidia/version
```

Expected:

- RTX 5090 devices are visible.
- Driver version is 570 or newer.
- CUDA version shown by `nvidia-smi` is sufficient for Ollama/PyTorch runtime use.

If `nvidia-smi` fails with a driver/library mismatch, reboot once more.

If `nvidia-smi` reports no devices, check whether passthrough is configured correctly and whether `nouveau` is loaded:

```bash
lsmod | grep nouveau
```

## Base Packages

Install only the server tools needed for this project:

```bash
sudo apt update
sudo apt install -y \
  git \
  curl \
  ca-certificates \
  build-essential \
  openssh-server \
  python3 \
  python3-pip \
  tmux \
  htop \
  nvtop
```

Conda is not required on this dedicated VM.

Python is only needed for lightweight project utilities such as schema validation, parser checks, and future CLI code.

## OpenSSH Setup

Install and enable OpenSSH:

```bash
sudo apt install -y openssh-server
sudo systemctl enable --now ssh
sudo systemctl status ssh --no-pager
```

Check the VM IP address:

```bash
ip addr
```

From the client machine:

```bash
ssh <user>@<vm-ip>
```

Recommended key-based login:

```bash
mkdir -p ~/.ssh
chmod 700 ~/.ssh
```

On the client machine, copy the public key:

```bash
ssh-copy-id <user>@<vm-ip>
```

If `ssh-copy-id` is unavailable, append the public key manually to:

```text
~/.ssh/authorized_keys
```

Then set permissions inside the VM:

```bash
chmod 600 ~/.ssh/authorized_keys
```

Recommended SSH daemon settings:

```bash
sudo cp /etc/ssh/sshd_config /etc/ssh/sshd_config.bak
sudo nano /etc/ssh/sshd_config
```

Use these values unless the local network requires something different:

```text
PermitRootLogin no
PasswordAuthentication yes
PubkeyAuthentication yes
X11Forwarding no
ClientAliveInterval 60
ClientAliveCountMax 5
```

After key login is confirmed, optionally disable password login:

```text
PasswordAuthentication no
```

Restart SSH:

```bash
sudo systemctl restart ssh
```

If using UFW:

```bash
sudo ufw allow OpenSSH
sudo ufw status
```

Do not disable password login until key login has been tested from a second terminal.

## tmux Setup

Use tmux for long Ollama pulls, model runs, and SSH-safe monitoring.

Create a minimal user config:

```bash
cat > ~/.tmux.conf <<'EOF'
set -g mouse on
set -g history-limit 50000
set -g base-index 1
setw -g pane-base-index 1
set -g status-interval 5
set -g status-right "%Y-%m-%d %H:%M"
setw -g mode-keys vi
bind r source-file ~/.tmux.conf \; display-message "tmux config reloaded"
EOF
```

Recommended sessions:

```bash
tmux new -s vag
```

Detach:

```text
Ctrl-b d
```

Reattach:

```bash
tmux attach -t vag
```

Useful panes:

```bash
nvidia-smi -l 1
```

```bash
watch -n 2 free -h
```

```bash
watch -n 5 df -h
```

## Ollama Setup

Install Ollama:

```bash
curl -fsSL https://ollama.com/install.sh | sh
ollama --version
```

Check service status:

```bash
systemctl status ollama --no-pager
```

With a 64 GiB VM disk, keep only the models currently under test.

Recommended model order:

```bash
ollama pull qwen2.5vl:7b
```

Then test one 32B model at a time:

```bash
ollama pull qwen2.5vl:32b
```

If testing Qwen3-VL 32B, remove the previous 32B model first if disk space is tight:

```bash
ollama rm qwen2.5vl:32b
ollama pull qwen3-vl:32b
```

## Disk Management

The 64 GiB VM disk is tight but workable if only one 32B model is kept at a time.

Monitor disk usage:

```bash
df -h
du -sh ~/.ollama
ollama list
```

Clean package cache:

```bash
sudo apt clean
sudo journalctl --vacuum-time=3d
```

Remove unused Ollama models:

```bash
ollama rm <model-name>
```

## Project Setup

Clone the repository:

```bash
git clone https://github.com/JOyagdol/View-Aware-Graph.git
cd View-Aware-Graph
```

Install minimal Python dependencies only if schema validation or project CLI scripts are needed.

Use `python3.11` on this Ubuntu server. Do not change the system `python3` default, because Ubuntu 22.04 uses Python 3.10 for OS packages.

```bash
python3.11 -m pip install --user -e .
```

For development tools:

```bash
python3.11 -m pip install --user -e ".[dev]"
```

## Smoke Test Flow

1. Confirm GPU:

```bash
nvidia-smi
```

2. Pull first model:

```bash
ollama pull qwen2.5vl:7b
```

3. Run the prompt in:

```text
prompts/view_graph_extraction.md
```

4. Store raw VLM output under ignored local paths:

```text
data/interim/vlm_raw/
data/processed/view_graphs/
```

5. Validate generated JSON with the project schema.

## References

- Ubuntu Server NVIDIA driver installation: https://ubuntu.com/server/docs/how-to/graphics/install-nvidia-drivers/
- NVIDIA RTX 5090 Linux driver 570.86.16: https://www.nvidia.com/en-us/drivers/details/240524/
- NVIDIA CUDA Linux installation guide: https://docs.nvidia.com/cuda/cuda-installation-guide-linux/
- Ollama Qwen2.5-VL models: https://ollama.com/library/qwen2.5vl
- Ollama Qwen3-VL models: https://ollama.com/library/qwen3-vl
