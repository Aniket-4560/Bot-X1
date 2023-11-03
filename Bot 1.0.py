import requests
import asyncio
from datetime import datetime, timedelta
from telethon.sync import TelegramClient, events

api_id = '6'
api_hash = 'eb06d4abfb49dc3eeb1aeb98ae0f581e'
bot_token = '6482350998:AAF05OkmabCsNPYr9me09exx4ij0svv6iVs'

# SMMStone API credentials
api_key = 'd819a1f00c233199588f18d6b904216d'
api_url = 'https://smmstone.com/api/v2'

# Initialize Telethon client
client = TelegramClient('bot_session', api_id, api_hash).start(bot_token=bot_token)
print("Bot is online!")

ongoing_processes = {}
#channel_ids = {}
channel_id_counter = 1


@client.on(events.NewMessage(pattern='/add_channel'))
async def add_channel(event):  
    #global channel_ids  # Declare channel_ids as a global variable
    global channel_id_counter
    try:
        # Assuming the user provides the necessary parameters in the message content
        params = event.raw_text.split(' ')
        service_id = params[1]
        link = params[2]
        quantity = params[3]
        runs = params[4]
        interval = params[5]

        # Allocate a unique channel ID if it's a new channel
        chat_id = event.chat_id
        channel_id = channel_id_counter
        channel_id_counter += 1

        #ongoing_processes[channel_id] = []  # Add this line to store the new channel
        ongoing_processes[channel_id] = {'cancelled': False, 'processes': []}


        for run in range(1, int(runs)+1):
            if ongoing_processes[channel_id]['cancelled']:
                await event.respond(f'All ongoing processes for channel ID {channel_id} have been cancelled.')
                break
            
            # Prepare the request parameters
            params = {
                'key': api_key,
                'action': 'add',
                'service': int(service_id),
                'link': link,
                'quantity': int(quantity),
            }

            # Add optional parameters if provided
            if runs:
                params['runs'] = int(runs)
            if interval:
                params['interval'] = int(interval)

            # Make the API call
            response = requests.post(api_url, params=params)

            if response.status_code == 200:
                order_id = response.json().get('order')

                # Calculate time of next run
                next_run_time = datetime.now() + timedelta(minutes=int(interval))
                next_run_formatted = next_run_time.strftime("%Y-%m-%d %H:%M:%S")

                new_message = f'Successfully placed order ID {order_id}. Run {run}/{runs}\nNext run at {next_run_formatted}\nChannel Link: {link}\nChannel ID: {channel_id}'

                # Send the message
                msg = await event.respond(new_message)
                #ongoing_processes[chat_id][-1]['message_id'] = msg.id
            else:
                await event.respond(f'Error: {response.text}')

            # If it's not the last run, wait for the specified interval (in seconds) before next iteration
            if run < int(runs):
                await asyncio.sleep(int(interval) * 10)  # Convert minutes to seconds

    except Exception as e:
        await event.respond(f'Error: {e}')

@client.on(events.NewMessage(pattern='/cancel'))
async def cancel_process(event):
    try:
        channel_id_to_cancel = int(event.raw_text.split(' ')[1])

        if channel_id_to_cancel in ongoing_processes:
            ongoing_processes[channel_id_to_cancel]['cancelled'] = True
            await event.respond(f'All ongoing processes for channel ID {channel_id_to_cancel} will be cancelled after the current run.')

        else:
            await event.respond(f'No ongoing process found for channel ID {channel_id_to_cancel}.')

    except Exception as e:
        await event.respond(f'Error: {e}')
        
# Run the bot
client.run_until_disconnected()
