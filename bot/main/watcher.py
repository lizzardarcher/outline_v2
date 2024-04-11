import asyncio
import os
from pathlib import Path

from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler


async def file_event_handler() -> None:
    class EventHandler(FileSystemEventHandler):
        def on_modified(self, event):
            print(event)
            wsgi = Path(__file__).parent.parent.parent.joinpath('outline_v2').joinpath('wsgi.py').resolve()
            os.system(f'touch {wsgi}')

    event_handler = EventHandler()
    observer = Observer()
    observer.schedule(event_handler, path=f"{Path(__file__).resolve().parent.parent.joinpath('admin.py')}" , recursive=False)
    observer.schedule(event_handler, path=f"{Path(__file__).resolve().parent.parent.joinpath('models.py')}", recursive=False)
    observer.start()
    try:
        while True:
            await asyncio.sleep(1)
    finally:
        observer.stop()
        observer.join()


if __name__ == '__main__':
    print(f"{Path(__file__).resolve().parent.parent.joinpath('admin.py')}" )
    print(f"{Path(__file__).resolve().parent.parent.joinpath('models.py')}")
    asyncio.run(file_event_handler())
