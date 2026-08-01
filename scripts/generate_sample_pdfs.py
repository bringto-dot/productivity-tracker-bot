"""One-off generator for the demo PDF guides in sample_guides/.

Run manually with: python scripts/generate_sample_pdfs.py
Requires reportlab (pip install reportlab) and a Cyrillic-capable TTF font
(uses Windows' bundled Arial by default).
"""

from pathlib import Path

from reportlab.lib.colors import HexColor
from reportlab.lib.enums import TA_LEFT
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import cm
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import ListFlowable, ListItem, Paragraph, SimpleDocTemplate, Spacer

OUT_DIR = Path(__file__).resolve().parent.parent / "sample_guides"
FONT_DIR = Path(r"C:\Windows\Fonts")

pdfmetrics.registerFont(TTFont("Body", str(FONT_DIR / "arial.ttf")))
pdfmetrics.registerFont(TTFont("Body-Bold", str(FONT_DIR / "arialbd.ttf")))
pdfmetrics.registerFont(TTFont("Body-Italic", str(FONT_DIR / "ariali.ttf")))

ACCENT = HexColor("#3B82F6")
TEXT = HexColor("#1F2933")

styles = getSampleStyleSheet()
title_style = ParagraphStyle(
    "TitleRu", parent=styles["Title"], fontName="Body-Bold", textColor=ACCENT, fontSize=22, spaceAfter=6
)
subtitle_style = ParagraphStyle(
    "SubtitleRu", parent=styles["Normal"], fontName="Body-Italic", textColor=TEXT, fontSize=11, spaceAfter=18
)
h2_style = ParagraphStyle(
    "H2Ru", parent=styles["Heading2"], fontName="Body-Bold", textColor=ACCENT, fontSize=14, spaceBefore=14, spaceAfter=6
)
body_style = ParagraphStyle(
    "BodyRu", parent=styles["Normal"], fontName="Body", textColor=TEXT, fontSize=10.5, leading=15, alignment=TA_LEFT
)
bullet_style = ParagraphStyle("BulletRu", parent=body_style, spaceAfter=4)


def build_pdf(filename: str, title: str, subtitle: str, sections: list[tuple[str, list[str]]]) -> None:
    OUT_DIR.mkdir(exist_ok=True)
    doc = SimpleDocTemplate(
        str(OUT_DIR / filename),
        pagesize=A4,
        leftMargin=2.2 * cm,
        rightMargin=2.2 * cm,
        topMargin=2 * cm,
        bottomMargin=2 * cm,
        title=title,
    )

    story = [Paragraph(title, title_style), Paragraph(subtitle, subtitle_style)]
    for heading, paragraphs in sections:
        story.append(Paragraph(heading, h2_style))
        items = []
        for p in paragraphs:
            if p.startswith("• "):
                items.append(ListItem(Paragraph(p[2:], bullet_style), leftIndent=10))
            else:
                if items:
                    story.append(ListFlowable(items, bulletType="bullet", start="•"))
                    items = []
                story.append(Paragraph(p, body_style))
                story.append(Spacer(1, 4))
        if items:
            story.append(ListFlowable(items, bulletType="bullet", start="•"))

    doc.build(story)
    print(f"Created {OUT_DIR / filename}")


def main() -> None:
    build_pdf(
        "time_management_guide.pdf",
        "5 техник тайм-менеджмента",
        "Гайд по продуктивности · Productivity Tracker Bot",
        [
            (
                "1. Метод Помодоро",
                [
                    "Работайте 25 минут без отвлечений, затем делайте перерыв на 5 минут. "
                    "После четырёх «помодоро» — длинный перерыв на 15–30 минут.",
                    "• Уберите телефон из зоны видимости на время рабочего интервала",
                    "• Записывайте, что отвлекло вас, а не переключайтесь сразу",
                    "• Не продлевайте интервал — короткие циклы держат фокус острее",
                ],
            ),
            (
                "2. Матрица Эйзенхауэра",
                [
                    "Разделите задачи на 4 квадранта по срочности и важности:",
                    "• Срочно и важно — делайте сразу",
                    "• Важно, но не срочно — планируйте время в календаре",
                    "• Срочно, но не важно — делегируйте",
                    "• Не срочно и не важно — удаляйте из списка без сожалений",
                ],
            ),
            (
                "3. Правило двух минут",
                [
                    "Если задача занимает меньше двух минут — сделайте её сразу, не откладывая "
                    "в список дел. Это освобождает голову от мелких «хвостов», которые незаметно "
                    "съедают концентрацию в течение дня.",
                ],
            ),
            (
                "4. Тайм-блокинг",
                [
                    "Заранее распределяйте весь день по блокам в календаре — включая встречи, "
                    "глубокую работу и даже отдых. Задача без выделенного времени почти всегда "
                    "проигрывает задаче, у которой есть слот в расписании.",
                ],
            ),
            (
                "5. «Съешьте лягушку»",
                [
                    "Начинайте день с самой неприятной и важной задачи — «лягушки». Как только "
                    "она сделана, остаток дня ощущается легче, а мотивация растёт вместо того, "
                    "чтобы падать к вечеру.",
                ],
            ),
            (
                "Как это связано с чек-ином в боте",
                [
                    "Попробуйте одну технику в течение недели и отмечайте свою продуктивность "
                    "каждый день во вкладке «✅ Чек-ин». Так вы увидите на графике статистики, "
                    "какой метод реально сработал именно для вас.",
                ],
            ),
        ],
    )

    build_pdf(
        "morning_workout.pdf",
        "Утренняя зарядка на 15 минут",
        "Тренировка без спортзала · Productivity Tracker Bot",
        [
            (
                "Зачем нужна утренняя зарядка",
                [
                    "Короткая зарядка утром ускоряет кровообращение, будит нервную систему быстрее "
                    "кофе и заметно повышает концентрацию в первой половине дня. Никакого "
                    "оборудования не требуется — только коврик или ровный пол.",
                ],
            ),
            (
                "Разминка (3 минуты)",
                [
                    "• Вращения головой и плечами — 30 секунд",
                    "• Круговые движения руками — 30 секунд",
                    "• Наклоны корпуса вправо/влево — 30 секунд",
                    "• Лёгкий бег на месте — 1,5 минуты",
                ],
            ),
            (
                "Основной блок (10 минут, 2 круга)",
                [
                    "• Приседания — 15 повторений",
                    "• Отжимания (можно с колен) — 10 повторений",
                    "• Планка — 30 секунд",
                    "• Выпады на каждую ногу — по 10 повторений",
                    "• Скручивания на пресс — 15 повторений",
                    "Между кругами — отдых 60 секунд. Дышите ровно, не задерживайте дыхание на "
                    "усилии.",
                ],
            ),
            (
                "Заминка (2 минуты)",
                [
                    "• Растяжка задней поверхности бедра — 30 секунд на каждую ногу",
                    "• Растяжка плеч и груди — 30 секунд",
                    "• Глубокое дыхание стоя — 30 секунд",
                ],
            ),
            (
                "Совет",
                [
                    "Отмечайте день тренировки заметкой в чек-ине бота — так будет проще заметить "
                    "связь между зарядкой и вашей вечерней оценкой продуктивности.",
                ],
            ),
        ],
    )

    build_pdf(
        "habits_lecture.pdf",
        "Мини-лекция: как формируются привычки",
        "Гайд по продуктивности · Productivity Tracker Bot",
        [
            (
                "Петля привычки",
                [
                    "Любая привычка строится из трёх элементов: триггер (сигнал), рутина "
                    "(действие) и награда. Мозг запоминает не само действие, а связку "
                    "«сигнал → награда» и со временем начинает выполнять рутину автоматически, "
                    "чтобы получить награду быстрее.",
                ],
            ),
            (
                "Миф про 21 день",
                [
                    "Популярное утверждение «привычка формируется за 21 день» не подтверждается "
                    "исследованиями. По данным University College London, в среднем на "
                    "автоматизацию простого действия уходит от 18 до 254 дней — в среднем около "
                    "66 дней, и это сильно зависит от сложности действия и регулярности "
                    "повторений.",
                ],
            ),
            (
                "Метод «наслоения привычек»",
                [
                    "Привязывайте новую привычку к уже существующей: «После того как я X, я "
                    "сделаю Y». Например: «После утреннего кофе я делаю чек-ин продуктивности в "
                    "боте». Существующая привычка становится триггером для новой — не нужно "
                    "полагаться на силу воли или память.",
                ],
            ),
            (
                "Практические советы",
                [
                    "• Начинайте с действия на 2 минуты — уменьшайте порог входа",
                    "• Делайте привычку заметной: кладите вещи на видное место",
                    "• Не прерывайте цепочку дважды подряд — один пропуск не страшен, два "
                    "подряд рушат систему",
                    "• Отслеживайте прогресс — сам факт наблюдения усиливает мотивацию",
                ],
            ),
            (
                "При чём тут стрики в боте",
                [
                    "Функция «🔥 Стрик» в разделе статистики использует именно этот принцип: "
                    "визуальная цепочка последовательных дней — это наглядный трекер, который "
                    "помогает не прерывать привычку ежедневного чек-ина.",
                ],
            ),
        ],
    )


if __name__ == "__main__":
    main()
