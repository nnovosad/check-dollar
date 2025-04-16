import cv2
import numpy as np
from fastapi import FastAPI, Request, File, UploadFile
from fastapi.templating import Jinja2Templates

app = FastAPI()
templates = Jinja2Templates(directory="templates")


@app.get("/")
def read_root():
    return {"Hello": "World"}


@app.get("/index")
async def get_index_page(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})


@app.post("/check/")
async def check_file(request: Request, file: UploadFile = File(...)):
    result = await get_result(file)  # Здесь обязательно await

    return templates.TemplateResponse(
        "result.html",
        {"result": result, "request": request}
    )


async def get_result(file: UploadFile):
    contents = await file.read()  # Читаем файл асинхронно

    # Преобразуем в numpy array и декодируем изображение
    nparr = np.frombuffer(contents, np.uint8)
    image = cv2.imdecode(nparr, cv2.IMREAD_COLOR)

    if image is None:
        return "Не удалось загрузить изображение"

    # Обработка изображения
    hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)

    lower_white = np.array([0, 0, 200])
    upper_white = np.array([180, 30, 255])
    lower_blue = np.array([90, 50, 50])
    upper_blue = np.array([130, 255, 255])

    mask_white = cv2.inRange(hsv, lower_white, upper_white)
    mask_blue = cv2.inRange(hsv, lower_blue, upper_blue)
    mask = cv2.bitwise_or(mask_white, mask_blue)

    contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    valid_areas = []
    for contour in contours:
        x, y, w, h = cv2.boundingRect(contour)
        area = w * h
        if (w <= 30 and h <= 30) or (area <= 900):
            valid_areas.append((x, y, w, h))

    return "Купюра соответствует требованиям" if valid_areas else "Купюра не соответствует требованиям"