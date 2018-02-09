# Created by Thomas Jones on 19/06/2017 - thomas@tomtecsolutions.com
# permaban.py, a plugin for minqlx to thoroughly perma-ban players.
# This plugin is released to everyone, for any purpose. It comes with no warranty, no guarantee it works, it's released AS IS.
# You can modify everything, except for lines 1-4 and the !tomtec_versions code. They're there to indicate I whacked this together originally. Please make it better :D

import minqlx

class permaban(minqlx.Plugin):
    def __init__(self):
        self.add_hook("player_connect", self.handle_player_connect, priority=minqlx.PRI_HIGH)

        self.add_command("permaban", self.cmd_permaban, 5, usage="<id>/<steam_id>")
        self.add_command("unpermaban", self.cmd_unpermaban, 5, usage="<id>/<steam_id>")
        self.add_command("tomtec_versions", self.cmd_showversion)

        self.plugin_version = "1.5"



    def cmd_permaban(self, player, msg, channel):
        if len(msg) < 2:
            return minqlx.RET_USAGE
        
        try:
            ident = int(msg[1])
            target_player = None
            if 0 <= ident < 64:
                steam_id = self.player(int(msg[1])).steam_id
                player_name = self.player(int(msg[1])).name
            else:
                player_name = ident
                steam_id = ident
        except ValueError:
            channel.reply("Invalid ID. Use either a client ID or a SteamID64.")
            return
        except minqlx.NonexistentPlayerError:
            channel.reply("Invalid client ID. Use either a client ID or a SteamID64.")
            return

        self.db.set("minqlx:players:{}:permabanned".format(steam_id), "1")

        if self.player(steam_id):
            self.kick(self.player(steam_id), "You have been permanently banned.")

        channel.reply("{}^7 has been permanently banned.".format(player_name))
        
    def cmd_unpermaban(self, player, msg, channel):
        if len(msg) < 2:
            return minqlx.RET_USAGE
        
        try:
            ident = int(msg[1])
            target_player = None
            if 0 <= ident < 64:
                steam_id = self.player(int(msg[1])).steam_id
                player_name = self.player(int(msg[1])).name
            else:
                player_name = ident
                steam_id = ident
        except ValueError:
            channel.reply("Invalid ID. Use either a client ID or a SteamID64.")
            return
        except minqlx.NonexistentPlayerError:
            channel.reply("Invalid client ID. Use either a client ID or a SteamID64.")
            return

        self.db.set("minqlx:players:{}:permabanned".format(steam_id), "0")

        if self.player(steam_id):
            self.kick(self.player(steam_id), "You have been unbanned.")

        channel.reply("{}^7 has been unbanned.".format(player_name))
        
    def handle_player_connect(self, player):
        is_banned_id = self.is_banned(player)

        if is_banned_id:
            if (is_banned_id == player.steam_id):
                return "Your account is permabanned.\n"
            else:
                self.db.set("minqlx:players:{}:permabanned".format(is_banned_id), "1")    # make sure every single associated account is banned
                self.db.set("minqlx:players:{}:permabanned".format(player.steam_id), "1") # make sure the new account is banned
                return "Your associated accounts are permabanned.\n"


    def is_banned(self, player):
        ip_list = list(self.db.smembers("minqlx:players:{}:ips".format(player.steam_id)))
        ip_list.append(player.ip)

        if self.db.get("minqlx:players:{}:permabanned".format(player.steam_id)) == "1":
            return player.steam_id
        
        for ip in ip_list:
            for steam_id in list(self.db.smembers("minqlx:ips:{}".format(ip))):
                if self.db.get("minqlx:players:{}:permabanned".format(steam_id)) == "1":
                    return steam_id
                
        return False

        
    def cmd_showversion(self, player, msg, channel):
        channel.reply("^4permaban.py^7 - version {}, created by Thomas Jones on 19/06/2017.".format(self.plugin_version))
