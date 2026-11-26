# Image Upscaler for macOS

Upscale images locally on your Mac’s GPU. Use the `upscale` command from Terminal or connect the local server to an MCP client. Image processing stays on your Mac. The first setup downloads Upscayl, model weights, and Python dependencies.

## Quickstart

Use macOS with a Metal-capable GPU, Python 3.10 or later, and ImageMagick 7. The examples were tested on Apple Silicon with Python 3.14. Install ImageMagick with `brew install imagemagick` if you use Homebrew.

```sh
git clone https://github.com/statrix29/image-upscaler-mcp.git
cd image-upscaler-mcp
./install.sh
./upscale examples/mountain.png -o examples/mountain-upscaled.png
```

The input is 192 × 128 pixels. The command writes a new 768 × 512 PNG and prints its path. The [input](examples/mountain.png) and [example result](examples/mountain-4x.png) are included.

| Task | Example |
| --- | --- |
| Double both dimensions | `./upscale photo.jpg --scale 2` |
| Set the width and preserve proportions | `./upscale photo.heic --width 2400` |
| Fill a 4K landscape canvas | `./upscale photo.jpg --size 4k --fit crop -o wallpaper.jpg` |
| Fit within a canvas and pad the edges | `./upscale photo.jpg --size 1920x1080 --fit pad --background black` |
| Upscale line art | `./upscale art.png --model digital-art` |

The command accepts PNG, JPEG, WebP, HEIC, HEIF, and TIFF inputs. It writes PNG, JPEG, or WebP. `--force` replaces an existing output when requested. Run `./upscale --help` for fractional scales, presets, aspect ratios, print density, and compression.

## Use with an MCP client

Run `./install.sh` first. Configure a local **stdio** server that runs the repository’s `.venv/bin/python` with `server.py` as its only argument. Use absolute paths to your cloned repository. For clients that accept JSON server configuration, the paths go in this entry.

```json
{
  "mcpServers": {
    "image-upscaler": {
      "command": "/absolute/path/to/image-upscaler-mcp/.venv/bin/python",
      "args": ["/absolute/path/to/image-upscaler-mcp/server.py"]
    }
  }
}
```

The server exposes `upscale_image` for JPEG, PNG, and WebP at 2×, 3×, or 4× and `list_upscaler_models` for model names. The server runs with the same local file permissions as its client. It creates a new output file and rejects existing destinations.

## Upstream software and license

The installer downloads the [Upscayl engine](https://github.com/upscayl/upscayl-ncnn) and [Upscayl model files](https://github.com/upscayl/upscayl/tree/main/resources/models) directly from upstream. The MCP server uses the [MCP Python SDK](https://github.com/modelcontextprotocol/python-sdk). The Terminal command uses [ImageMagick](https://imagemagick.org/). These dependencies and models retain their own terms.

This repository’s wrapper code is source-available under the [PolyForm Strict License 1.0.0](LICENSE). For a commercial license, open a [licensing inquiry](https://github.com/statrix29/image-upscaler-mcp/issues/new?title=Commercial%20licensing%20inquiry).
