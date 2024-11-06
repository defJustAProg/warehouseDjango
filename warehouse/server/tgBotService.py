import httpx
from django.http import JsonResponse

async def send_record_to_bot(bot_url, record):
    try:
        async with httpx.AsyncClient() as client:
            await client.post(f"{bot_url}/sendMessage", json=record.to_dict())
            return JsonResponse({"message": "Roll sent to bot."}, status=200)
    except httpx.HTTPStatusError:
        return JsonResponse({"message": "Roll failed to send to bot."}, status=503)