# Bulletin-Board

Pinboard bot, but this time better! Originally made for RDL but it's public source!
Supports multiple-guilds.

Requires Disnake >= 2.4.x

Requires Permissions:
View Messages
Manage Messages
Manage Webhooks

Simply extract the files, place your token in a 'token.txt' file in the root directory and hey presto you've got a bot!
To run, simply run main.py in your favourite package management software.

COMMANDS:

/setloggingchannel #channel
When set, the bot will log all actions done to this channel.

/setdefaultbulletin #channel
When set, registered channel overflow pins will go here by default.

/register #channel #output-channel (optional)
When set for a channel, when a pin would bring a channel up to the 50 pin limit, the bot will instead unpin something else and post that comment instead.

/lock message_url
Locks a message to the top of the pin list in a specified channel. Up to 10 messages can be locked to the top, however Discord will start ratelimiting the bot after about two, so it's recommended to keep this short per-channel.
Unlocks a message from the top of the pin list, if the message is already in the list.

/list #channel
Gives the URLs of all the Locked Pins in a specified channel.

As with all of my bots, this bot is licensed under AGPL3.

    Copyright(c) OblivionCreator - 2022

    This program is free software: you can redistribute it and/or modify
    it under the terms of the GNU Affero General Public License as
    published by the Free Software Foundation, either version 3 of the
    License, or (at your option) any later version.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU Affero General Public License for more details.

    You should have received a copy of the GNU Affero General Public License
    along with this program.  If not, see <https://www.gnu.org/licenses/>.
