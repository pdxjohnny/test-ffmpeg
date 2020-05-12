import os
import asyncio
import tempfile

from dffml import op, Definition


@op(
    inputs={
        "input_file": Definition(name="input_file", primitive="bytes"),
        "resolution": Definition(name="Resolution", primitive="int"),
    },
    outputs={"output_file": Definition(name="output_file", primitive="bytes")},
)
async def convert_to_gif(input_file, resolution):
    with tempfile.NamedTemporaryFile(
        prefix="ffmpeg-", suffix=".mp4", delete=False
    ) as temp_input_file:
        temp_input_file.write(input_file)
        temp_input_file.seek(0)
        os.fsync(temp_input_file.fileno())
        proc = await asyncio.create_subprocess_exec(
            # "strace",
            # "-y",
            # "-yy",
            # "-o",
            # "/tmp/ffmpeg.trace",
            # "--",
            # "/snap/bin/ffmpeg",
            "ffmpeg",
            "-ss",
            "0.3",
            "-t",
            "10",
            "-i",
            temp_input_file.name,
            "-y",
            "-vf",
            f"fps=10,scale={resolution}:-1:flags=lanczos,split[s0][s1];[s0]palettegen[p];[s1][p]paletteuse",
            "-loop",
            "0",
            "-f",
            "gif",
            "pipe:1",
            stdout=asyncio.subprocess.PIPE,
        )
        out, error = await proc.communicate()
        return {"output_file": out}
