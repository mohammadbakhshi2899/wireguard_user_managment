from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackQueryHandler
from telegram import InlineKeyboardMarkup, InlineKeyboardButton
from db_functions import *
from gen_config import gen_config
import datetime

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)

# For first time running.
if get_admin_user_id() is None:
    logging.error("Please add an admin user to database.")


def start(update, context):
    if check_user_exist(update.message.from_user.id):
        update.message.reply_text("You've already registered.")
    else:
        update.message.reply_text('Please send 15T to my cart\nAnd send a screenshot from your payment')


def alarm(context):
    job = context.job
    context.bot.send_message(job.context, text='Warning: your account will expire tomorrow!')
    context.bot.send_message(job.context, text='Please send a screenshot from your payment.')


def error(update, context):
    logger.warning('Update "%s" caused error "%s"', update, context.error)


def remains(update, context):
    user_id = update.message.from_user.id
    if check_user_exist(user_id):
        day = get_expiration_date(user_id)
        if day != 0:
            update.message.reply_text(f"You still have {day} day.")
        else:
            update.message.reply_text("Your account has expired.")
    else:
        update.message.reply_text("Sorry. You're not registered yet.")


def confirmation_handler(update, context):
    data = update.callback_query.data
    user_id = data[1:]
    if data[0] == 'n':
        context.bot.send_message(chat_id=user_id, text='Sorry payment is invalid.')
    elif data[0] == 'y':
        if check_user_exist(user_id):
            if check_expired(user_id):
                context.bot.send_message(chat_id=user_id, text='Your account updated for next month.')
                update_user(user_id)
        else:
            user = get_tmp_user(user_id)
            # Generate file config
            file_name = gen_config()
            with open(file_name, 'r') as fd:
                context.bot.sendDocument(user_id, document=fd)
            add_user(user_id, user[2])
            context.bot.send_message(chat_id=user_id, text=f'Hi! You are now registered.')
            context.job_queue.run_daily(alarm, datetime.time(13, 45, 00), context=user_id, name=str(user_id))


def image_payment(update, context):
    user_id = update.message.from_user.id
    file = context.bot.getFile(update.message.photo[-1].file_id)
    file.download(f'img/{user_id}.jpg')
    if check_user_exist(user_id):
        if not check_expired(user_id):
            update.message.reply_text("You've already payed for this month.")
            return
    # Add new users in temp users table
    else:
        add_tmp_user(user_id, update.message.from_user.name)

    update.message.reply_text("Waiting for confirmation.\nIt might take a while.")
    # Get confirmation from admin.
    context.bot.send_photo(chat_id=get_admin_user_id(), photo=update.message.photo[-1])
    keyboard = InlineKeyboardMarkup([[InlineKeyboardButton('YES', callback_data='y' + str(user_id)),
                                      InlineKeyboardButton('NO', callback_data='n' + str(user_id))]])
    context.bot.send_message(chat_id=get_admin_user_id(), text='confirm?', reply_markup=keyboard)


def main():
    updater = Updater("TOKEN", use_context=True)
    dp = updater.dispatcher
    dp.add_handler(CallbackQueryHandler(confirmation_handler))
    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(CommandHandler("remains", remains))
    dp.add_handler(MessageHandler(Filters.photo, image_payment))
    dp.add_error_handler(error)
    updater.start_polling()

    updater.idle()


if __name__ == '__main__':
    main()
