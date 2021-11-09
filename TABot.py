import os
import random
import discord
from discord.ext import tasks

import MACDTrader

#parameters
PRODUCTS = ["ETH-USD", "LRC-USD", "MATIC-USD", "ENJ-USD"]


class MyClient(discord.Client):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.trader = MACDTrader.MACDTrader(products=PRODUCTS)

        self.responses_affirmative = [
            "It is certain", "It is decidedly so", "Without a doubt",
            "Yes definitely", "Yes"
        ]
        self.responses_non_committal = [
            "Ask again later please", "Better not tell you now",
            "Concentrate and ask again", "You already know the answer", "Maybe"
        ]
        self.responses_negative = [
            "Don't count on it", "My reply is no", "My sources say no",
            "Outlook not so good", "Very doubtful", "No"
        ]
        self.user_added = []

        self._8_BALL_ADD_CMD = "8!add"
        self._8_BALL_REM_CMD = "8!rem"
        self._8_BALL_RESPONSES_CMD = "8!responses"
        self._8_BALL_BALL_CMD = "8!ball"

        self.trader_signals.start()

    async def on_ready(self):
        print(f'We have logged in as {self.user} (ID: {self.user.id})')

    #****MACDTrader functions****

    @tasks.loop(seconds=60)
    async def trader_signals(self):
        channel = self.get_channel(int(os.environ['channel_id']))

        signals = self.trader.get_signals()

        for signal in signals:
            await channel.send(signal)

    @trader_signals.before_loop
    async def before_signals(self):
        await self.wait_until_ready()

    #****end MACDTrader functions****

    async def on_message(self, message):

        # ****start MACDTrader commands for the bot****
        if (message.content.startswith('$signal add')):
            try:
                self.trader.add_product(message.content.split(" ")[2])
                await message.channel.send("Product added!")
            except IndexError:
                await message.channel.send(
                    "Please add the product symbol and ensure that it is separated from the command using a space."
                )
            except ValueError:
                await message.channel.send("Invalid product")

        elif (message.content.startswith('$signal remove')
              or message.content.startswith("$signal rem")):
            try:
                self.trader.remove_product(message.content.split(" ")[2])
                await message.channel.send("Product removed!")
            except IndexError:
                await message.channel.send(
                    "Please add the product symbol and ensure that it is separated from the command using a space."
                )
            except ValueError:
                await message.channel.send(
                    "This product was not added before ;-;")

        elif (message.content.startswith('$signal products')):
            await message.channel.send(self.trader.get_products_str())

        #****end MACDTrader Commands****

        #****start 8Ball Commands****

        elif (message.content.startswith(self._8_BALL_BALL_CMD)):
            num = 0

            if (len(self.user_added) > 0):
                num = random.randrange(4)
            else:
                num = random.randrange(3)

            response_list = []

            if (num == 0):
                response_list = self.responses_affirmative
            elif (num == 1):
                response_list = self.responses_non_committal
            elif (num == 2):
                response_list = self.responses_negative
            elif (num == 3):
                response_list = self.user_added

            await message.channel.send(response_list[random.randrange(
                len(response_list))])

        elif (message.content.startswith(self._8_BALL_ADD_CMD)):
            self.user_added.append(message.content[len(self._8_BALL_ADD_CMD):])
            await message.channel.send("Response added!")

        elif (message.content.startswith(self._8_BALL_REM_CMD)):
            try:
                self.user_added.remove(
                    message.content[len(self._8_BALL_REM_CMD):])
                await message.channel.send("Response removed!")
            except ValueError:
                await message.channel.send(
                    "You are trying to remove a preset response or your response was never added"
                )

        elif (message.content.startswith(self._8_BALL_RESPONSES_CMD)):
            str = ""

            for response in (self.responses_affirmative +
                             self.responses_non_committal +
                             self.responses_negative + self.user_added):
                str = str + response + "\n"

            await message.channel.send(str)

        #****end 8Ball Commands****
