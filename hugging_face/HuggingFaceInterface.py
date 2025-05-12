import asyncio
import json
import os
import sys
from typing import List

from collector_db.DTOs.URLWithHTML import URLWithHTML

class HuggingFaceInterface:

    @staticmethod
    async def get_url_relevancy_async(urls_with_html: List[URLWithHTML]) -> List[bool]:
        urls = [u.url for u in urls_with_html]
        input_data = json.dumps(urls)

        proc = await asyncio.create_subprocess_exec(
            sys.executable, "hugging_face/relevancy_worker.py",
            stdin=asyncio.subprocess.PIPE,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
            env=os.environ.copy(),  # ⬅️ ensure env variables are inherited
        )

        stdout, stderr = await proc.communicate(input=input_data.encode("utf-8"))
        print(stderr)

        raw_output = stdout.decode("utf-8").strip()

        if proc.returncode != 0:
            raise RuntimeError(f"Error running HuggingFace: {stderr}/{raw_output}")

        # Try to extract the actual JSON line
        for line in raw_output.splitlines():
            try:
                return json.loads(line)
            except json.JSONDecodeError as e:
                continue

        raise RuntimeError(f"Could not parse JSON from subprocess: {raw_output}")

