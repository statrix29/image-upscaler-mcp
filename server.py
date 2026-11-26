import os
import pathlib
import subprocess
import tempfile
from typing import Literal, get_args

from mcp.server.fastmcp import FastMCP

ROOT = pathlib.Path(__file__).parent.resolve()
BIN = ROOT / "bin" / "upscayl-bin"
MODELS_DIR = ROOT / "models"

Model = Literal[
    "upscayl-standard-4x",
    "upscayl-lite-4x",
    "remacri-4x",
    "ultrasharp-4x",
    "ultramix-balanced-4x",
    "high-fidelity-4x",
    "digital-art-4x",
]

mcp = FastMCP("image-upscaler")


@mcp.tool()
def upscale_image(
    input_path: str,
    output_path: str | None = None,
    scale: int = 4,
    model: Model = "upscayl-standard-4x",
) -> str:
    """Upscale a local image file using a GPU-accelerated Real-ESRGAN model (runs locally via Metal on Apple Silicon).

    Use this whenever the user asks to upscale, enlarge, enhance, super-resolve, or increase the resolution of an image.

    Args:
        input_path: Absolute path to the input image (jpg, png, or webp). Tilde expansion is supported.
        output_path: Absolute path for the output. If omitted, writes next to the input as "<stem>_upscaled_<N>x.png".
        scale: Output scale factor. One of 2, 3, or 4. Default 4.
        model: Which AI model to use. Default "upscayl-standard-4x" is best for photos. Use "upscayl-lite-4x" for speed, "digital-art-4x" for illustrations, "remacri-4x"/"ultrasharp-4x" for sharper textures.

    Returns:
        Absolute path to the upscaled image file.
    """
    if scale not in (2, 3, 4):
        raise ValueError(f"scale must be 2, 3, or 4 (got {scale})")
    if model not in get_args(Model):
        raise ValueError("choose one of the installed upscaling models")

    inp = pathlib.Path(input_path).expanduser().resolve()
    if not inp.is_file():
        raise FileNotFoundError(f"input image not found: {inp}")
    if inp.suffix.lower() not in {".jpg", ".jpeg", ".png", ".webp"}:
        raise ValueError("choose a JPEG, PNG, or WebP input")

    if output_path:
        out = pathlib.Path(output_path).expanduser().absolute()
    else:
        out = inp.with_name(f"{inp.stem}_upscaled_{scale}x.png")
    if out.suffix.lower() not in {".jpg", ".jpeg", ".png", ".webp"}:
        raise ValueError("choose a JPEG, PNG, or WebP output")
    if os.path.lexists(out):
        raise FileExistsError(f"output already exists: {out}")
    out.parent.mkdir(parents=True, exist_ok=True)

    with tempfile.TemporaryDirectory(prefix=".upscale-", dir=out.parent) as directory:
        staged = pathlib.Path(directory) / f"output{out.suffix.lower()}"
        result = subprocess.run(
            [
                str(BIN), "-i", str(inp), "-o", str(staged),
                "-s", str(scale), "-n", model, "-m", str(MODELS_DIR),
            ],
            capture_output=True,
            text=True,
        )
        if result.returncode != 0:
            raise RuntimeError(
                f"upscayl-bin failed (exit {result.returncode}):\n"
                f"stdout: {result.stdout}\nstderr: {result.stderr}"
            )
        if not staged.is_file():
            raise RuntimeError("upscayl-bin completed without producing an image")
        os.link(staged, out)

    return str(out)


@mcp.tool()
def list_upscaler_models() -> list[dict]:
    """List the available upscaler models with short descriptions of what each is best for."""
    return [
        {"name": "upscayl-standard-4x", "best_for": "general photos (default)"},
        {"name": "upscayl-lite-4x", "best_for": "speed / low-memory; lower quality"},
        {"name": "remacri-4x", "best_for": "sharper textures and detail"},
        {"name": "ultrasharp-4x", "best_for": "very sharp output; can over-sharpen"},
        {"name": "ultramix-balanced-4x", "best_for": "balanced sharpness and softness"},
        {"name": "high-fidelity-4x", "best_for": "preserving original detail faithfully"},
        {"name": "digital-art-4x", "best_for": "illustrations, anime, line art"},
    ]


if __name__ == "__main__":
    mcp.run(transport="stdio")
