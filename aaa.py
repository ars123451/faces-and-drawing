from pprint import pprint

import requests
import cv2
import bs4
import peewee

html = requests.get('https://skillbox.by/course/profession-python/').text

soup = bs4.BeautifulSoup(html, 'html.parser')
all_images = soup.find_all('img')


def draw_mustache(image, x, y, w, h):
    mh = h // 10
    mw = w * 2 // 5
    mx = x + w // 2 - mw // 2
    my = y + h * 2 // 3
    # cv2.rectangle(image, (mx, my), (mx+mw, my+mh), (255, 255, 0), 3)
    hair_w = max(mw // 15, 1)
    for dx in range(mw // hair_w):
        cv2.line(image, (mx + hair_w * dx, my), (mx + hair_w * (dx + 1), my + mh), (0, 0, 0), 1)
        cv2.line(image, (mx + hair_w * dx, my + mh), (mx + hair_w * (dx + 1), my), (0, 0, 0), 1)


def viewImage(image, name_of_window):
    cv2.namedWindow(name_of_window, cv2.WINDOW_NORMAL)
    cv2.imshow(name_of_window, image)
    cv2.waitKey(0)
    cv2.destroyAllWindows()


database = peewee.SqliteDatabase('Mustached.db')


class Mustached(peewee.Model):
    name = peewee.CharField()

    class Meta:
        database = database


Mustached.create_table()


downloaded_files = []
for tag in all_images:
    url = tag['src']
    if url and ('png' or 'jpg' or 'svg') in url:
        filename = url.split('/')[-1]
        filename = f'photos/{filename}'
        downloaded_files.append(filename)
        with open(filename, 'wb') as photos:
            photos.write(requests.get(url).content)

#
#
for image_path in downloaded_files:
    face_cascade = cv2.CascadeClassifier('haarcascade_frontalface_default.xml')
    image = cv2.imread(image_path)

    try:
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    except cv2.error:
        # print('FAIL', image_path)
        continue

    faces = face_cascade.detectMultiScale(
        gray,
        scaleFactor=1.1,
        minNeighbors=5,
        minSize=(10, 10)
    )
    if len(faces):
        print(image_path)

        for (x, y, w, h) in faces:
            draw_mustache(image, x, y, w, h)
        path = image_path.replace('photos', 'photos_result')
        # viewImage(image, image_path)
        cv2.imwrite(path, image)

        Mustached.create(name=path)


print(list(Mustached.select()))


