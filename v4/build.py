#!/usr/bin/env python3
"""Собирает v4/index.html — концепт главной KronosTime по разбору заказчика (03.10.2026).

Что взято из разбора:
- шапка и подвал — текущие KronosTime, доработаны, а не переделаны;
- белый фон, премиально и спокойно, без анимации часов при наведении;
- баннер под контент-отдел в трёх вариантах (переключатель внизу страницы, ?banner=a|b|c);
- полоса фактов, «Какие часы ищете?», новинки в одну строку «цена + в корзину» (из №1),
  «Под какой случай?» (из №2), бренды вокруг знака с подпиской поверх (из №1);
- хиты продаж — новый вид: топ-10 с крупными номерами;
- магазины и журнал — пока как варианты на обсуждение.
Товары, цены и статьи — с публичных страниц kronostime.ru (только чтение). Запуск: python3 build.py
"""
import html
import json
import os
import re

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
NB = ' '


def load(name):
    return json.load(open(os.path.join(ROOT, 'assets', name), encoding='utf-8'))


P = {p['id']: p for p in load('products.json') + load('hamilton.json') + load('longines.json') + load('extra.json')}


def e(s):
    return html.escape(str(s), quote=True)


def rub(n):
    return f"{int(n):,}".replace(',', NB) + NB + '₽'


ICON = {
    'pin': '<path d="M12 21s-7-6.2-7-11.5A7 7 0 0 1 19 9.5C19 14.8 12 21 12 21z"/><circle cx="12" cy="9.5" r="2.4"/>',
    'down': '<path d="m6 9 6 6 6-6"/>',
    'search': '<circle cx="11" cy="11" r="7"/><path d="m20 20-3.6-3.6"/>',
    'compare': '<path d="M5 20v-5M10 20v-9M15 20v-6M20 20V6"/>',
    'heart': '<path d="M12 20s-7.5-4.6-9.2-9.3C1.7 7.5 3.8 4.5 7 4.5c2 0 3.4 1.1 5 2.9 1.6-1.8 3-2.9 5-2.9 3.2 0 5.3 3 4.2 6.2C19.5 15.4 12 20 12 20z"/>',
    'user': '<circle cx="12" cy="8" r="4"/><path d="M4 21c1.5-4 4.5-6 8-6s6.5 2 8 6"/>',
    'bag': '<path d="M5 8h14l-1.2 12H6.2L5 8z"/><path d="M9 8V6.5a3 3 0 0 1 6 0V8"/>',
    'menu': '<path d="M3 7h18M3 12h18M3 17h18"/>',
    'arrow': '<path d="M4 12h16M14 6l6 6-6 6"/>',
    'left': '<path d="m15 6-6 6 6 6"/>',
    'right': '<path d="m9 6 6 6-6 6"/>',
    'up': '<path d="M12 20V5M6 11l6-6 6 6"/>',
    'phone': '<path d="M5 4h4l2 5-2.5 1.5a11 11 0 0 0 5 5L15 13l5 2v4a2 2 0 0 1-2 2A16 16 0 0 1 3 6a2 2 0 0 1 2-2z"/>',
    'clock': '<circle cx="12" cy="12" r="8.5"/><path d="M12 7.5V12l3 2"/>',
    'close': '<path d="M6 6l12 12M18 6 6 18"/>',
    'tg': '<path d="M20.5 4.5 3.5 11l5.5 2 2 6 3-4 4.5 3.5z"/><path d="m9 13 8-6"/>',
    'chat': '<path d="M12 4a8 8 0 0 0-6.9 12L4 20l4.1-1.1A8 8 0 1 0 12 4z"/>',
}


def icon(name, cls='i'):
    return f'<svg class="{cls}" viewBox="0 0 24 24" aria-hidden="true" focusable="false">{ICON[name]}</svg>'


def split_name(brand, name):
    n = name
    for b in (brand, brand.split()[0]):
        if n.lower().startswith(b.lower() + ' '):
            n = n[len(b) + 1:]
            break
    n = re.sub(r'\s*\([^)]*\)\s*$', '', n)
    toks = n.split()
    ref = ''
    if toks and re.search(r'\d', toks[-1]) and re.fullmatch(r'[A-Za-zА-Яа-я0-9.\-/]+', toks[-1]):
        ref = toks.pop()
    return ' '.join(toks), ref


def discount(p):
    if p.get('old') and p['old'] > p['price']:
        return round((p['old'] - p['price']) * 100 / p['old'])
    return 0


def card(pid, tag='', cls=''):
    """Карточка товара: цена и «в корзину» в одну строку.
    Старая цена и скидка стоят мелкой строкой НАД ценой, поэтому со скидкой карточка
    не растёт и кнопка не сжимается. Без скидки строка пустая — высота та же."""
    p = P[pid]
    model, ref = split_name(p['brand'], p['name'])
    d = discount(p)
    was = f'<span class="pc__was"><s>{rub(p["old"])}</s><em>−{d}%</em></span>' if d else '<span class="pc__was" aria-hidden="true"></span>'
    tag_html = f'<span class="pc__tag">{e(tag)}</span>' if tag else ''
    title = e(p['brand']) + (f' <span>{e(model)}</span>' if model else '')
    return f'''<article class="pc {cls}">
  <a class="pc__img" href="#" data-to="карточка {e(p['name'])}">{tag_html}<img src="../{e(p['big'])}" alt="{e(p['name'])}" width="446" height="550" loading="lazy" decoding="async"></a>
  <button class="pc__fav" type="button" aria-label="В избранное: {e(p['name'])}" aria-pressed="false">{icon('heart')}</button>
  <a class="pc__name" href="#" data-to="карточка {e(p['name'])}">{title}</a>
  <span class="pc__ref">{e(ref) or NB}</span>
  <div class="pc__buy">
    <div class="pc__price">{was}<b>{rub(p['price'])}</b></div>
    <button class="pc__cart" type="button" aria-label="В корзину: {e(p['name'])}">{icon('bag')}<span>В корзину</span></button>
  </div>
</article>'''


# ---------- Шапка ----------
MEGA_CATALOG = [
    ('Для кого', ['Мужские часы', 'Женские часы']),
    ('Механизм', ['Механические', 'Кварцевые', 'Электронные']),
    ('Страна', ['Швейцарские', 'Японские', 'Российские', 'Немецкие', 'Американские', 'Австрийские', 'Итальянские']),
    ('Материал корпуса', ['Стальные', 'Золотые', 'Керамические', 'Титановые', 'Карбоновые']),
    ('Особенности', ['Противоударные', 'Водонепроницаемые', 'С бриллиантами', 'Карманные', 'Скелетоны', 'С автоподзаводом', 'С сапфировым стеклом']),
    ('Стиль', ['Классические', 'Спортивные', 'Военные', 'Ретро']),
    ('Популярные бренды', ['Tissot', 'Certina', 'Casio', 'Seiko', 'Orient', 'Rado', 'Longines', 'Hamilton', 'Mido', 'Zeppelin', 'Swatch', 'Citizen']),
]
MEGA_LUX = [
    ('Часы люкс', ['Мужские', 'Женские', 'Все часы люкс']),
    ('Популярные бренды', ['Breitling', 'Frederique Constant', 'Longines', 'Maurice Lacroix', 'Mido', 'Omega', 'Oris', 'Rado', 'Raymond Weil', 'TAG Heuer']),
]
LOGOS = [('tissot', 'Tissot'), ('casio', 'Casio'), ('longines', 'Longines'), ('orient', 'Orient'), ('rado', 'Rado'),
         ('hamilton', 'Hamilton'), ('certina', 'Certina'), ('mido', 'Mido'), ('omega', 'Omega'), ('tagheuer', 'TAG Heuer'),
         ('oris', 'Oris'), ('breitling', 'Breitling'), ('fc', 'Frederique Constant'), ('ml', 'Maurice Lacroix')]


def mega_cols(cols):
    return ''.join(f'<div class="mg__col"><p class="mg__h">{e(h)}</p><ul>' +
                   ''.join(f'<li><a href="#" data-to="раздел «{e(x)}»">{e(x)}</a></li>' for x in items) +
                   '</ul></div>' for h, items in cols)


def header():
    lux = P['87327']
    letters = ''.join(f'<a href="#" data-to="бренды на {c}">{c}</a>' for c in 'ABCDEFGHIJKLMOPQRSTUVWZ')
    logo_grid = ''.join(f'<a href="#" data-to="бренд {e(n)}"><img src="../assets/logo/{k}.png" alt="{e(n)}" loading="lazy"></a>' for k, n in LOGOS[:12])
    return f'''
<div class="tb">
  <div class="wrap tb__row">
    <button class="tb__city" type="button">{icon('pin')}Москва{icon('down')}</button>
    <nav class="tb__links" aria-label="Покупателям">
      <a href="#stores">Наши магазины</a><a href="#" data-to="рассрочка">Рассрочка</a><a href="#" data-to="гарантия">Гарантия</a><a href="#" data-to="доставка">Доставка</a><a href="#" data-to="статус заказа">Статус заказа</a>
    </nav>
    <div class="tb__right">
      <a href="#" data-to="звонок">+7 (495) 128-09-32</a><a href="#" data-to="звонок">+7 (800) 511-94-55</a>
      <a class="tb__ico" href="#" data-to="чат в MAX" aria-label="Написать в MAX">{icon('chat')}</a><a class="tb__ico" href="#" data-to="чат в Telegram" aria-label="Написать в Telegram">{icon('tg')}</a>
    </div>
  </div>
</div>
<header class="hd" id="top">
  <div class="wrap hd__row">
    <button class="hd__burger" type="button" aria-label="Меню" data-mega="m-catalog">{icon('menu')}</button>
    <a class="hd__logo" href="#" data-to="главная"><img src="../assets/site/logo.svg" alt="KronosTime" width="185" height="30"></a>
    <form class="sr" role="search" onsubmit="return false">
      <label class="sr__field"><span class="sr-only">Поиск по каталогу</span><input type="search" placeholder="Бренд, модель или артикул" autocomplete="off"><button type="submit" aria-label="Найти">{icon('search')}</button></label>
      <div class="sr__drop">
        <div><p class="sr__h">Часто ищут</p><ul class="sr__q"><li><a href="#" data-to="поиск">Tissot PRX</a></li><li><a href="#" data-to="поиск">Casio G-Shock</a></li><li><a href="#" data-to="поиск">Seiko 5 Sports</a></li><li><a href="#" data-to="поиск">Мужские механические</a></li><li><a href="#" data-to="поиск">Часы с бриллиантами</a></li></ul></div>
        <div><p class="sr__h">Бренды</p><div class="sr__brands">{''.join(f'<a href="#" data-to="бренд {e(n)}"><img src="../assets/logo/{k}.png" alt="{e(n)}" loading="lazy"></a>' for k, n in LOGOS[:8])}</div></div>
      </div>
    </form>
    <div class="hd__act">
      <a class="ha" href="#" data-to="сравнение" aria-label="Сравнение">{icon('compare')}<span class="ha__t">Сравнение</span></a>
      <a class="ha" href="#" data-to="избранное" aria-label="Избранное">{icon('heart')}<b class="ha__n" data-fav hidden>0</b><span class="ha__t">Избранное</span></a>
      <a class="ha ha--user" href="#" data-to="вход" aria-label="Войти">{icon('user')}<span class="ha__t">Войти</span></a>
      <a class="ha" href="#" data-to="корзина" aria-label="Корзина">{icon('bag')}<b class="ha__n" data-cart hidden>0</b><span class="ha__t">Корзина</span></a>
    </div>
  </div>
  <nav class="nv" aria-label="Каталог">
    <ul class="wrap nv__list">
      <li><button class="nv__a is-red" type="button" aria-expanded="false" aria-controls="m-catalog" data-mega="m-catalog">Каталог часов{icon('down')}</button></li>
      <li><button class="nv__a" type="button" aria-expanded="false" aria-controls="m-lux" data-mega="m-lux">Часы люкс{icon('down')}</button></li>
      <li><button class="nv__a" type="button" aria-expanded="false" aria-controls="m-brands" data-mega="m-brands">Бренды{icon('down')}</button></li>
      <li><a class="nv__a" href="#new">Новинки</a></li>
      <li><a class="nv__a is-red" href="#" data-to="распродажа">Распродажа</a></li>
    </ul>
    <div class="mg" id="m-catalog" hidden><div class="wrap mg__in mg__in--cat">{mega_cols(MEGA_CATALOG)}</div></div>
    <div class="mg" id="m-lux" hidden><div class="wrap mg__in mg__in--lux">{mega_cols(MEGA_LUX)}
      <a class="mg__promo" href="#" data-to="часы люкс"><img src="../{e(lux['big'])}" alt="" loading="lazy"><span><b>Longines Master Collection</b>{rub(lux['price'])}</span></a></div></div>
    <div class="mg" id="m-brands" hidden><div class="wrap mg__in mg__in--brands"><div><p class="mg__h">Бренды от A до Z</p><div class="mg__letters">{letters}</div><a class="lnk" href="#" data-to="все бренды">Все бренды{icon('arrow')}</a></div><div class="mg__logos">{logo_grid}</div></div></div>
  </nav>
</header>'''


# ---------- Баннер ----------
SLIDES = [
    # kind: split — фото справа растворяется в сплошном фоне, текст из полей инфоблока;
    #       art   — готовая картинка контент-отдела с текстом внутри (как текущие баннеры).
    dict(kind='split', tone='dark', bg='#050505', img='assets/life/16_watches-3.jpg', mob='assets/life/16_watches-3.jpg',
         kicker='Tissot', title='Gentleman Powermatic 80 Silicium', sub='Швейцарский автоподзавод с запасом хода до 80 часов', btn='Смотреть модель',
         thumb='assets/life/16_watches-3.jpg', alt='Tissot Gentleman Powermatic 80 Silicium'),
    dict(kind='art', img='v4/img/Hamilton_Ventura.jpg', mob='', title='Ventura', kicker='Hamilton',
         thumb='v4/img/Hamilton_Ventura_2.jpg', alt='Hamilton Ventura'),
    dict(kind='split', tone='light', bg='#eef0f3', img='assets/life/06_watches_3.jpg', mob='assets/life/06_watches_3.jpg',
         kicker='Certina', title='DS Action Diver', sub='Дайверские часы с калибром Powermatic 80', btn='Смотреть модель',
         thumb='assets/life/06_watches_3.jpg', alt='Certina DS Action Diver на снегу'),
    dict(kind='art', top=True, img='v4/img/Rado_Hyperchrome_Chronograph.jpg', mob='', title='HyperChrome Chronograph', kicker='Rado',
         thumb='v4/img/Rado_Hyperchrome_Chronograph_2.jpg', alt='Rado HyperChrome Chronograph'),
    dict(kind='cover', tone='dark', img='assets/life/00_Longines_header.jpg', mob='assets/life/00_Longines_header.jpg',
         kicker='Longines', title='Часы Longines', sub='Классика и спорт швейцарской марки с 1832 года', btn='Смотреть Longines',
         thumb='assets/life/00_Longines_header.jpg', alt='Три часов Longines на камнях у моря'),
]


def slide(i, s):
    first = i == 0
    load_attr = 'fetchpriority="high"' if first else 'loading="lazy"'
    mob = f'<source media="(max-width: 767px)" srcset="../{e(s["mob"])}">' if s.get('mob') else ''
    cap = ''
    if s['kind'] != 'art':
        cap = f'''<span class="bs__cap"><span class="bs__k">{e(s['kicker'])}</span><span class="bs__t">{e(s['title'])}</span><span class="bs__s">{e(s['sub'])}</span><span class="bs__btn">{e(s['btn'])}{icon('arrow')}</span></span>'''
    style = f' style="--bs-bg:{s["bg"]}"' if s.get('bg') else ''
    desk_only = ' data-desk-only' if not s.get('mob') else ''
    tone = f' bs--{s["tone"]}' if s.get('tone') else ''
    tone += ' bs--top' if s.get('top') else ''
    return f'''<a class="bs bs--{s['kind']}{tone}{' is-on' if first else ''}" href="#" data-to="{e(s['title'])}"{style}{desk_only} aria-hidden="{'false' if first else 'true'}" tabindex="{'0' if first else '-1'}">
  <picture>{mob}<img src="../{e(s['img'])}" alt="{e(s['alt'])}" {load_attr} decoding="async"></picture>{cap}
</a>'''


def banner():
    slides = ''.join(slide(i, s) for i, s in enumerate(SLIDES))
    dots = ''.join(f'<button class="bn__dot{" is-on" if i == 0 else ""}" type="button" aria-label="Баннер {i + 1}: {e(s["title"])}"{" data-desk-only" if not s.get("mob") else ""}><i></i></button>' for i, s in enumerate(SLIDES))
    agenda = ''.join(f'''<li><button class="ag{" is-on" if i == 0 else ""}" type="button" data-i="{i}"><img src="../{e(s['thumb'])}" alt="" loading="lazy"><span><small>{e(s['kicker'])}</small>{e(s['title'])}</span><i></i></button></li>''' for i, s in enumerate(SLIDES))
    side = P['80810']
    sm, sref = split_name(side['brand'], side['name'])
    d = discount(side)
    return f'''
<section class="bn" id="banner" aria-roledescription="карусель" aria-label="Баннеры">
  <div class="wrap bn__in">
    <div class="bn__stage" tabindex="-1">
      {slides}
      <button class="bn__arr bn__arr--l" type="button" aria-label="Предыдущий баннер">{icon('left')}</button>
      <button class="bn__arr bn__arr--r" type="button" aria-label="Следующий баннер">{icon('right')}</button>
      <div class="bn__dots">{dots}</div>
    </div>
    <ol class="bn__agenda" aria-label="Все баннеры">{agenda}</ol>
    <aside class="bn__side" aria-label="Хит продаж">
      <span class="bn__side-k">Хит продаж</span>
      <a class="bn__side-img" href="#" data-to="карточка {e(side['name'])}"><img src="../{e(side['big'])}" alt="{e(side['name'])}" loading="lazy"></a>
      <a class="pc__name" href="#" data-to="карточка {e(side['name'])}">{e(side['brand'])} <span>{e(sm)}</span></a>
      <span class="pc__ref">{e(sref)}</span>
      <div class="pc__buy"><div class="pc__price"><span class="pc__was"><s>{rub(side['old'])}</s><em>−{d}%</em></span><b>{rub(side['price'])}</b></div><button class="pc__cart" type="button" aria-label="В корзину: {e(side['name'])}">{icon('bag')}<span>В корзину</span></button></div>
    </aside>
  </div>
</section>'''


# ---------- Полоса фактов ----------
FACTS = [('с 2008', 'года продаём часы', 'о компании'), ('100+', 'мировых брендов', 'все бренды'),
         ('45 000+', 'моделей в каталоге', 'каталог'), ('10', 'магазинов KronosTime', 'магазины'),
         ('4,9', 'на Яндексе, 2000+ отзывов', 'отзывы')]


def facts():
    items = ''.join(f'<li><a href="#" data-to="{e(t)}"><b>{e(n)}</b><span>{e(s)}</span></a></li>' for n, s, t in FACTS)
    return f'<section class="facts" aria-label="KronosTime в цифрах"><ul class="wrap facts__list">{items}</ul></section>'


# ---------- Каталог часов: оглавление с фото при наведении ----------
INDEX = [('Мужские часы', 'Casio, Seiko, Tissot, Hamilton', '38610'),
         ('Женские часы', 'Tissot, Rado, Longines, Lincor', '81343'),
         ('Механические', 'Автоподзавод и ручной завод', '70818'),
         ('Хронографы', 'Tissot, Seiko, Longines', '45920'),
         ('Дайверские', 'Certina, Orient, Longines', '74524'),
         ('Классические', 'Longines, Rado, Михаил Москвин', '37652'),
         ('Электронные', 'Casio G-Shock, Boccia', '106276'),
         ('Часы люкс', 'Longines, Rado, Omega, TAG Heuer', '87327')]


def catalog_index():
    """Компактная полоса разделов: одна строка из 8 входов в каталог."""
    items = ''.join(f'''<li><a class="cx" href="#" data-to="раздел «{e(name)}»"><span class="cx__img"><img src="../{e(P[pid]['big'])}" alt="" loading="lazy"></span><span class="cx__t">{e(name)}</span></a></li>''' for name, note, pid in INDEX)
    return f'''
<section class="sec sec--tight cxs" aria-labelledby="cx-h">
  <div class="wrap">
    <div class="cxs__head"><h2 class="cxs__h" id="cx-h">Каталог часов</h2><a class="lnk" href="#" data-to="каталог">Весь каталог{icon('arrow')}</a></div>
    <ul class="cxs__list">{items}</ul>
  </div>
</section>'''


# ---------- Хиты продаж: полка карточек на тени, листается вбок ----------
HITS = ['80810', '72097', '105273', '90061', '106276', '45920', '87361', '106297', '38610']


def hits():
    items = ''.join(f'<li class="shelf__item rv" style="--d:{min(i, 4) * 70}ms">{card(pid, cls="pc--shelf")}</li>' for i, pid in enumerate(HITS))
    return f'''
<section class="sec hits" aria-labelledby="hits-h">
  <div class="wrap">
    <div class="sec__head rv"><div><h2 class="h2" id="hits-h">Хиты продаж</h2><p class="lede">Модели, которые чаще всего выбирают в KronosTime</p></div>
      <div class="sec__tools"><a class="lnk" href="#" data-to="все хиты продаж">Все хиты{icon('arrow')}</a>
        <button class="shelf__btn" type="button" data-shelf="-1" aria-label="Назад">{icon('left')}</button><button class="shelf__btn" type="button" data-shelf="1" aria-label="Вперёд">{icon('right')}</button></div>
    </div>
    <div class="shelf" data-shelfbox><ul class="shelf__list" aria-label="Хиты продаж">{items}</ul></div>
  </div>
</section>'''


# ---------- Под какой случай ----------
OCC = [
    ('В подарок', 'Подарок, который будут носить каждый день: от яркого G-Shock до швейцарской механики.', 'assets/life/16_watches-3.jpg', ['106276', '105273', '28296'], 2),
    ('Первые часы с механикой', 'Автоподзавод и ручной завод: часы, которые живут без батарейки.', 'assets/life/04_watches_3.jpg', ['96204', '72097', '71051'], 2),
    ('На каждый день', 'Прочный корпус, удобный браслет и водозащита — чтобы не снимать.', 'assets/life/06_watches_3.jpg', ['115690', '90061', '74524'], 2),
    ('В коллекцию', 'Сложные функции и большие марки — часы, которые передают по наследству.', 'assets/life/03_chasy_3.jpg', ['27353', '87361', '87327'], 2),
]
OCC_LEVEL = ['Недорого', 'Оптимально', 'Чтобы запомнилось']


def occasions():
    panels = []
    for k, (title, text, photo, ids, on_photo) in enumerate(OCC):
        rows = []
        for j, pid in enumerate(ids):
            p = P[pid]
            model, _ = split_name(p['brand'], p['name'])
            d = discount(p)
            was = f'<s>{rub(p["old"])}</s>' if d else ''
            mark = '<em>на фото</em>' if j == on_photo else ''
            rows.append(f'''<li><a href="#" data-to="карточка {e(p['name'])}"><img src="../{e(p['big'])}" alt="" loading="lazy"><span><small>{OCC_LEVEL[j]}{mark}</small><b>{e((p['brand'] + ' ' + model).strip())}</b><span class="oc__p">{rub(p['price'])}{was}</span></span></a></li>''')
        on = k == 0
        panels.append(f'''<li class="oc{' is-open' if on else ''}">
  <button class="oc__tab" type="button" aria-expanded="{'true' if on else 'false'}" aria-controls="oc-{k}"><img src="../{e(photo)}" alt="" loading="lazy"><span class="oc__n">0{k + 1}</span><span class="oc__t">{e(title)}</span></button>
  <div class="oc__body" id="oc-{k}">
    <div class="oc__photo"><img src="../{e(photo)}" alt="" loading="lazy"></div>
    <div class="oc__copy"><span class="oc__n">0{k + 1}</span><h3>{e(title)}</h3><p>{e(text)}</p><ul class="oc__list">{''.join(rows)}</ul>
      <a class="lnk" href="#" data-to="подборка «{e(title)}»">Смотреть все{icon('arrow')}</a></div>
  </div>
</li>''')
    return f'''
<section class="sec occ" aria-labelledby="occ-h">
  <div class="wrap">
    <div class="sec__head rv"><div><h2 class="h2" id="occ-h">Под какой случай выбираем?</h2><p class="lede">Три варианта на каждый повод. Часы на фото — те же, что в списке.</p></div></div>
    <ul class="occ__list rv">{''.join(panels)}</ul>
  </div>
</section>'''


# ---------- Новинки: светлые плитки, текст сверху, часы снизу ----------
NEW = ['1819256', '1819259', '1818901', '1818996']


def tile(pid):
    p = P[pid]
    model, ref = split_name(p['brand'], p['name'])
    return f'''<article class="nt">
  <span class="nt__k">Новинка</span>
  <a class="nt__name" href="#" data-to="карточка {e(p['name'])}">{e(p['brand'])}{(' ' + e(model)) if model else ''}</a>
  <span class="nt__ref">{e(ref)}</span>
  <span class="nt__price">{rub(p['price'])}</span>
  <div class="nt__acts"><a class="nt__more" href="#" data-to="карточка {e(p['name'])}">Подробнее</a><button class="nt__cart" type="button" data-cart-btn aria-label="В корзину: {e(p['name'])}">{icon('bag')}В корзину</button></div>
  <a class="nt__img" href="#" data-to="карточка {e(p['name'])}" tabindex="-1" aria-hidden="true"><img src="../{e(p['big'])}" alt="" loading="lazy"></a>
  <button class="pc__fav" type="button" aria-label="В избранное: {e(p['name'])}" aria-pressed="false">{icon('heart')}</button>
</article>'''


def news():
    items = ''.join(f'<li class="rv" style="--d:{i * 90}ms">{tile(pid)}</li>' for i, pid in enumerate(NEW))
    return f'''
<section class="sec new" id="new" aria-labelledby="new-h">
  <div class="wrap">
    <div class="sec__head rv"><div><h2 class="h2" id="new-h">Только что в каталоге</h2><p class="lede">Новинки этой недели — от российской классики до цифровых Boccia из титана</p></div>
      <div class="sec__tools"><a class="lnk" href="#" data-to="новинки">Все новинки{icon('arrow')}</a></div></div>
    <ul class="nt__grid">{items}</ul>
  </div>
</section>'''


# ---------- Магазины: плитки на тени ----------
STORES = [('Таганский пассаж', 'ул. Таганская, 3', '1 этаж, вход со стороны улицы Таганская', 'Открыто до 22:00'),
          ('Дубровская Слобода', '1-я улица Машиностроения, 10', '2 этаж, вход со стороны улицы', 'Открыто до 21:00')]


STORE_PHOTOS = ['assets/b/stores_mob.jpg', 'assets/site/facade.jpg']


# Магазины по городам — с публичных страниц kronostime.ru/stores/ и kazan., naberezhnye-chelny. (только чтение)
CITIES = [
    ('Москва', '+7 (495) 128-09-32', [
        ('Магазин KronosTime', 'Таганский пассаж', 'ул. Таганская, 3', '1 этаж, вход со стороны улицы Таганская', 'до 22:00'),
        ('Магазин KronosTime', 'Дубровская Слобода', '1-я улица Машиностроения, 10', '2 этаж, вход со стороны улицы', 'до 21:00')]),
    ('Казань', '+7 (843) 207-06-89', [
        ('Премиальный магазин KronosTime', 'ТЦ Мега', 'пр. Победы, 141', '1 этаж, напротив магазина MAAG', 'до 22:00'),
        ('Магазин Kronos', 'ТЦ Мега', 'пр. Победы, 141', '1 этаж, рядом с Armani Exchange', 'до 22:00'),
        ('Премиальный магазин Tissot', 'ТРЦ Парк Хаус', 'пр. Ямашева, 46/33', '1 этаж, по центральной аллее', 'до 22:00'),
        ('Магазин Kronos', 'ТРЦ Парк Хаус', 'пр. Ямашева, 46/33', '1 этаж, главный вход и направо', 'до 22:00'),
        ('Магазин Kronos', 'ТРЦ Южный', 'пр. Победы, 91', '1 этаж, центральный вход', 'до 22:00'),
        ('Магазин Casio', 'ТРЦ Тандем', 'пр. Ибрагимова, 56', '1 этаж, рядом с Лэтуалем', 'до 22:00')]),
    ('Набережные Челны', '8 (800) 511-94-55', [
        ('Премиальный магазин Casio', 'ТРЦ Омега', 'пр. Сююмбике, 2/19', '1 этаж, главный вход и налево', 'до 21:00')]),
]


def stores():
    """Вариант 2: мозаика плиток на тени — фото с текстом, два магазина, рейтинг и «10 магазинов»."""
    msk = CITIES[0][2]
    cards = ''.join(f'''<li class="rv" style="--d:{(i + 1) * 80}ms"><article class="sc">
  <span class="sc__open"><i></i>Открыто {e(h)}</span>
  <h3 class="sc__t">{e(mall)}</h3>
  <p class="sc__a">{e(ad)}<span>{e(fl)}</span></p>
  <div class="sc__acts"><a class="sc__btn" href="#" data-to="маршрут до магазина «{e(mall)}»">Маршрут</a><a class="sc__lnk" href="#" data-to="звонок">{e(CITIES[0][1])}</a></div>
</article></li>''' for i, (kind, mall, ad, fl, h) in enumerate(msk))
    return f'''
<section class="sec stores" id="stores" aria-labelledby="stores-h">
  <div class="wrap">
    <ul class="sb">
      <li class="sb__hero rv"><a class="sh" href="#" data-to="все магазины">
        <img src="../assets/b/stores_mob.jpg" alt="Магазин KronosTime" loading="lazy">
        <span class="sh__body"><span class="sh__k">Магазины KronosTime</span><span class="sh__t" id="stores-h">Посмотрите часы вживую</span><span class="sh__s">10 магазинов. Покажем модели, подберём размер браслета и отложим часы к вашему приходу.</span></span>
      </a></li>
      {cards}
      <li class="rv" style="--d:240ms"><a class="sy" href="#" data-to="отзывы на Яндексе"><span class="sy__n">4,9</span><span class="sy__stars" aria-hidden="true">★★★★★</span><span class="sy__s">2000+ отзывов на Яндексе</span><span class="sy__go">Читать отзывы{icon('arrow')}</span></a></li>
      <li class="rv" style="--d:320ms"><a class="sa" href="#" data-to="все магазины"><span class="sa__n">10</span><span class="sa__s">магазинов KronosTime</span><span class="sa__go">Все адреса{icon('arrow')}</span></a></li>
    </ul>
  </div>
</section>'''


# ---------- Журнал: главная статья крупно и три карточки на тени ----------
POST_MAIN = ('assets/life/02_chasy_0_1.jpg', 'Гиды', '30 сентября', '6 минут',
             'Как выбрать вторые часы в коллекцию: что купить после первой универсальной модели',
             'Первая модель обычно универсальная. Разбираем, чем её дополнить: дайвер, классика на ремешке или хронограф.')
POSTS = [('assets/life/03_chasy_3.jpg', 'Гиды', '29 сентября', 'Дата в часах: какую функцию выбрать и за что не стоит переплачивать'),
         ('assets/life/14_certina_3.jpg', 'Обзоры', '21 сентября', 'Certina DS Action Diver Powermatic 80: обзор швейцарского дайвера с запасом хода 80 часов'),
         ('assets/life/08_chasy_pvd_2.jpg', 'Уход за часами', '24 сентября', 'PVD-покрытие часов: мифы об износе и правила ухода')]
TOPICS = ['Гиды', 'Обзоры', 'Сравнения', 'Уход за часами']


def journal():
    img, cat, d, read, title, lead = POST_MAIN
    cards = ''.join(f'''<li class="rv" style="--d:{i * 90}ms"><a class="jc" href="#" data-to="статья журнала"><span class="jc__img"><img src="../{e(im)}" alt="" loading="lazy"></span><span class="jc__body"><span class="jc__meta"><b>{e(c)}</b>{e(dt)}</span><span class="jc__t">{e(t)}</span></span></a></li>''' for i, (im, c, dt, t) in enumerate(POSTS))
    topics = ''.join(f'<li><a href="#" data-to="журнал: {e(t)}">{e(t)}</a></li>' for t in TOPICS)
    return f'''
<section class="sec journal" aria-labelledby="journal-h">
  <div class="wrap">
    <div class="sec__head rv"><div><h2 class="h2" id="journal-h">Журнал KronosTime</h2><ul class="jt">{topics}</ul></div>
      <div class="sec__tools"><a class="lnk" href="#" data-to="журнал">Все статьи{icon('arrow')}</a></div></div>
    <a class="jf rv" href="#" data-to="статья журнала">
      <span class="jf__img"><img src="../{e(img)}" alt="" loading="lazy"></span>
      <span class="jf__body"><span class="jc__meta"><b>{e(cat)}</b>{e(d)} · {e(read)}</span><span class="jf__t">{e(title)}</span><span class="jf__lead">{e(lead)}</span><span class="jf__go">Читать{icon('arrow')}</span></span>
    </a>
    <ul class="jc__grid">{cards}</ul>
  </div>
</section>'''


# ---------- Бренды вокруг знака + подписка ----------
SUN_OUT = [('tissot', 'Tissot'), ('longines', 'Longines'), ('rado', 'Rado'), ('oris', 'Oris'), ('tagheuer', 'TAG Heuer'),
           ('omega', 'Omega'), ('breitling', 'Breitling'), ('mido', 'Mido'), ('ml', 'Maurice Lacroix'), ('fc', 'Frederique Constant')]
# Внутреннее кольцо только по бокам: середина свободна под форму подписки
SUN_IN = [(168, 'casio', 'Casio'), (150, 'certina', 'Certina'), (132, 'hamilton', 'Hamilton'),
          (48, 'orient', 'Orient'), (30, '@Seiko', 'Seiko'), (12, '@Citizen', 'Citizen')]


def sun():
    def item(a, key, name, cls):
        inner = f'<span class="sun__word">{e(name)}</span>' if key.startswith('@') else f'<img src="../assets/logo/{key}.png" alt="{e(name)}" loading="lazy">'
        return f'<li class="sun__b {cls}" style="--a:{a:.1f}deg"><a href="#" data-to="бренд {e(name)}">{inner}</a></li>'

    n = len(SUN_OUT)
    outer = ''.join(item(170 - 160 * k / (n - 1), key, name, 'sun__b--o') for k, (key, name) in enumerate(SUN_OUT))
    inner = ''.join(item(a, key, name, 'sun__b--i') for a, key, name in SUN_IN)
    return f'''
<section class="sun" aria-labelledby="sun-h">
  <div class="wrap">
    <div class="sun__stage rv">
      <svg class="sun__arcs" viewBox="0 0 1000 500" preserveAspectRatio="none" aria-hidden="true"><path d="M30 500 A470 470 0 0 1 970 500"/><path d="M120 500 A380 380 0 0 1 880 500"/></svg>
      <ul class="sun__brands" aria-label="Популярные бренды">{outer}{inner}</ul>
      <div class="sun__core">
        <p class="sun__k">100+ брендов вокруг одного знака</p>
        <h2 class="sun__h" id="sun-h">Подпишитесь на новости и специальные предложения</h2>
        <p class="sun__sub">Новинки, акции и подборки часов</p>
        <form class="sub" novalidate>
          <div class="sub__row"><label class="sr-only" for="sub-mail">E-mail</label><input id="sub-mail" type="email" placeholder="Введите ваш e-mail" required><button class="btn" type="submit">Подписаться</button></div>
          <label class="chk"><input type="checkbox" required><span>Соглашаюсь с <a href="#" data-to="обработка персональных данных">обработкой персональных данных</a></span></label>
          <label class="chk"><input type="checkbox"><span>Соглашаюсь с <a href="#" data-to="рекламная рассылка">рекламной рассылкой</a></span></label>
        </form>
      </div>
      <span class="sun__disc" aria-hidden="true"><img src="../assets/site/mark.svg" alt=""></span>
    </div>
  </div>
</section>'''


# ---------- Подвал (текущий KronosTime, доработан) ----------
def footer():
    def col(h, links):
        return f'<div class="ft__col"><p class="ft__h">{e(h)}</p><ul>' + ''.join(f'<li><a href="#" data-to="{e(x)}">{e(x)}</a></li>' for x in links) + '</ul></div>'
    pays = ''.join(f'<img src="../assets/site/{k}.png" alt="{e(n)}" loading="lazy">' for k, n in [('mir', 'Мир'), ('mastercard', 'Mastercard')]) + \
        '<span class="pay-visa" aria-label="Visa">VISA</span>' + \
        ''.join(f'<img src="../assets/site/{k}.png" alt="{e(n)}" loading="lazy">' for k, n in [('sbp', 'СБП'), ('tbank', 'Т-Банк'), ('ysplit', 'Сплит'), ('dolyame', 'Долями')])
    soc = lambda items: ''.join(f'<a href="#" data-to="{e(n)}" aria-label="{e(n)}"><img src="../assets/site/{k}.png" alt="" loading="lazy"></a>' for k, n in items)
    return f'''
<footer class="ft">
  <div class="wrap ft__cols">
    {col('Помощь', ['Доставка и оплата', 'Обмен и возврат', 'Гарантия', 'Статус заказа', 'Вопросы и ответы'])}
    {col('Покупателям', ['Программа лояльности', 'Нашли дешевле', 'Рассрочка', 'Сервисный центр'])}
    {col('Компания', ['О компании', 'Наши магазины', 'Политика', 'Вакансии', 'Франшиза'])}
    <div class="ft__col"><p class="ft__h">Свяжитесь с нами</p><ul>
      <li><a class="ft__tel" href="#" data-to="звонок">{icon('phone')}+7 (495) 128-09-32</a></li>
      <li><a class="ft__tel" href="#" data-to="звонок">{icon('phone')}+7 (800) 511-94-55</a></li>
      <li><a href="#" data-to="контакты">Контакты</a></li><li><a href="#" data-to="обратный звонок">Заказать звонок</a></li></ul></div>
    <div class="ft__col ft__col--soc">
      <p class="ft__h">Напишите нам</p><p class="ft__note">Выберите удобный способ связи</p><div class="ft__soc">{soc([('max', 'MAX'), ('telegram', 'Telegram'), ('whasapp', 'WhatsApp')])}</div>
      <p class="ft__h">Мы в социальных сетях</p><p class="ft__note">Новости, обзоры и подборки часов</p><div class="ft__soc">{soc([('vk', 'ВКонтакте'), ('youtube', 'YouTube'), ('dzen', 'Дзен')])}</div>
    </div>
  </div>
  <div class="wrap ft__pay">
    <span class="ft__pay-h">Мы принимаем к оплате</span><div class="ft__pays">{pays}</div>
    <a class="ya ya--ft" href="#" data-to="отзывы на Яндексе"><span class="ya__logo">Я</span><span class="ya__name">Яндекс</span><span>★★★★★ <b>4,9</b></span><small>2000+ отзывов</small></a>
  </div>
  <div class="ft__bottom">
    <div class="wrap ft__bottom-in">
      <a class="ft__logo" href="#top"><img src="../assets/site/logo.svg" alt="KronosTime" width="185" height="30"><span>Твой стиль. Твоё время</span></a>
      <div class="ft__legal"><p>© 2008–2026 KronosTime <i>•</i> <a href="#" data-to="пользовательское соглашение">Пользовательское соглашение</a> <i>•</i> <a href="#" data-to="политика конфиденциальности">Политика конфиденциальности</a></p><p>Информация на сайте не является публичной офертой</p></div>
      <a class="ft__up" href="#top" aria-label="Наверх">{icon('up')}</a>
    </div>
  </div>
</footer>'''


def main():
    page = f'''<!doctype html>
<html lang="ru">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>KronosTime — концепт главной, версия 4</title>
<meta name="robots" content="noindex, nofollow">
<link rel="icon" href="../assets/site/mark.svg">
<link rel="preload" href="../fonts/Montserrat-Medium.woff2" as="font" type="font/woff2" crossorigin>
<link rel="preload" href="../fonts/Montserrat-SemiBold.woff2" as="font" type="font/woff2" crossorigin>
<link rel="stylesheet" href="style.css">
</head>
<body data-banner="a" data-bsize="m">
<a class="skip" href="#main">К содержимому</a>
{header()}
<main id="main">
{banner()}
{facts()}
{catalog_index()}
{hits()}

{news()}
{stores()}
{journal()}
{sun()}
</main>
{footer()}
<div class="cb" role="region" aria-label="Панель концепта">
  <span class="cb__dot"></span><span class="cb__t">Концепт v4</span>
  <span class="cb__g" role="group" aria-label="Вариант баннера">Баннер:
    <button type="button" data-variant="a" aria-pressed="true" title="Широкий, как у Bestwatch">A</button><button type="button" data-variant="b" aria-pressed="false" title="Широкий со списком баннеров">B</button><button type="button" data-variant="c" aria-pressed="false" title="Баннер и хит продаж, как сейчас">C</button></span>
  <span class="cb__g" role="group" aria-label="Высота баннера">Высота:
    <button type="button" data-bsize="s" aria-pressed="false" title="Низкий, 3,6 : 1">S</button><button type="button" data-bsize="m" aria-pressed="true" title="Средний, 3,2 : 1">M</button><button type="button" data-bsize="l" aria-pressed="false" title="Высокий, 2,4 : 1 — был раньше">L</button></span>
  <a class="cb__l" href="../arena/" data-real>арена</a>
  <button class="cb__x" type="button" aria-label="Скрыть панель">{icon('close')}</button>
</div>
<div class="toast" role="status" aria-live="polite"></div>
<script src="app.js"></script>
</body>
</html>
'''

    def tidy(text):
        text = re.sub(r'(?<=\s)(в|и|с|к|у|о|а|от|до|на|по|за|из|не|что|как) ', lambda m: m.group(1) + NB, text)
        return text
    page = re.sub(r'>([^<]+)<', lambda m: '>' + tidy(m.group(1)) + '<', page)
    with open(os.path.join(HERE, 'index.html'), 'w', encoding='utf-8') as f:
        f.write(page)
    print('v4/index.html собран:', len(page), 'символов')


if __name__ == '__main__':
    main()
