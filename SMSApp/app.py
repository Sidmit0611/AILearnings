from fastapi import FastAPI, Request

app = FastAPI()

@app.api_route("/sms", methods=["POST", "GET"])
async def receive_sms(request: Request):
    content_type = request.headers.get("content-type", "")
    
    print("\n--- NEW REQUEST ---")
    print("Method:", request.method)
    print("Headers:", dict(request.headers))

    if "application/json" in content_type:
        data = await request.json()
    elif "application/x-www-form-urlencoded" in content_type:
        data = await request.form()
        data = dict(data)
    else:
        data = await request.body()
        data = data.decode("utf-8")

    print("Received SMS:", data)
    return {"status": "ok"}
