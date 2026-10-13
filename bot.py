import json
import os
from datetime import datetime

from telegram import (
    Update,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    ReplyKeyboardMarkup,
    KeyboardButton,
    ReplyKeyboardRemove,
)
from telegram.ext import (
    Application,
    CommandHandler,
    CallbackQueryHandler,
    MessageHandler,
    ContextTypes,
    filters,
)

# ================= SOZLAMALAR =================

TOKEN = "8786009673:AAEwVIIEIHRXHXnEI7L-XdPA6QHRaVnHXDo"
ADMIN_IDS = [5538156384]

FREE_DELIVERY_FROM = 120000
DELIVERY_PRICE = 15000

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
PRODUCTS_FILE = os.path.join(BASE_DIR, "products.json")
ORDERS_FILE = os.path.join(BASE_DIR, "orders.json")
USERS_FILE = os.path.join(BASE_DIR, "users.json")

CATEGORIES = {
    "burger": "🍔 Burgerlar",
    "hotdog": "🌭 Hot-doglar",
    "koralevskiy": "🌭 Koralevskiy",
    "hotlet": "🌭 Hotletlar",
    "shashdog": "🍢 Shash-doglar",
    "lavash": "🌯 Lavashlar",
    "shaurma": "🌯 Shaurma",
}

INITIAL_PRODUCTS = {
    "gam": {"name": "Gam Burger", "price": 30000, "category": "burger"},
    "dubl": {"name": "Duble Burger", "price": 35000, "category": "burger"},
    "big": {"name": "Big Burger", "price": 40000, "category": "burger"},
    "best": {"name": "Best Burger", "price": 45000, "category": "burger"},
    "max": {"name": "Big Max Burger", "price": 60000, "category": "burger"},

    "odd": {"name": "Oddiy", "price": 12000, "category": "hotdog"},
    "odd2": {"name": "Oddiy 2X", "price": 14000, "category": "hotdog"},
    "sirli": {"name": "Sirli 2X", "price": 15000, "category": "hotdog"},
    "nonli": {"name": "Nonli", "price": 17000, "category": "hotdog"},
    "goshtli": {"name": "Go'shtli", "price": 23000, "category": "hotdog"},

    "kor30x2": {"name": "Koralevskiy 30sm 2X", "price": 15000, "category": "koralevskiy"},
    "kor30x3": {"name": "Koralevskiy 30sm 3X", "price": 18000, "category": "koralevskiy"},
    "kor40x3": {"name": "Koralevskiy 40sm 3X", "price": 20000, "category": "koralevskiy"},
    "kor40x4": {"name": "Koralevskiy 40sm 4X", "price": 23000, "category": "koralevskiy"},
    "kor40x5": {"name": "Koralevskiy 40sm 5X", "price": 25000, "category": "koralevskiy"},

    "h25x2": {"name": "Hotlet 25sm 2X", "price": 22000, "category": "hotlet"},
    "h25x3": {"name": "Hotlet 25sm 3X", "price": 28000, "category": "hotlet"},
    "h30x2": {"name": "Hotlet 30sm 2X", "price": 25000, "category": "hotlet"},
    "h30x3": {"name": "Hotlet 30sm 3X", "price": 32000, "category": "hotlet"},
    "h30x4": {"name": "Hotlet 30sm 4X", "price": 38000, "category": "hotlet"},
    "h40x3": {"name": "Hotlet 40sm 3X", "price": 35000, "category": "hotlet"},
    "h40x4": {"name": "Hotlet 40sm 4X", "price": 42000, "category": "hotlet"},
    "h40x5": {"name": "Hotlet 40sm 5X", "price": 50000, "category": "hotlet"},

    "sd25x1": {"name": "Shash-Dog 25sm 1X", "price": 20000, "category": "shashdog"},
    "sd25x2": {"name": "Shash-Dog 25sm 2X", "price": 25000, "category": "shashdog"},
    "sd30x1": {"name": "Shash-Dog 30sm 1X", "price": 25000, "category": "shashdog"},
    "sd30x2": {"name": "Shash-Dog 30sm 2X", "price": 32000, "category": "shashdog"},
    "sd30x3": {"name": "Shash-Dog 30sm 3X", "price": 38000, "category": "shashdog"},
    "sd40x2": {"name": "Shash-Dog 40sm 2X", "price": 42000, "category": "shashdog"},
    "sd40x3": {"name": "Shash-Dog 40sm 3X", "price": 45000, "category": "shashdog"},
    "sd40x4": {"name": "Shash-Dog 40sm 4X", "price": 50000, "category": "shashdog"},

    "lmini": {"name": "Mini", "price": 28000, "category": "lavash"},
    "lodd": {"name": "Oddiy", "price": 33000, "category": "lavash"},
    "lextra": {"name": "Extra", "price": 38000, "category": "lavash"},
    "lbig": {"name": "Big", "price": 43000, "category": "lavash"},
    "lbest": {"name": "Best", "price": 48000, "category": "lavash"},

    "smini": {"name": "Mini", "price": 30000, "category": "shaurma"},
    "sodd": {"name": "Oddiy", "price": 33000, "category": "shaurma"},
    "sbig": {"name": "Big", "price": 35000, "category": "shaurma"},
}


# ================= JSON =================

def load_json(path, default):
    if not os.path.exists(path):
        return default
    try:
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    except (json.JSONDecodeError, OSError):
        return default


def save_json(path, data):
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


PRODUCTS = load_json(PRODUCTS_FILE, INITIAL_PRODUCTS.copy())
ORDERS = load_json(ORDERS_FILE, {})
USERS = load_json(USERS_FILE, {})

save_json(PRODUCTS_FILE, PRODUCTS)


# ================= YORDAMCHI FUNKSIYALAR =================

def is_admin(user_id):
    return user_id in ADMIN_IDS


def money(amount):
    return f"{int(amount):,}".replace(",", " ") + " so'm"


def register_user(user):
    USERS[str(user.id)] = {
        "id": user.id,
        "name": user.full_name,
        "username": user.username or "",
    }
    save_json(USERS_FILE, USERS)


def get_cart(context):
    return context.user_data.setdefault("cart", {})


def cart_count(context):
    return sum(get_cart(context).values())


def cart_total(context):
    total = 0
    for product_id, qty in get_cart(context).items():
        product = PRODUCTS.get(product_id)
        if product:
            total += int(product["price"]) * qty
    return total


# ================= ASOSIY KLAVIATURA =================

def main_keyboard(user_id, context):
    rows = [
        [
            KeyboardButton("🍔 Menyu"),
            KeyboardButton(f"🛒 Savatcha ({cart_count(context)})"),
        ],
        [
            KeyboardButton("📦 Buyurtmalarim"),
            KeyboardButton("📍 Filiallar"),
        ],
        [KeyboardButton("📞 Aloqa")],
    ]
    if is_admin(user_id):
        rows.append([KeyboardButton("🔐 Admin panel")])
    return ReplyKeyboardMarkup(rows, resize_keyboard=True)


# ================= ADMIN KLAVIATURA =================

def admin_keyboard():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("📦 Buyurtmalar", callback_data="admin_orders")],
        [
            InlineKeyboardButton("🛍 Mahsulotlar", callback_data="admin_products"),
            InlineKeyboardButton("➕ Qo'shish", callback_data="admin_add"),
        ],
        [
            InlineKeyboardButton("✏️ Tahrirlash", callback_data="admin_edit"),
            InlineKeyboardButton("🗑 O'chirish", callback_data="admin_delete"),
        ],
        [
            InlineKeyboardButton("👥 Foydalanuvchilar", callback_data="admin_users"),
            InlineKeyboardButton("📊 Statistika", callback_data="admin_stats"),
        ],
    ])


# ================= MENYU =================

def category_keyboard(context):
    rows = []
    for key, title in CATEGORIES.items():
        rows.append([InlineKeyboardButton(title, callback_data=f"cat:{key}")])
    rows.append([
        InlineKeyboardButton(f"🛒 Savatcha ({cart_count(context)})", callback_data="cart")
    ])
    return InlineKeyboardMarkup(rows)


def product_keyboard(category, context):
    rows = []
    for product_id, product in PRODUCTS.items():
        if product["category"] != category:
            continue
        label = f'{product["name"]} — {money(product["price"])}'
        rows.append([InlineKeyboardButton(label, callback_data=f"add:{product_id}")])
    rows.append([
        InlineKeyboardButton("⬅️ Kategoriyalar", callback_data="menu"),
        InlineKeyboardButton(f"🛒 Savat ({cart_count(context)})", callback_data="cart"),
    ])
    return InlineKeyboardMarkup(rows)


# ================= START =================

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    register_user(user)
    context.user_data.pop("admin_action", None)
    await update.message.reply_text(
        f"🍔 Assalomu alaykum, {user.first_name}!\n\n"
        "Big Burgers botiga xush kelibsiz!",
        reply_markup=main_keyboard(user.id, context),
    )


async def show_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.callback_query:
        query = update.callback_query
        await query.answer()
        await query.edit_message_text(
            "🍔 Menyudan kategoriyani tanlang:",
            reply_markup=category_keyboard(context),
        )
    else:
        await update.message.reply_text(
            "🍔 Menyudan kategoriyani tanlang:",
            reply_markup=category_keyboard(context),
        )


# ================= CALLBACK =================

async def callbacks(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    data = query.data
    user_id = query.from_user.id
    await query.answer()

    if data == "noop":
        return

    # MENU
    if data == "menu":
        await query.edit_message_text(
            "🍔 Menyudan kategoriyani tanlang:",
            reply_markup=category_keyboard(context),
        )
        return

    # CATEGORY
    if data.startswith("cat:"):
        category = data.split(":", 1)[1]
        await query.edit_message_text(
            f"{CATEGORIES.get(category, 'Menyu')}\n\nMahsulotni tanlang:",
            reply_markup=product_keyboard(category, context),
        )
        return

    # ADD PRODUCT
    if data.startswith("add:"):
        product_id = data.split(":", 1)[1]
        if product_id not in PRODUCTS:
            await query.answer("Mahsulot topilmadi.", show_alert=True)
            return
        cart = get_cart(context)
        cart[product_id] = cart.get(product_id, 0) + 1
        category = PRODUCTS[product_id]["category"]
        await query.edit_message_reply_markup(
            reply_markup=product_keyboard(category, context)
        )
        await query.answer("🛒 Savatga qo'shildi!")
        return

    # CART
    if data == "cart":
        await show_cart_query(query, context)
        return

    # QUANTITY
    if data.startswith("qty:"):
        _, product_id, change = data.split(":")
        cart = get_cart(context)
        cart[product_id] = cart.get(product_id, 0) + int(change)
        if cart[product_id] <= 0:
            cart.pop(product_id, None)
        await show_cart_query(query, context)
        return

    # CHECKOUT
    if data == "checkout":
        if not get_cart(context):
            await query.edit_message_text("🛒 Savatingiz bo'sh.")
            return
        context.user_data["checkout_step"] = "phone"
        contact_keyboard = ReplyKeyboardMarkup(
            [[KeyboardButton("📱 Telefon raqamni yuborish", request_contact=True)]],
            resize_keyboard=True,
            one_time_keyboard=True,
        )
        await query.message.reply_text(
            "📞 Telefon raqamingizni tugma orqali yuboring yoki raqamingizni yozing.",
            reply_markup=contact_keyboard,
        )
        return

    # ADMIN
    if (
        data.startswith("admin_")
        or data.startswith("ord:")
        or data.startswith("prod:")
    ):
        if not is_admin(user_id):
            await query.answer("Sizda admin huquqi yo'q.", show_alert=True)
            return
        await admin_callbacks(update, context)
        return


# ================= SAVATCHA =================

async def show_cart_query(query, context):
    cart = get_cart(context)
    if not cart:
        await query.edit_message_text(
            "🛒 Savatingiz hozircha bo'sh.",
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("🍔 Menyu", callback_data="menu")]
            ]),
        )
        return

    lines = ["🛒 SAVATCHA\n"]
    rows = []

    for product_id, qty in cart.items():
        product = PRODUCTS.get(product_id)
        if not product:
            continue
        subtotal = int(product["price"]) * qty
        lines.append(f'🍔 {product["name"]} × {qty} — {money(subtotal)}')
        rows.append([
            InlineKeyboardButton("➖", callback_data=f"qty:{product_id}:-1"),
            InlineKeyboardButton(f'{product["name"]} × {qty}', callback_data="noop"),
            InlineKeyboardButton("➕", callback_data=f"qty:{product_id}:1"),
        ])

    food_total = cart_total(context)
    delivery = 0 if food_total >= FREE_DELIVERY_FROM else DELIVERY_PRICE
    total = food_total + delivery

    lines.append(f"\n🍽 Mahsulotlar: {money(food_total)}")
    if delivery == 0:
        lines.append("🚚 Yetkazib berish: Bepul")
    else:
        lines.append(f"🚚 Yetkazib berish: {money(delivery)}")
    lines.append(f"💰 Jami: {money(total)}")

    rows.append([InlineKeyboardButton("✅ Buyurtma berish", callback_data="checkout")])
    rows.append([InlineKeyboardButton("🍔 Menyuga qaytish", callback_data="menu")])

    await query.edit_message_text(
        "\n".join(lines),
        reply_markup=InlineKeyboardMarkup(rows),
    )


# ================= TELEFON =================

async def contact_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if context.user_data.get("checkout_step") != "phone":
        return

    contact = update.message.contact
    phone = contact.phone_number if contact else update.message.text.strip()

    context.user_data["order_phone"] = phone
    context.user_data["checkout_step"] = "address"

    await update.message.reply_text(
        "📍 Yetkazib berish manzilingizni yozing:",
        reply_markup=ReplyKeyboardRemove(),
    )


# ================= TEXT HANDLER =================

async def text_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    text = (update.message.text or "").strip()
    register_user(user)

    # ADMIN ACTION
    action = context.user_data.get("admin_action")
    if action and is_admin(user.id):
        await handle_admin_text(update, context, text)
        return

    # PHONE
    if context.user_data.get("checkout_step") == "phone":
        context.user_data["order_phone"] = text
        context.user_data["checkout_step"] = "address"
        await update.message.reply_text(
            "📍 Yetkazib berish manzilingizni yozing:",
            reply_markup=ReplyKeyboardRemove(),
        )
        return

    # ADDRESS
    if context.user_data.get("checkout_step") == "address":
        if not get_cart(context):
            context.user_data.pop("checkout_step", None)
            await update.message.reply_text("Savatingiz bo'sh.")
            return

        phone = context.user_data.get("order_phone", "")
        address = text
        order_id = str(user.id)
        user_orders = ORDERS.setdefault(order_id, [])

        food_total = cart_total(context)
        delivery = 0 if food_total >= FREE_DELIVERY_FROM else DELIVERY_PRICE
        total = food_total + delivery

        items = []
        for product_id, qty in get_cart(context).items():
            product = PRODUCTS.get(product_id)
            if product:
                items.append({
                    "product_id": product_id,
                    "name": product["name"],
                    "quantity": qty,
                    "price": int(product["price"]),
                    "subtotal": int(product["price"]) * qty,
                })

        order_number = sum(len(v) for v in ORDERS.values()) + 1

        order = {
            "number": order_number,
            "user_id": user.id,
            "username": user.username or "",
            "customer": user.full_name,
            "items": items,
            "food_total": food_total,
            "delivery": delivery,
            "total": total,
            "phone": phone,
            "address": address,
            "status": "Yangi",
            "date": datetime.now().strftime("%Y-%m-%d %H:%M"),
        }

        user_orders.append(order)
        save_json(ORDERS_FILE, ORDERS)

        context.user_data["cart"] = {}
        context.user_data.pop("checkout_step", None)
        context.user_data.pop("order_phone", None)

        await update.message.reply_text(
            f"✅ Buyurtmangiz qabul qilindi!\n"
            f"🧾 Buyurtma №{order_number}\n"
            f"💰 Jami: {money(total)}\n\n"
            "Tez orada siz bilan bog'lanamiz.",
            reply_markup=main_keyboard(user.id, context),
        )

        admin_text = format_order(order)
        for admin_id in ADMIN_IDS:
            try:
                await context.bot.send_message(
                    chat_id=admin_id,
                    text=admin_text,
                    reply_markup=order_admin_keyboard(user.id, order_number),
                )
            except Exception as exc:
                print(f"Admin {admin_id} ga xabar yuborilmadi: {exc}")
        return

    # MENU
    if text == "🍔 Menyu":
        await show_menu(update, context)

    # CART
    elif text.startswith("🛒 Savatcha"):
        await update.message.reply_text(
            "Quyidagi tugma orqali savatchani oching:",
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("🛒 Savatchani ochish", callback_data="cart")]
            ]),
        )

    # ORDERS
    elif text == "📦 Buyurtmalarim":
        await show_user_orders(update, context)

    # BRANCHES
    elif text == "📍 Filiallar":
        await update.message.reply_text(
            "📍 Filiallar haqida ma'lumot olish uchun: 📞 Aloqa"
        )

    # CONTACT
    elif text == "📞 Aloqa":
        await update.message.reply_text(
            "📞 Aloqa: filial administratori bilan bog'laning."
        )

    # ADMIN PANEL
    elif text == "🔐 Admin panel" and is_admin(user.id):
        await update.message.reply_text(
            "🔐 ADMIN PANEL",
            reply_markup=admin_keyboard(),
        )


# ================= BUYURTMA FORMAT =================

def format_order(order):
    lines = [
        "🔔 YANGI BUYURTMA",
        f'🧾 Buyurtma №{order["number"]}',
        "",
        f'👤 Mijoz: {order.get("customer", "Noma\'lum")}',
        f'🆔 Telegram ID: {order.get("user_id", "")}',
        f'📱 Username: @{order.get("username") or "-"}',
        f'📞 Telefon: {order.get("phone", "-")}',
        f'📍 Manzil: {order.get("address", "-")}',
        "",
    ]
    for item in order.get("items", []):
        lines.append(
            f'🍔 {item["name"]} × {item["quantity"]} — {money(item["subtotal"])}'
        )
    lines += [
        "",
        f'🍽 Mahsulotlar: {money(order.get("food_total", 0))}',
        f'🚚 Yetkazish: {money(order.get("delivery", 0))}',
        f'💰 JAMI: {money(order.get("total", 0))}',
        f'📌 Holati: {order.get("status", "Yangi")}',
        f'🕒 Sana: {order.get("date", "-")}',
    ]
    return "\n".join(lines)


def find_order(user_id, number):
    for order in ORDERS.get(str(user_id), []):
        if int(order["number"]) == int(number):
            return order
    return None


# ================= ADMIN ORDER BUTTONS =================

def order_admin_keyboard(user_id, number):
    return InlineKeyboardMarkup([
        [
            InlineKeyboardButton(
                "✅ Qabul qilish",
                callback_data=f"ord:status:{user_id}:{number}:Qabul qilindi",
            ),
            InlineKeyboardButton(
                "👨‍🍳 Tayyorlanmoqda",
                callback_data=f"ord:status:{user_id}:{number}:Tayyorlanmoqda",
            ),
        ],
        [
            InlineKeyboardButton(
                "🛵 Yetkazilmoqda",
                callback_data=f"ord:status:{user_id}:{number}:Yetkazilmoqda",
            ),
            InlineKeyboardButton(
                "✅ Yetkazildi",
                callback_data=f"ord:status:{user_id}:{number}:Yetkazildi",
            ),
        ],
        [
            InlineKeyboardButton(
                "❌ Bekor qilish",
                callback_data=f"ord:status:{user_id}:{number}:Bekor qilindi",
            )
        ],
        [
            InlineKeyboardButton(
                "✏️ Buyurtmani tahrirlash",
                callback_data=f"ord:edit:{user_id}:{number}",
            )
        ],
    ])


# ================= USER ORDERS =================

async def show_user_orders(update, context):
    user_id = str(update.effective_user.id)
    orders = ORDERS.get(user_id, [])
    if not orders:
        await update.message.reply_text("📦 Sizda hali buyurtmalar yo'q.")
        return

    lines = ["📦 BUYURTMALARIM\n"]
    for order in reversed(orders[-10:]):
        lines.append(
            f'🧾 №{order["number"]} | {money(order["total"])}\n'
            f'📌 {order.get("status", "Yangi")} | {order.get("date", "")}'
        )
    await update.message.reply_text("\n\n".join(lines))


# ================= ADMIN =================

def all_orders():
    result = []
    for orders in ORDERS.values():
        result.extend(orders)
    return sorted(result, key=lambda x: int(x.get("number", 0)), reverse=True)


def admin_products_keyboard(action=None):
    rows = []
    for product_id, product in PRODUCTS.items():
        if action:
            rows.append([
                InlineKeyboardButton(
                    f'{product["name"]} — {money(product["price"])}',
                    callback_data=f"prod:{action}:{product_id}",
                )
            ])
    rows.append([InlineKeyboardButton("⬅️ Admin panel", callback_data="admin_back")])
    return InlineKeyboardMarkup(rows)


# ================= ADMIN CALLBACK =================

async def admin_callbacks(update, context):
    query = update.callback_query
    data = query.data
    user_id = query.from_user.id

    if not is_admin(user_id):
        await query.answer("Sizda admin huquqi yo'q.", show_alert=True)
        return

    # BACK
    if data == "admin_back":
        await query.edit_message_text(
            "🔐 ADMIN PANEL",
            reply_markup=admin_keyboard(),
        )
        return

    # ORDERS
    if data == "admin_orders":
        orders = all_orders()
        if not orders:
            await query.edit_message_text(
                "📦 Hozircha buyurtmalar yo'q.",
                reply_markup=admin_keyboard(),
            )
            return

        rows = []
        for order in orders[:30]:
            rows.append([
                InlineKeyboardButton(
                    f'№{order["number"]} | {order["customer"]} | {money(order["total"])}',
                    callback_data=f'ord:view:{order["user_id"]}:{order["number"]}',
                )
            ])
        rows.append([InlineKeyboardButton("⬅️ Orqaga", callback_data="admin_back")])
        await query.edit_message_text(
            "📦 BUYURTMALAR:",
            reply_markup=InlineKeyboardMarkup(rows),
        )
        return

    # PRODUCTS
    if data == "admin_products":
        lines = ["🛍 MAHSULOTLAR\n"]
        for pid, product in PRODUCTS.items():
            lines.append(
                f'🔹 {pid} — {product["name"]} — {money(product["price"])} — '
                f'{CATEGORIES.get(product["category"], product["category"])}'
            )
        await query.edit_message_text(
            "\n".join(lines),
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("⬅️ Admin panel", callback_data="admin_back")]
            ]),
        )
        return

    # ADD
    if data == "admin_add":
        context.user_data["admin_action"] = "add"
        await query.edit_message_text(
            "➕ Mahsulot qo'shish.\n\n"
            "Format:\n"
            "id | nomi | narxi | kategoriya\n\n"
            "Masalan:\n"
            "newburger | Yangi Burger | 50000 | burger"
        )
        return

    # EDIT
    if data == "admin_edit":
        await query.edit_message_text(
            "✏️ Tahrirlash uchun mahsulotni tanlang:",
            reply_markup=admin_products_keyboard("edit"),
        )
        return

    # DELETE
    if data == "admin_delete":
        await query.edit_message_text(
            "🗑 O'chirish uchun mahsulotni tanlang:",
            reply_markup=admin_products_keyboard("delete"),
        )
        return

    # USERS
    if data == "admin_users":
        if not USERS:
            text = "👥 Foydalanuvchilar yo'q."
        else:
            lines = [f"👥 FOYDALANUVCHILAR: {len(USERS)}\n"]
            for user in list(USERS.values())[:50]:
                lines.append(
                    f'👤 {user.get("name", "-")} | '
                    f'ID: {user.get("id", "-")} | '
                    f'@{user.get("username") or "-"}'
                )
            text = "\n".join(lines)
        await query.edit_message_text(
            text,
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("⬅️ Admin panel", callback_data="admin_back")]
            ]),
        )
        return

    # STATS
    if data == "admin_stats":
        orders = all_orders()
        total_sum = sum(int(o.get("total", 0)) for o in orders)
        delivered = sum(1 for o in orders if o.get("status") == "Yetkazildi")
        cancelled = sum(1 for o in orders if o.get("status") == "Bekor qilindi")
        text = (
            "📊 STATISTIKA\n\n"
            f"👥 Foydalanuvchilar: {len(USERS)}\n"
            f"📦 Buyurtmalar: {len(orders)}\n"
            f"✅ Yetkazilgan: {delivered}\n"
            f"❌ Bekor qilingan: {cancelled}\n"
            f"💰 Umumiy summa: {money(total_sum)}\n"
            f"🛍 Mahsulotlar: {len(PRODUCTS)}"
        )
        await query.edit_message_text(
            text,
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("⬅️ Admin panel", callback_data="admin_back")]
            ]),
        )
        return

    # PRODUCT ACTION
    if data.startswith("prod:"):
        _, action, product_id = data.split(":", 2)
        if product_id not in PRODUCTS:
            await query.answer("Mahsulot topilmadi.", show_alert=True)
            return

        if action == "delete":
            product = PRODUCTS.pop(product_id)
            save_json(PRODUCTS_FILE, PRODUCTS)
            await query.edit_message_text(
                f'🗑 "{product["name"]}" o\'chirildi.',
                reply_markup=admin_keyboard(),
            )
            return

        if action == "edit":
            context.user_data["admin_action"] = f"edit:{product_id}"
            product = PRODUCTS[product_id]
            await query.edit_message_text(
                "✏️ Mahsulotni tahrirlash.\n\n"
                "Format:\n"
                "nomi | narxi | kategoriya\n\n"
                "Hozirgi qiymat:\n"
                f'{product["name"]} | {product["price"]} | {product["category"]}'
            )
            return

    # ORDER ACTION
    if data.startswith("ord:"):
        parts = data.split(":", 4)
        if len(parts) < 4:
            return

        action = parts[1]
        order_user_id = parts[2]
        number = parts[3]
        order = find_order(order_user_id, number)

        if not order:
            await query.answer("Buyurtma topilmadi.", show_alert=True)
            return

        if action == "view":
            await query.edit_message_text(
                format_order(order),
                reply_markup=order_admin_keyboard(order_user_id, number),
            )
            return

        if action == "status":
            if len(parts) < 5:
                return
            new_status = parts[4]
            order["status"] = new_status
            save_json(ORDERS_FILE, ORDERS)
            await query.edit_message_text(
                format_order(order),
                reply_markup=order_admin_keyboard(order_user_id, number),
            )
            try:
                await context.bot.send_message(
                    chat_id=int(order_user_id),
                    text=(
                        f"📦 Buyurtma №{order['number']} holati o'zgardi.\n\n"
                        f"📌 Yangi holat: {new_status}"
                    ),
                )
            except Exception as exc:
                print(f"Foydalanuvchiga status yuborilmadi: {exc}")
            return

        if action == "edit":
            context.user_data["admin_action"] = f"edit_order:{order_user_id}:{number}"
            await query.edit_message_text(
                "✏️ Buyurtmani tahrirlash.\n\n"
                "Format:\n"
                "telefon | manzil\n\n"
                f'Hozirgi telefon: {order.get("phone", "-")}\n'
                f'Hozirgi manzil: {order.get("address", "-")}'
            )
            return


# ================= ADMIN TEXT =================

async def handle_admin_text(update, context, text):
    action = context.user_data.get("admin_action")

    # ADD
    if action == "add":
        parts = [x.strip() for x in text.split("|")]
        if len(parts) != 4:
            await update.message.reply_text(
                "❌ Format xato.\n\nid | nomi | narxi | kategoriya"
            )
            return

        product_id, name, price, category = parts
        if product_id in PRODUCTS:
            await update.message.reply_text("❌ Bu ID allaqachon mavjud.")
            return

        try:
            price = int(price)
        except ValueError:
            await update.message.reply_text("❌ Narx son bo'lishi kerak.")
            return

        if category not in CATEGORIES:
            await update.message.reply_text(
                f"❌ Kategoriya noto'g'ri.\nMavjud: {', '.join(CATEGORIES.keys())}"
            )
            return

        PRODUCTS[product_id] = {
            "name": name,
            "price": price,
            "category": category,
        }
        save_json(PRODUCTS_FILE, PRODUCTS)
        context.user_data.pop("admin_action", None)

        await update.message.reply_text(
            f"✅ Mahsulot qo'shildi:\n"
            f"🍔 {name}\n"
            f"💰 {money(price)}\n"
            f"📂 {CATEGORIES[category]}",
            reply_markup=admin_keyboard(),
        )
        return

    # EDIT PRODUCT
    if action and action.startswith("edit:"):
        product_id = action.split(":", 1)[1]
        if product_id not in PRODUCTS:
            context.user_data.pop("admin_action", None)
            await update.message.reply_text("❌ Mahsulot topilmadi.")
            return

        parts = [x.strip() for x in text.split("|")]
        if len(parts) != 3:
            await update.message.reply_text(
                "❌ Format xato:\nnomi | narxi | kategoriya"
            )
            return

        name, price, category = parts
        try:
            price = int(price)
        except ValueError:
            await update.message.reply_text("❌ Narx son bo'lishi kerak.")
            return

        if category not in CATEGORIES:
            await update.message.reply_text(
                f"❌ Kategoriya noto'g'ri:\n{', '.join(CATEGORIES.keys())}"
            )
            return

        PRODUCTS[product_id] = {
            "name": name,
            "price": price,
            "category": category,
        }
        save_json(PRODUCTS_FILE, PRODUCTS)
        context.user_data.pop("admin_action", None)

        await update.message.reply_text(
            f"✅ Mahsulot yangilandi:\n{name} — {money(price)}",
            reply_markup=admin_keyboard(),
        )
        return

    # EDIT ORDER
    if action and action.startswith("edit_order:"):
        _, order_user_id, number = action.split(":")
        order = find_order(order_user_id, number)
        if not order:
            context.user_data.pop("admin_action", None)
            await update.message.reply_text("❌ Buyurtma topilmadi.")
            return

        parts = [x.strip() for x in text.split("|")]
        if len(parts) != 2:
            await update.message.reply_text("❌ Format xato:\ntelefon | manzil")
            return

        order["phone"] = parts[0]
        order["address"] = parts[1]
        save_json(ORDERS_FILE, ORDERS)
        context.user_data.pop("admin_action", None)

        await update.message.reply_text(
            "✅ Buyurtma ma'lumotlari yangilandi.",
            reply_markup=admin_keyboard(),
        )
        try:
            await context.bot.send_message(
                chat_id=int(order_user_id),
                text=f"✏️ Buyurtma №{number} ma'lumotlari yangilandi.",
            )
        except Exception as exc:
            print(f"Foydalanuvchiga xabar yuborilmadi: {exc}")
        return


# ================= ERROR =================

async def error_handler(update, context):
    print(f"Xatolik: {context.error}")


# ================= MAIN =================

def main():
    if TOKEN == "BOT_TOKENINGIZNI_BU_YERGA_QOYING":
        print("❌ Avval TOKEN o'rniga BotFather bergan tokenni yozing.")
        return

    # Termux/VPN tarmog'ida Telegram API sekin javob bersa timeoutni oshiramiz
    app = (
        Application.builder()
        .token(TOKEN)
        .connect_timeout(60)
        .read_timeout(60)
        .write_timeout(60)
        .pool_timeout(60)
        .get_updates_connect_timeout(60)
        .get_updates_read_timeout(60)
        .get_updates_write_timeout(60)
        .get_updates_pool_timeout(60)
        .build()
    )

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(callbacks))
    app.add_handler(MessageHandler(filters.CONTACT, contact_handler))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, text_handler))
    app.add_error_handler(error_handler)

    print("🤖 Bot ishga tushdi...")
    print("📡 Telegram serveriga ulanmoqda...")

    try:
        app.run_polling(
            drop_pending_updates=True,
            allowed_updates=Update.ALL_TYPES,
        )
    except Exception as exc:
        print(f"❌ Bot ishga tushishda xatolik: {exc}")
        print("📡 Internet/VPN va BOT TOKENni tekshiring.")


if __name__ == "__main__":
    main()
