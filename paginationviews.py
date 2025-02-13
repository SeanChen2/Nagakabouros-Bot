import discord
from table2ascii import table2ascii, Alignment
from abc import ABC, abstractmethod
from random import choice
from data import ILLAOI_QUOTES

# Abstract class for any view that requires pagination
class PaginationView(ABC, discord.ui.View):
    
    def __init__(self):
        super().__init__()
        self.current_page = 1
        self.items_per_page = 20
        self.data = []

    async def send(self, message):
        self.message = await message.channel.send(view=self)
        await self.update_message(self.data[:self.items_per_page])

    async def update_buttons(self):
        if self.current_page <= 1:
            self.back_button.disabled = True
        else:
            self.back_button.disabled = False

        if self.current_page >= int(len(self.data) / self.items_per_page) + 1:
            self.next_button.disabled = True
        else:
            self.next_button.disabled = False

    @discord.ui.button(label="Back", style=discord.ButtonStyle.primary)
    async def back_button(self, interaction, button):
        await interaction.response.defer()
        self.current_page -= 1
        
        # Slice out the current page's data and edit the leaderboard message
        until_item = self.current_page * self.items_per_page
        from_item = until_item - self.items_per_page
        
        await self.update_message(self.data[from_item:until_item])


    @discord.ui.button(label="Next", style=discord.ButtonStyle.primary)
    async def next_button(self, interaction, button):
        await interaction.response.defer()
        self.current_page += 1
        
        # Slice out the current page's data and edit the leaderboard message
        until_item = self.current_page * self.items_per_page
        from_item = until_item - self.items_per_page
        
        await self.update_message(self.data[from_item:until_item])


    # This method should generate a viewable form of content to be sent in Discord. This could be a plain message or embed.
    @abstractmethod
    def generate_content(self, data):
        pass


    # This method should call update_buttons() and edit the message with new content
    @abstractmethod
    def update_message(self, data):
        pass


# Concrete class for the champion leaderboard view
class LeaderboardView(PaginationView):

    # Generate the ASCII table of champions
    def generate_content(self, data):
        return "```LoL Champion Leaderboard\n----------------------------\n\n" + table2ascii(
            header=["Rank", "Champion", "Role", "Tier", "Win rate", "Pick rate", "Ban rate"],
            body=data,
            alignments= [Alignment.LEFT, Alignment.LEFT, Alignment.LEFT, Alignment.CENTER, Alignment.CENTER, Alignment.CENTER, Alignment.CENTER]
        ) + "```"


    async def update_message(self, data):
        await self.update_buttons()
        await self.message.edit(content=self.generate_content(data), view=self)


class CounterView(PaginationView):

    def setup(self, champ_name, champ_role, data):
        self.champ_name = champ_name
        self.champ_role = champ_role
        self.data = data

    # Generate the embed of counter matchups for the requested champion
    def generate_content(self, data):
            
            # Create a string from the counter data (name, win rate)
            counter_str = ""
            
            for counter in data:
                counter_str += f"**{counter[0]}** - {counter[1]}\n"
            
            counter_embed = discord.Embed(
                colour=discord.Color.brand_green(),
                title=f"LoL Counters for {self.champ_name} {self.champ_role}",
                description=counter_str
            )

            counter_embed.set_footer(text=choice(ILLAOI_QUOTES))
            counter_embed.set_author(name="Nagakabouros")

            return counter_embed
    

    async def update_message(self, data):
        await self.update_buttons()
        await self.message.edit(embed=self.generate_content(data), view=self)
