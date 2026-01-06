# Quick helper to run the server using .env values
$env:APP_NAME="VMC Bridge Backend"
. .\.env

$host = $env:HOST -or "127.0.0.1"
$port = $env:PORT -or "8000"

uvicorn app.main:app --reload --host $host --port $port
