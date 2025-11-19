
from train.scripts_cli import generate_gemini_cli_script
import asyncio

sc = generate_gemini_cli_script("hello", "gemini-2.5-pro", True)


async def run_t():
    proc = await asyncio.create_subprocess_shell(
        sc,
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE,
        shell=True
    )
    print(sc)
    async def read_stream(stream, prefix):
        """Read and print stream line by line in real-time."""
        lines = []
        while True:
            line = await stream.readline()
            if not line:
                break
            decoded = line.decode('utf-8', errors='ignore').rstrip()
            print(f"{prefix}: {decoded}")
            lines.append(decoded)
        return "\n".join(lines)
    
    stdout_str, stderr_str, _ = await asyncio.wait_for(
        asyncio.gather(
            read_stream(proc.stdout, f"[]"),
            read_stream(proc.stderr, f"[ERR]"),
            proc.wait()
        ),
        timeout=100000
    )

#     print("STDOUT:", stdout_str.decode())
#     print("STDERR:", stderr_str.decode())
asyncio.run(run_t())
