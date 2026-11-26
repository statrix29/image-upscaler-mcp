#!/usr/bin/env bash
set -euo pipefail

root="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
release="20251207-174704"
engine_url="https://github.com/upscayl/upscayl-ncnn/releases/download/$release/upscayl-bin-$release-macos.zip"
engine_sha256="277419791281a56eae0c739c70120b974d7267cf7c2de8e86dc09798d4b314db"
models_ref="a00d55fee90e0f9435d5eaa86e76700df8199af8"
models_url="https://raw.githubusercontent.com/upscayl/upscayl/$models_ref/resources/models"
models=(
    upscayl-standard-4x upscayl-lite-4x digital-art-4x high-fidelity-4x
    remacri-4x ultrasharp-4x ultramix-balanced-4x
)

if [[ "$(uname -s)" != Darwin ]]; then
    printf 'This installer requires macOS.\n' >&2
    exit 1
fi
python3 -c 'import sys; sys.exit(sys.version_info < (3, 10))' || {
    printf 'Install Python 3.10 or newer and make sure python3 is on PATH.\n' >&2
    exit 1
}

mkdir -p "$root/bin" "$root/models"
work="$(mktemp -d "$root/.install.XXXXXXXX")"
trap 'rm -rf -- "$work"' EXIT
download() {
    curl --fail --silent --show-error --location --retry 2 "$1" --output "$2"
}

printf 'Downloading Upscayl engine %s\n' "$release"
download "$engine_url" "$work/engine.zip"
printf '%s  %s\n' "$engine_sha256" "$work/engine.zip" | shasum -a 256 -c
unzip -q "$work/engine.zip" -d "$work/engine"
engine="$(find "$work/engine" -type f -name upscayl-bin -print -quit)"
if [[ -z "$engine" ]]; then
    printf 'Upscayl executable missing from the verified archive.\n' >&2
    exit 1
fi
install -m 755 "$engine" "$work/upscayl-bin"
mv -f "$work/upscayl-bin" "$root/bin/upscayl-bin"

for model in "${models[@]}"; do
    printf 'Downloading %s\n' "$model"
    for ext in bin param; do
        filename="$model.$ext"
        download "$models_url/$filename" "$work/$filename"
        mv -f "$work/$filename" "$root/models/$filename"
    done
done

python3 -m venv "$root/.venv"
"$root/.venv/bin/python" -m pip install -r "$root/requirements.txt"
printf 'Setup complete. Run %s/upscale --help to get started.\n' "$root"
