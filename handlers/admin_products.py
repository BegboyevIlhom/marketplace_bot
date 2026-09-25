from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext
import json

import db.database as db
from utils.states import AddProduct, EditProduct
from handlers.admin_menu import is_admin
from keyboards.admin_kb import (
    admin_categories_kb, admin_products_kb, skip_old_price_kb, photo_extra_done_kb,
    availability_kb, add_product_confirm_kb, edit_product_fields_kb, confirm_delete_kb,
    ADMIN_BTN_ADD_PRODUCT, ADMIN_BTN_EDIT_PRODUCT,
)

router = Router()


# ============== ADD PRODUCT ==============

@router.message(F.text == ADMIN_BTN_ADD_PRODUCT)
async def add_product_start(message: Message, state: FSMContext):
    if not is_admin(message.from_user.id):
        return
    categories = await db.get_categories()
    await state.set_state(AddProduct.category)
    await message.answer(
        "Kategoriyani tanlang yoki yangisini qo'shing:",
        reply_markup=admin_categories_kb(categories, "addcat", with_add=True),
    )


@router.callback_query(AddProduct.category, F.data == "addcat:new")
async def add_new_category(callback: CallbackQuery, state: FSMContext):
    await callback.message.answer("Yangi kategoriya nomi (RU):")
    await state.set_state(AddProduct.new_category_ru)
    await callback.answer()


@router.message(AddProduct.new_category_ru)
async def new_category_ru(message: Message, state: FSMContext):
    await state.update_data(new_cat_ru=message.text)
    await message.answer("Yangi kategoriya nomi (UZ):")
    await state.set_state(AddProduct.new_category_uz)


@router.message(AddProduct.new_category_uz)
async def new_category_uz(message: Message, state: FSMContext):
    data = await state.get_data()
    cat_id = await db.add_category(data["new_cat_ru"], message.text)
    await state.update_data(category_id=cat_id)
    await message.answer("Nomi RU:")
    await state.set_state(AddProduct.name_ru)


@router.callback_query(AddProduct.category, F.data.startswith("addcat:"))
async def add_product_category_chosen(callback: CallbackQuery, state: FSMContext):
    cat_id = int(callback.data.split(":")[1])
    await state.update_data(category_id=cat_id)
    await callback.message.answer("Nomi RU:")
    await state.set_state(AddProduct.name_ru)
    await callback.answer()


@router.message(AddProduct.name_ru)
async def add_name_ru(message: Message, state: FSMContext):
    await state.update_data(name_ru=message.text)
    await message.answer("Nomi UZ:")
    await state.set_state(AddProduct.name_uz)


@router.message(AddProduct.name_uz)
async def add_name_uz(message: Message, state: FSMContext):
    await state.update_data(name_uz=message.text)
    await message.answer("Qisqa tavsif RU (1-3 qator):")
    await state.set_state(AddProduct.short_ru)


@router.message(AddProduct.short_ru)
async def add_short_ru(message: Message, state: FSMContext):
    await state.update_data(short_ru=message.text)
    await message.answer("Qisqa tavsif UZ:")
    await state.set_state(AddProduct.short_uz)


@router.message(AddProduct.short_uz)
async def add_short_uz(message: Message, state: FSMContext):
    await state.update_data(short_uz=message.text)
    await message.answer("To'liq tavsif RU:")
    await state.set_state(AddProduct.full_ru)


@router.message(AddProduct.full_ru)
async def add_full_ru(message: Message, state: FSMContext):
    await state.update_data(full_ru=message.text)
    await message.answer("To'liq tavsif UZ:")
    await state.set_state(AddProduct.full_uz)


@router.message(AddProduct.full_uz)
async def add_full_uz(message: Message, state: FSMContext):
    await state.update_data(full_uz=message.text)
    await message.answer("Narxni kiriting (faqat raqam, so'mda):")
    await state.set_state(AddProduct.price)


@router.message(AddProduct.price)
async def add_price(message: Message, state: FSMContext):
    if not message.text.isdigit():
        await message.answer("Iltimos faqat raqam kiriting:")
        return
    await state.update_data(price=int(message.text))
    await message.answer(
        "Eski narx (chegirma ko'rsatish uchun), yoki o'tkazib yuboring:",
        reply_markup=skip_old_price_kb(),
    )
    await state.set_state(AddProduct.old_price)


@router.callback_query(AddProduct.old_price, F.data == "skip")
async def skip_old_price(callback: CallbackQuery, state: FSMContext):
    await state.update_data(old_price=None)
    await callback.message.answer("Asosiy rasmni yuboring:")
    await state.set_state(AddProduct.photo_main)
    await callback.answer()


@router.message(AddProduct.old_price)
async def add_old_price(message: Message, state: FSMContext):
    if not message.text.isdigit():
        await message.answer("Iltimos faqat raqam kiriting, yoki tugmani bosing:")
        return
    await state.update_data(old_price=int(message.text))
    await message.answer("Asosiy rasmni yuboring:")
    await state.set_state(AddProduct.photo_main)


@router.message(AddProduct.photo_main, F.photo)
async def add_photo_main(message: Message, state: FSMContext):
    file_id = message.photo[-1].file_id
    await state.update_data(photo_main=file_id, photos_extra=[])
    await message.answer(
        "Qo'shimcha rasm yuboring, yoki 'Tayyor' tugmasini bosing:",
        reply_markup=photo_extra_done_kb(),
    )
    await state.set_state(AddProduct.photo_extra)


@router.message(AddProduct.photo_extra, F.photo)
async def add_photo_extra(message: Message, state: FSMContext):
    data = await state.get_data()
    extra = data.get("photos_extra", [])
    extra.append(message.photo[-1].file_id)
    await state.update_data(photos_extra=extra)
    await message.answer(
        f"Qo'shildi ({len(extra)} ta). Yana yuborishingiz mumkin, yoki 'Tayyor':",
        reply_markup=photo_extra_done_kb(),
    )


@router.callback_query(AddProduct.photo_extra, F.data == "done")
async def photo_extra_done(callback: CallbackQuery, state: FSMContext):
    await callback.message.answer("Mahsulot mavjudmi?", reply_markup=availability_kb())
    await state.set_state(AddProduct.characteristics)
    await callback.answer()


@router.callback_query(AddProduct.characteristics, F.data.startswith("avail:"))
async def add_availability(callback: CallbackQuery, state: FSMContext):
    available = callback.data.split(":")[1] == "1"
    await state.update_data(available=available)
    await callback.message.answer("Xarakteristikalar (yo'q bo'lsa '-' yozing):")
    await callback.answer()


@router.message(AddProduct.characteristics)
async def add_characteristics(message: Message, state: FSMContext):
    chars = "" if message.text.strip() == "-" else message.text
    await state.update_data(characteristics_ru=chars, characteristics_uz=chars)
    data = await state.get_data()

    price = f"{data['price']:,}".replace(",", " ")
    preview = f"📦 {data['name_ru']}\n\n{data['short_ru']}\n\n{data['full_ru']}\n\n💰 {price}"
    if chars:
        preview += f"\n🔧 {chars}"

    await state.set_state(AddProduct.confirm)
    await message.answer_photo(
        data["photo_main"], caption=preview, reply_markup=add_product_confirm_kb()
    )


@router.callback_query(AddProduct.confirm, F.data == "publish")
async def publish_product(callback: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    product_id = await db.add_product(data)
    await state.clear()
    await callback.message.answer(f"✅ Mahsulot qo'shildi (ID: {product_id})")
    await callback.answer()


@router.callback_query(AddProduct.confirm, F.data == "cancel_add")
async def cancel_add_product(callback: CallbackQuery, state: FSMContext):
    await state.clear()
    await callback.message.answer("❌ Bekor qilindi")
    await callback.answer()


# ============== EDIT / DELETE PRODUCT ==============

@router.message(F.text == ADMIN_BTN_EDIT_PRODUCT)
async def edit_product_start(message: Message, state: FSMContext):
    if not is_admin(message.from_user.id):
        return
    categories = await db.get_categories()
    if not categories:
        await message.answer("Hozircha kategoriyalar yo'q.")
        return
    await state.set_state(EditProduct.choose_category)
    await message.answer("Kategoriyani tanlang:", reply_markup=admin_categories_kb(categories, "editcat"))


@router.callback_query(EditProduct.choose_category, F.data.startswith("editcat:"))
async def edit_choose_category(callback: CallbackQuery, state: FSMContext):
    cat_id = int(callback.data.split(":")[1])
    products = await db.get_products_by_category(cat_id, include_hidden=True)
    if not products:
        await callback.answer("Bu kategoriyada tovar yo'q.", show_alert=True)
        return
    await state.set_state(EditProduct.choose_product)
    await callback.message.answer("Mahsulotni tanlang:", reply_markup=admin_products_kb(products, "editprod"))
    await callback.answer()


@router.callback_query(EditProduct.choose_product, F.data.startswith("editprod:"))
async def edit_choose_product(callback: CallbackQuery, state: FSMContext):
    product_id = int(callback.data.split(":")[1])
    p = await db.get_product(product_id)
    text = f"📦 {p['name_ru']} — {p['price']:,}".replace(",", " ")
    text += f"\nStatus: {'yashirilgan' if p['is_hidden'] else 'faol'}"
    await state.set_state(EditProduct.choose_field)
    await callback.message.answer(text, reply_markup=edit_product_fields_kb(product_id))
    await callback.answer()


@router.callback_query(EditProduct.choose_field, F.data.startswith("editf:"))
async def edit_choose_field(callback: CallbackQuery, state: FSMContext):
    _, product_id, field = callback.data.split(":")
    await state.update_data(edit_product_id=int(product_id), edit_field=field)
    await state.set_state(EditProduct.waiting_value)
    if field == "photo_main":
        await callback.message.answer("Yangi rasmni yuboring:")
    else:
        await callback.message.answer("Yangi qiymatni kiriting:")
    await callback.answer()


@router.message(EditProduct.waiting_value, F.photo)
async def edit_value_photo(message: Message, state: FSMContext):
    data = await state.get_data()
    if data["edit_field"] != "photo_main":
        await message.answer("Rasm emas, matn kutilmoqda.")
        return
    await db.update_product_field(data["edit_product_id"], "photo_main", message.photo[-1].file_id)
    await state.clear()
    await message.answer("✅ Yangilandi")


@router.message(EditProduct.waiting_value, F.text)
async def edit_value_text(message: Message, state: FSMContext):
    data = await state.get_data()
    field = data["edit_field"]
    value = message.text
    if field in ("price", "old_price"):
        if not value.isdigit():
            await message.answer("Iltimos faqat raqam kiriting:")
            return
        value = int(value)
    await db.update_product_field(data["edit_product_id"], field, value)
    await state.clear()
    await message.answer("✅ Yangilandi")


@router.callback_query(F.data.startswith("toggle_hide:"))
async def toggle_hide(callback: CallbackQuery):
    product_id = int(callback.data.split(":")[1])
    p = await db.get_product(product_id)
    await db.set_product_hidden(product_id, not p["is_hidden"])
    await callback.answer("Holat o'zgartirildi ✅")


@router.callback_query(F.data.startswith("delprod:"))
async def delete_product_ask(callback: CallbackQuery):
    product_id = int(callback.data.split(":")[1])
    await callback.message.answer(
        "Haqiqatan ham o'chirmoqchimisiz? (eski buyurtmalar buzilmaydi)",
        reply_markup=confirm_delete_kb(product_id),
    )
    await callback.answer()


@router.callback_query(F.data.startswith("delprod_confirm:"))
async def delete_product_confirm(callback: CallbackQuery, state: FSMContext):
    product_id = int(callback.data.split(":")[1])
    await db.delete_product(product_id)
    await state.clear()
    await callback.message.answer("🗑 O'chirildi")
    await callback.answer()


@router.callback_query(F.data == "delprod_cancel")
async def delete_product_cancel(callback: CallbackQuery):
    await callback.message.answer("Bekor qilindi")
    await callback.answer()
