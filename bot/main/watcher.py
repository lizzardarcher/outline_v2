import asyncio
import os
from pathlib import Path

from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
async def file_event_handler() -> None:
    folder = Path(__file__).resolve().parent.parent

    class EventHandler(FileSystemEventHandler):
        def on_any_event(self, event):
            wsgi = Path(__file__).parent.parent.joinpath('outline_v2').joinpath('wsgi.py').resolve()
            os.system(f'touch {wsgi}')

    path = f"{folder}"
    event_handler = EventHandler()
    observer = Observer()
    observer.schedule(event_handler, path, recursive=True)
    observer.start()
    try:
        while True:
            await asyncio.sleep(1)
    except KeyboardInterrupt:
        observer.stop()
    observer.join()

if __name__ == '__main__':
    asyncio.run(file_event_handler())