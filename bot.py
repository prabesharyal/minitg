from dotenv import load_dotenv
load_dotenv()

#import inbuilt modules
from ast import main
import os, shutil, time, re, requests


#import downloaders
import yt_dlp

#Import Telegram Features
from telegram import InputMediaAudio, InputMediaVideo, Update, ReplyKeyboardRemove
from telegram.ext import Application, CommandHandler, ContextTypes, MessageHandler, filters

#import openai
import openai

API_HASH = TG_BOT = os.getenv('TG_BOT_TOKEN')
# API_HASH = ''
openai.api_key = os.environ.get('OPENAI_API_KEY')
model_engine = "gpt-3.5-turbo" 
# openai.api_key = ''

def convert_html(string):
    string= string.replace('<', '&lt')
    string= string.replace('>', '&gt')
    return string


def caption_cleaner(title):
    text = re.sub(r'\d{4}\/\d{2}\/\d{2}|(?:[01]\d|2[0-3]):(?:[0-5]\d):(?:[0-5]\d)|UTC|@[A-Za-z0-9_.]+|\#[A-Za-z0-9_]+|▫️$|•| :\n|\n\.\n|\.\n\.|follow|via|credit|Follow|Via| - |',"",title)
    text = re.sub(r'(https?:\/\/)?([\da-z\.-]+)\.([a-z\.]{2,6})([\/\w \.-]*)',"", text)
    text = re.sub(r'[\s]{3}','',text)
    return text


def clean_clutter():
    print("Removing If any Previously unused files.")
    for files in os.listdir():    
        if files.endswith(('py','json','Procfile','txt','text','pip','git','pycache','cache','session','vendor','profile.d','heroku'))==False:
            if os.path.isdir(files) == True:
                print("Removing Dir : {}".format(files))
                shutil.rmtree(files)
            #elif os.path.isdir(files) == True:
                #print("Skipping Dir : {}".format(files))
            else:
                os.remove(files)
                print("Removed File : {}".format(files))

def yt_dlp_tiktok_dl(URLS):
    if re.match(r"(?:https:\/\/)?([vt]+)\.([tiktok]+)\.([com]+)\/([\/\w@?=&\.-]+)", URLS):
        r = requests.head(URLS, allow_redirects=False)
        URLS = r.headers['Location']
    ydl_opts = {'ignoreerrors': True, 'trim_file_name' : 25}
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(URLS)
        video_title = info['title']
    video_title = "✨" if video_title == '' else video_title
    video_title = convert_html(video_title)
    CAPTION = '<a href="{}">{}</a>'.format(URLS,video_title)
    return CAPTION

def yt_dlp_ig_reel_dl(URLS):
    ydl_opts = {'ignoreerrors': True, 'trim_file_name' : 25}
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(URLS)
        video_title = info['description']
    video_title = caption_cleaner(video_title)
    video_title = convert_html(video_title)
    video_title = "✨" if re.match(r'^[\s|\n]+$',video_title) else video_title
    CAPTION = '<a href="{}">{}</a>'.format(URLS,video_title)
    return CAPTION

def yt_dlp_youtube_dl(URLS):
    ydl_opts = {'trim_file_name' : 20,'max_filesize':50*1024*1024, 'format_sort': ['res:1080','ext:mp4:m4a']}
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(URLS)
        video_title = info['title']
    video_title = "✨" if video_title == '' else video_title
    video_title = convert_html(video_title)
    CAPTION = '<a href="{}">{}</a>'.format(URLS,video_title)
    return CAPTION

def yt_dlp_youtube_audio_dl(URLS):
    ydl_opts = {'format': 'm4a/bestaudio/best',
    # ℹ️ See help(yt_dlp.postprocessor) for a list of available Postprocessors and their arguments
    'postprocessors': [{  # Extract audio using ffmpeg
        'key': 'FFmpegExtractAudio',
        'preferredcodec': 'mp3',}]}
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(URLS)
        audio_title = info['title']
    audio_title = "✨" if audio_title == '' else audio_title
    CAPTION = '<a href="{}">{}</a>'.format(URLS,audio_title)
    return CAPTION

def yt_dlp_Others_dl(URLS):
    ydl_opts = {'trim_file_name' : 20, 'max_filesize':50*1024*1024}
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(URLS)
        video_title = info['title']
    video_title = "✨" if video_title == '' else video_title
    video_title = convert_html(video_title)
    CAPTION = '<a href="{}">{}</a>'.format(URLS,video_title)
    return CAPTION

async def yt_dlp_sender(update,context,CAPTION):
    downloaded_files = os.listdir('./')
    tosend=list()
    for medias in downloaded_files:
        size =int((os.path.getsize(medias))/(1024*1024))
        if os.path.isdir(medias):
            'is a directory'
        elif medias.endswith(('avi', 'flv', 'mkv', 'mov', 'mp4', 'webm', '3g2', '3gp', 'f4v', 'mk3d', 'divx', 'mpg', 'ogv', 'm4v', 'wmv', 'aiff', 'alac', 'flac', 'm4a', 'mka', 'mp3', 'ogg', 'opus', 'wav','aac', 'ape', 'asf', 'f4a', 'f4b', 'm4b', 'm4p', 'm4r', 'oga', 'ogx', 'spx', 'vorbis', 'wma')):
            tosend.append(medias)
        elif size < 50 and medias.endswith(('py','json','Procfile','txt','text','pip', 'md','git','pycache','cache','session','vendor','profile.d'))==False:
            os.remove(medias)
        elif size > 50 or medias.endswith('part'):
            print(medias + "is "+str(size)+" MB."+"\n"+"Which is greater than 50 MB, So removing it !!")
            os.remove(medias)
    #print(tosend)
    if tosend == None:
        return "No Files Downloaded"
    no_of_files = len(tosend)
    if no_of_files == 1:
        files = tosend[0]
        if files.endswith(('avi', 'flv', 'mkv', 'mov', 'mp4', 'webm', '3g2', '3gp', 'f4v', 'mk3d', 'divx', 'mpg', 'ogv', 'm4v', 'wmv')):
                print("Found Short Video and Sending!!!")
                await context.bot.send_video(chat_id=update.message.chat_id, video=open(files, 'rb'), supports_streaming=True,caption = CAPTION, parse_mode='HTML')
                print("Video {} was Sent Successfully!".format(files))
                os.remove(files)
                try:
                    await context.bot.delete_message(chat_id=update.message.chat.id, message_id=update.message.message_id)
                except BaseException:
                    print("Message was already deleted.")
                time.sleep(3)
        elif files.endswith(('aiff', 'alac', 'flac', 'm4a', 'mka', 'mp3', 'ogg', 'opus', 'wav','aac', 'ape', 'asf', 'f4a', 'f4b', 'm4b', 'm4p', 'm4r', 'oga', 'ogx', 'spx', 'vorbis', 'wma')):
                print("Found Short Audio")
                await context.bot.send_audio(chat_id=update.message.chat_id, audio=open(files, 'rb'), caption = CAPTION, parse_mode='HTML')
                print("Audio {} was Sent Successfully!".format(files))
                os.remove(files)
                try:
                    await context.bot.delete_message(chat_id=update.message.chat.id, message_id=update.message.message_id)
                except BaseException:
                    print("Message was already deleted. \n \n")
                time.sleep(2)
    elif no_of_files > 1 and no_of_files<=10:
        media_group=[]
        for multimedias in tosend:
                if multimedias.endswith(('avi', 'flv', 'mkv', 'mov', 'mp4', 'webm', '3g2', '3gp', 'f4v', 'mk3d', 'divx', 'mpg', 'ogv', 'm4v', 'wmv')): #appends videos

                    media_group.append(InputMediaVideo(open(multimedias,'rb'),caption = CAPTION if len(media_group) == 0 else '',parse_mode='HTML'))
                elif multimedias.endswith(('aiff', 'alac', 'flac', 'm4a', 'mka', 'mp3', 'ogg', 'opus', 'wav','aac', 'ape', 'asf', 'f4a', 'f4b', 'm4b', 'm4p', 'm4r', 'oga', 'ogx', 'spx', 'vorbis', 'wma')): #appends audios

                    media_group.append(InputMediaAudio(open(multimedias,'rb'), caption = CAPTION if len(media_group) == 0 else '',parse_mode='HTML'))
        
        await context.bot.send_media_group(chat_id = update.message.chat.id, media = media_group, write_timeout=60)
        media_group = []
        try:
            await context.bot.delete_message(chat_id=update.message.chat.id, message_id=update.message.message_id)
        except BaseException:
            print("Yt-DLP Sender, Message was already deleted.")
    
    for todlete in os.listdir('./'):
        if os.path.isdir(todlete)==False and todlete.endswith(('py','json','Procfile','txt','text','pip','git','pycache','cache','session','vendor','profile.d'))==False:
            os.remove(todlete)
            print("removed file"+todlete)


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Send a message when the command /start is issued."""
    user = update.effective_user
    print(update.message['text']+" - Bot is already running!")
    await update.message.reply_html(
        rf"Dear {user.mention_html()}, Bot is active, Send URLs of supported sites to get video.", reply_markup=ReplyKeyboardRemove(selective=True))

async def help(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Send a message when the command /help is issued."""
    user = update.effective_user
    print(update.message['text']+" - Help Command Issued")
    await context.bot.delete_message(chat_id=update.message.chat.id, message_id=update.message.message_id)
    await context.bot.send_message(chat_id=update.message.chat.id, text='''<b><u> A lot of help commands available.</u></b>\n \n    <code>/start</code> - <i>Check whether bot is working or not.</i>\n    <code>/help</code> - <i>This menu is displayed.</i>\n    <code>/clean</code> - <i>Resets the bot server to the deployment time.</i>\n \n    <b>Any Sort of Public Video Links </b> - <i>Sends you video upto 50MB using that link.</i>\n\n    <code>/ytaudio </code><u>your_youtube_link</u> - <i>Sends audio from link.</i> \n\n <b> Some OpenAI tools :</b>\n    &#8226;<code>/dalle </code><u>Write Something to generate Image from.</u> - <i>Sends pictures from text.</i>\n    &#8226;<code>/gpt </code><u>Write Something to generate Text from.</u> - <i>Completes Your Text.</i> \n\n<b>Isn't this help enough ???</b>''',parse_mode='HTML')

#''''''

async def clean(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Send a message when the command /clean is issued."""
    clean_clutter()
    print("Server clean was success.")
    await context.bot.delete_message(chat_id=update.message.chat.id, message_id=update.message.message_id)
    await context.bot.send_message(chat_id=update.message.chat.id, text='Server is <b>virgin</b> again.',parse_mode='HTML')


async def yt_audio(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    link = (((update.message['text']).split(" "))[1])
    print("Through Yt-audio downloader")
    try :
        CAPTION = yt_dlp_youtube_audio_dl(link)
        await yt_dlp_sender(update,context,CAPTION)
    except BaseException:
        print("Audio Download Error")
        await context.bot.send_message(chat_id=update.message.chat.id, text="Sorry, Couldn't download audio of from given link : <code>{}</code> . \n Check link again and make sure if it works.".format(link),parse_mode='HTML')

async def dalle(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    
    rawtext = str((update.message['text']))
    generate = rawtext[6:]
    print("Generating Image from Text : "+ generate)
    try :
        response = openai.Image.create(prompt=generate, n=1, size="1024x1024")
        image_url = response['data'][0]['url']
        await context.bot.send_message(chat_id=update.message.chat.id, text='<a href="{}">{}</a>'.format(image_url,generate),parse_mode='HTML')
        await context.bot.delete_message(chat_id=update.message.chat.id, message_id=update.message.message_id)
        print("Sent Image Successfully !")
    except BaseException:
        print("Some Error in Dalle.")
        await context.bot.send_message(chat_id=update.message.chat.id, text="Sorry, Couldn't generate Image from your message : <code>{}</code> . \n\n Please try again later. \n\n <i>Note: Sometimes it happens when you violate Terms and Conditions !</i>".format(generate),parse_mode='HTML')

async def gpt(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    rawtext = str((update.message['text']))
    title = rawtext[4:]
    print("Generating Response : " + title)
    try :
        response = openai.ChatCompletion.create(
        model='gpt-3.5-turbo',
        n=1,
        messages=[
            {"role": "system", "content": "You are a helpful assistant with exciting, interesting things to say."},
            {"role": "user", "content": title},
        ])
        completedtext = response.choices[0]['message']['content']
        await context.bot.send_message(chat_id=update.message.chat.id, text='*{}* \n\n{}'.format(title,completedtext),parse_mode='MARKDOWN')
        # await context.bot.delete_message(chat_id=update.message.chat.id, message_id=update.message.message_id)
        print("Sent generated text !")
    except BaseException:
        print("Some Error in GPT.")
        await context.bot.send_message(chat_id=update.message.chat.id, text="Sorry, Couldn't complete text from your message : <code>{}</code> . \n\n Please try again later.\n\n <i>Note: Sometimes it happens when you violate Terms and Conditions !</i>".format(title),parse_mode='HTML')


async def main_url_dl(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    clean_clutter()
    string = update.message.text
    print(string)
    pattern = '([^\s\.]+\.[^\s]{2,}|www\.[^\s]+\.[^\s]{2,})'
    entries = re.findall(pattern, string)
    for URLS in entries:
        if re.match(r"(?:https:\/\/)?([vt]+|[www]+)\.?([tiktok]+)\.([com]+)\/([\/\w@?=&\.-]+)", URLS):
            CAPTION = yt_dlp_tiktok_dl(URLS)
            await yt_dlp_sender(update,context,CAPTION)
        
        elif re.match(r"((?:http|https):\/\/)(?:www.)?(?:instagram.com|instagr.am|instagr.com)\/(\w+)\/([\w\-/?=&]+)",URLS):
            try:
                print("Instaloader Module Failed, retrying with yt-dlp")
                CAPTION = yt_dlp_ig_reel_dl(URLS)
                await yt_dlp_sender(update,context,CAPTION)
            except BaseException:
                print("yt-dlp module failed downloading this video. \n Maybe not a video or private one.")
        
        elif re.match(r"(?:https?:\/\/)?(?:www\.|m\.)?youtu\.?be(?:\.com)?\/?.*(?:watch|embed)?(?:.*v=|v\/|\/)([\w\-_\&=]+)?", URLS):
            CAPTION = yt_dlp_youtube_dl(URLS)
            await yt_dlp_sender(update,context,CAPTION)
        
        else:
            try:
                CAPTION = yt_dlp_Others_dl(URLS)
                await yt_dlp_sender(update,context,CAPTION)
            except BaseException:
                print("Unsupported URL : {}".format(URLS))



def main() -> None:
    """Start the bot."""
    # Create the Application and pass it your bot's token.
    application = Application.builder().token(API_HASH).read_timeout(10).write_timeout(50).get_updates_read_timeout(42).connect_timeout(30).build()
    print("Application is running!")
    # on different commands - answer in Telegram
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("help", help))
    application.add_handler(CommandHandler("clean", clean))
    #youtube music
    application.add_handler(CommandHandler("ytaudio", yt_audio))
    
    #DALLE
    application.add_handler(CommandHandler("dalle", dalle))
    
    #gpt
    application.add_handler(CommandHandler("gpt", gpt))

    #For other links
    application.add_handler(MessageHandler(filters.Regex('([^\s\.]+\.[^\s]{2,}|www\.[^\s]+\.[^\s]{2,})') & ~filters.COMMAND, main_url_dl))

    # Run the bot until the user presses Ctrl-C
    application.run_polling()

if __name__ == "__main__":
    main()