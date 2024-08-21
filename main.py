from PIL import Image, ImageFilter, ImageDraw
from aiogram import Bot, Dispatcher, executor, types
from aiogram.dispatcher import FSMContext
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton


token = '6175272668:AAELMoqliC3AsLAk6N-8rA3zVMx17tKhiGs'
bot = Bot(token)
dp = Dispatcher(bot=bot)

btnBlur = KeyboardButton('Blur')
btnContour = KeyboardButton('Contour')
btnDetail = KeyboardButton('Detail')
btnEmboss = KeyboardButton('Emboss')
btnBaW = KeyboardButton('Black and white')
btnGPH = KeyboardButton('Gradient pride horizontal')
btnGPV = KeyboardButton('Gradient pride vertical')
btnGPD = KeyboardButton('Gradient pride diagonal')
btnGTPH = KeyboardButton('Gradient trans-pride horizontal')
btnGTPV = KeyboardButton('Gradient trans-pride vertical')
btnGTPD = KeyboardButton('Gradient trans-pride diagonal')
btnRtt = KeyboardButton('Rotate')
btnReset = KeyboardButton('Reset')

mainMenu = ReplyKeyboardMarkup().add(btnBlur, btnContour, btnDetail, btnEmboss, btnBaW, btnGPH, btnGPV, btnGPD, btnGTPH,
                                     btnGTPV, btnGTPD, btnRtt, btnReset)


@dp.message_handler(commands=['start'])
async def botStart(message: types.Message):
    await message.answer('Бот для редактирования фотографий готов к работе.', reply_markup=mainMenu)


@dp.message_handler(content_types=['photo'])
async def getPhoto(message: types.Message):
    await message.photo[-1].download(f'img.png')
    getCopy()
    await message.answer('Фотография успешно загружена')


def draw_gradient(im, *colours, direction="diagonal"):
    def _interpolate(start, end):
        diffs = [(t - f) / lines for f, t in zip(start, end)]
        for i in range(lines):
            yield [round(value + (diff * i)) for value, diff in zip(start, diffs)]

    draw = ImageDraw.Draw(im)

    if direction == "horizontal":
        lines = im.width // (len(colours) - 1)
    elif direction == "vertical":
        lines = im.height // (len(colours) - 1)
    else:
        lines = (im.width * 2) // len(colours)

    line_number = 0

    for i in range(len(colours) - 1):
        for colour in _interpolate(colours[i], colours[i + 1]):
            if direction == "horizontal":
                draw.line([(line_number, 0), (line_number, im.height)], tuple(colour), width=1)
            elif direction == "vertical":
                draw.line([(0, line_number), (im.width, line_number)], tuple(colour), width=1)
            else:
                draw.line([(line_number, 0), (0, line_number)], tuple(colour), width=1)

            line_number += 1

    return im


def pride(im, direction="diagonal"):
    grad = Image.new("RGBA", im.size, color=(0, 0, 0, 0))
    colours = (
        (240, 1, 0),
        (255, 128, 0),
        (255, 255, 0),
        (0, 121, 64),
        (64, 65, 255),
        (161, 0, 193),
    )
    grad = draw_gradient(grad, *colours, direction=direction)
    grad.putalpha(127)
    return Image.alpha_composite(im, grad)


def trans_pride(im, direction="diagonal"):
    grad = Image.new("RGBA", im.size, color=(0, 0, 0, 0))
    colours = (
        (91, 206, 251),
        (245, 168, 184),
        (255, 255, 255),
        (245, 168, 184),
        (91, 206, 251),
    )
    grad = draw_gradient(grad, *colours, direction=direction)
    grad.putalpha(127)
    return Image.alpha_composite(im, grad)


def getCopy():
    imgCopy = Image.open(f'img.png')
    imgCopy.save(f'imgCopy.png')


def gradient(type: str, direction: str, imgCopy):
    imgCopy = imgCopy.convert("RGBA")
    if type == 'pride':
        pride_im = pride(imgCopy, direction=direction)
        imgCopy = pride_im
    elif type == 'trans':
        trans_im = trans_pride(imgCopy, direction=direction)
        imgCopy = trans_im
    return imgCopy


async def sendPhoto(id):
    await bot.send_photo(id, photo=open(f'imgCopy.png', 'rb'))


async def routine(id, imgCopy):
    imgCopy.save(f'imgCopy.png')
    await sendPhoto(id)


@dp.message_handler()
async def bot_message(message: types.Message, state=FSMContext):
    try:
        imgCopy = Image.open('imgCopy.png')
        if message.text == 'Blur':
            imgCopy = imgCopy.filter(ImageFilter.BLUR)
            await routine(message.from_user.id, imgCopy)
        elif message.text == 'Contour':
            imgCopy = imgCopy.filter(ImageFilter.CONTOUR)
            await routine(message.from_user.id, imgCopy)
        elif message.text == 'Detail':
            imgCopy = imgCopy.filter(ImageFilter.DETAIL)
            await routine(message.from_user.id, imgCopy)
        elif message.text == 'Emboss':
            imgCopy = imgCopy.filter(ImageFilter.EMBOSS)
            await routine(message.from_user.id, imgCopy)
        elif message.text == 'Black and white':
            imgCopy = imgCopy.convert('1')
            await routine(message.from_user.id, imgCopy)
        elif message.text == 'Gradient pride horizontal':
            imgCopy = gradient('pride', 'horizontal', imgCopy)
            await routine(message.from_user.id, imgCopy)
        elif message.text == 'Gradient pride vertical':
            imgCopy = gradient('pride', 'vertical', imgCopy)
            await routine(message.from_user.id, imgCopy)
        elif message.text == 'Gradient pride diagonal':
            imgCopy = gradient('pride', 'diagonal', imgCopy)
            await routine(message.from_user.id, imgCopy)
        elif message.text == 'Gradient trans-pride horizontal':
            imgCopy = gradient('trans', 'horizontal', imgCopy)
            await routine(message.from_user.id, imgCopy)
        elif message.text == 'Gradient trans-pride vertical':
            imgCopy = gradient('trans', 'vertical', imgCopy)
            await routine(message.from_user.id, imgCopy)
        elif message.text == 'Gradient trans-pride diagonal':
            imgCopy = gradient('trans', 'diagonal', imgCopy)
            await routine(message.from_user.id, imgCopy)
        elif message.text == 'Rotate':
            imgCopy = imgCopy.rotate(90)
            await routine(message.from_user.id, imgCopy)
        elif message.text == 'Reset':
            getCopy()
            await sendPhoto(message.from_user.id)
    except:
        await message.answer('Произошла ошибка', reply_markup=mainMenu)


if __name__ == '__main__':
    executor.start_polling(dp)
