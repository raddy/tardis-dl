import typer, jsonlines
from tardis_request import DatasetDownload, DownloadParams, DownloadRequest, TardisGenerator
from settings import TARDIS_KEY, CACHE_DIR
from rich import print
import asyncio

app = typer.Typer(name="tardis-dl", add_completion=False, help="Tool for downloading Tardis MD")

async def save(generator : TardisGenerator, file_name : str):
    with jsonlines.open(file_name, mode='w') as writer:
        async for local_timestamp, message in generator.messages:
            message['local_time'] = local_timestamp.isoformat()
            writer.write(message)

def file_name(params : DownloadParams):
    return f"{params.exchange}_{params.symbols[0]}_{params.date}_{params.msg_type}.ndjson"

def download_via_generator(params : DownloadParams):
    request = DownloadRequest(params, CACHE_DIR, TARDIS_KEY)
    generator = TardisGenerator(request)
    asyncio.run(save(generator, file_name(params)))

def download_via_datasets(params : DownloadParams):
    request = DownloadRequest(params, CACHE_DIR, TARDIS_KEY)
    download = DatasetDownload(request)

@app.command()
def main(exchange : str = typer.Argument(..., help = "exchange name"), 
         date : str = typer.Argument(..., help = "date as YYYY-MM-DD"),
         msg_type : str = typer.Argument(..., help = "message type to download"),
         symbol : str = typer.Argument(..., help = "remote exchange symbols (comma separated, no spaces)"),
         csv : bool = typer.Option(False, is_flag=True)):
    
    params = DownloadParams(exchange, date, msg_type, [symbol])
    if not csv:
        download_via_generator(params)
    else:
        download_via_datasets(params)

if __name__ == '__main__':
    app()