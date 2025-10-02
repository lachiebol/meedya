from typing import List, Dict, Optional
from pydantic import BaseModel, Field

class SubtitleEntry(BaseModel):
    index: int
    timestamp: str
    text: str


class Subtitle(BaseModel):
    file_path: str
    format: str
    language: Optional[str] = None
    entries: List[SubtitleEntry] = Field(default_factory=list)

    def add_entry(self, index: int, timestamp: str, text: str):
        entry = SubtitleEntry(index=index, timestamp=timestamp, text=text)
        self.entries.append(entry)

    def save(self, path: str):
        self.file_path = path
        with open(self.file_path, 'w', encoding='utf-8') as f:
            for entry in self.entries:
                f.write(f"{entry.index}\n")
                f.write(f"{entry.timestamp}\n")
                f.write(f"{entry.text}\n\n")

    def get_entry_count(self) -> int:
        return len(self.entries)

    def __str__(self):
        return f"Subtitle({self.file_path}, {self.format}, {len(self.entries)} entries)"

    def __repr__(self):
        return f"Subtitle({self.file_path}, {self.format})"
