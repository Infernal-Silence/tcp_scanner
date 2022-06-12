from flask import Flask, jsonify, request
import asyncio
import aiohttp
import syslog


app = Flask(__name__)


async def check_port(ip, port):
    syslog.syslog(f'Scanning {ip}:{port}')
    async with aiohttp.ClientSession(
            connector=aiohttp.TCPConnector(ssl=False), timeout=aiohttp.ClientTimeout(total=5)
    ) as session:
        try:
            async with session.get(f'http://{ip}:{port}') as _response:
                return {"port": port, "state": "open"}
        except (aiohttp.ClientConnectorError, asyncio.TimeoutError) as e:
            syslog.syslog(f'Got an exception: {e}')
            return {"port": port, "state": "close"}


@app.route('/scan/<ip>/<int:begin_port>/<int:end_port>')
async def scan_ip(ip, begin_port, end_port):
    syslog.syslog(f'Received request from {request.remote_addr}')
    tasks = []
    for p in range(begin_port, end_port + 1):
        tasks.append(check_port(ip, p))
    results = await asyncio.gather(*tasks)
    return jsonify(results)


if __name__ == '__main__':
    app.run()
