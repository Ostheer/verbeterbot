# handlers
def start(update, context):
    # Start de verstandhouding
    update.message.reply_text('Hi!')

def help(update, context):
    # Wees behulpzaam
    update.message.reply_text('Help!')

def galm(update, context):
    # Weerklank van verzonden bericht
    update.message.reply_text(update.message.text)
