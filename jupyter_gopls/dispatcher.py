from tornado.concurrent import run_on_executor
from tornado.gen import convert_yielded
from pathlib import Path
from jupyter_lsp.types import EditableFile, ShadowFileSystem


class GoFile(EditableFile):
    def __init__(self, path):
        # Python 3.5 relict:
        self.path = Path(path) if isinstance(path, str) else path

        if path.endswith(".ipynb"):
            self.path = self.path.with_suffix(".go")

    async def read(self):
        self.lines = await convert_yielded(self.read_lines())

    async def write(self):
        return await convert_yielded(self.write_lines())

    @run_on_executor
    def read_lines(self):
        # empty string required by the assumptions of the gluing algorithm
        lines = [""]
        try:
            # TODO: what to do about bad encoding reads?
            lines = self.path.read_text(encoding="utf-8").splitlines()

        except FileNotFoundError:
            pass
        return lines

    @run_on_executor
    def write_lines(self):
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self.path.write_text("\n".join(self.lines), encoding="utf-8")

    # @staticmethod
    # def trim(lines: list, character: int, side: int):
    #     needs_glue = False
    #     if lines:
    #         trimmed = lines[side][character:]
    #         if lines[side] != trimmed:
    #             needs_glue = True
    #         lines[side] = trimmed
    #     return needs_glue

    # @staticmethod
    # def join(left, right, glue: bool):
    #     if not glue:
    #         return []
    #     return [(left[-1] if left else "") + (right[0] if right else "")]

    def apply_change(self, text: str, start, end):
        before = self.lines[: start["line"]]
        after = self.lines[end["line"] :]

        needs_glue_left = self.trim(lines=before, character=start["character"], side=0)
        needs_glue_right = self.trim(lines=after, character=end["character"], side=-1)

        inner = text.split("\n")

        self.lines = (
            before[: -1 if needs_glue_left else None]
            + self.join(before, inner, needs_glue_left)
            + inner[1 if needs_glue_left else None : -1 if needs_glue_right else None]
            + self.join(inner, after, needs_glue_right)
            + after[1 if needs_glue_right else None :]
        ) or [""]

    @property
    def full_range(self):
        start = {"line": 0, "character": 0}
        end = {
            "line": len(self.lines),
            "character": len(self.lines[-1]) if self.lines else 0,
        }
        return {"start": start, "end": end}


class ShadowGoFileSystem(ShadowFileSystem):
    @classmethod
    def get_file(self, path: str) -> EditableFile:
        return GoFile(path)
