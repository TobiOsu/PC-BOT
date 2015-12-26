import discord
import requests
import sys

client = discord.Client()

if len(sys.argv) < 3:
    print("usage: " + sys.argv[0] + " <email> <password>")
    sys.exit(0)

client.login(sys.argv[1], sys.argv[2])

osu_api = input("Enter a valid osu! API key for osu! functions (enter nothing to disable): ")  # API Key for osu!

usage = {
    "!pcbot": "display commands",
    "!google <query ...>": "search the web",
    "!display <query ...>": "search the web for images",
    "!lucky <query ...>": "retrieve a link",
    "!profile <user>": "sends link to osu! profile",
    "!osu <profile> <stat>": "displays a profile stat (may break some things",
    "!rank <profile>:": "displays various stats for profile"
}


# Return length of longest keyword for printing
def longest_cmd():
    cmd_len = 0
    for k, _ in usage.items():
        if len(k) > cmd_len:
            cmd_len = len(k)
    return cmd_len


def handle_command(message):
    args = message.content.split()
    send_message = ""

    # Avoid these comments
    if len(args) < 1:
        return

    if args[0] == "!google":  # Search google
        if len(args) > 1:
            send_message = "http://www.google.com/search?q=" + "+".join(args[1:])
        else:
            send_message = ":thumbsdown:"
    elif args[0] == "!display":  # Link to images
        if len(args) > 1:
            send_message = "http://www.google.com/search?q=" + "+".join(args[1:]) + "&tbm=isch"
        else:
            send_message = ":thumbsdown:"
    elif args[0] == "!lucky":  # Return a link from lucky
        if len(args) > 1:
            to_get = r"http://www.google.com/search?q=" + r"+".join(args[1:]) + r"&btnI"
            result = requests.get(to_get, allow_redirects="false")
            send_message = result.url
        else:
            send_message = ":thumbsdown:"
    elif args[0] == "!profile":  # Link to osu! profile
        if len(args) > 1:
            send_message = r"http://osu.ppy.sh/u/" + str(args[1])
        else:
            send_message = ":thumbsdown:"
    elif args[0] == "!osu":  # Give osu! profile stat
        if len(args) > 2:
            if osu_api:
                to_get = r"http://osu.ppy.sh/api/get_user?k=" + osu_api + r"&u=" + args[1]
                osu_stats_request = requests.get(to_get)
                osu_stats = osu_stats_request.json()[0]
                try:
                    send_message = "**%s** for %s: `%s`" % (args[2], args[1], osu_stats[args[2]])
                except KeyError:
                    send_message = "No such key. :thumbsdown:"
            else:
                send_message = "This command is disabled. :thumbsdown:"
        else:
            send_message = ":thumbsdown:"
    elif args[0] == "!rank":  # Give a list of osu! profile stats
        if len(args) > 1:
            if osu_api:
                to_get = r"http://osu.ppy.sh/api/get_user?k=" + osu_api + r"&u=" + args[1]
                osu_stats_request = requests.get(to_get)
                osu_stats = osu_stats_request.json()[0]
                send_message = "*Stats for %s* (%s) ```" % (
                    osu_stats["username"],
                    osu_stats["user_id"]
                )
                send_message += "Performance:   %spp (#%s) /#%s" % (
                    osu_stats["pp_raw"],
                    osu_stats["pp_rank"],
                    osu_stats["pp_country_rank"]
                )
                send_message += "\nAccuracy:      %0.6f" % float(osu_stats["accuracy"])
                send_message += "\n               %s SS %s S %s A" % (
                    osu_stats["count_rank_ss"],
                    osu_stats["count_rank_s"],
                    osu_stats["count_rank_a"]
                )
                send_message += "\nPlaycount:     " + osu_stats["playcount"]
                send_message += "```"
            else:
                send_message = "This command is disabled. :thumbsdown:"
        else:
            send_message = ":thumbsdown:"
    elif args[0] == "!pcbot":  # Show help
        send_message = "Commands: ```"
        space_len = longest_cmd() + 4
        for k, v in usage.items():
            send_message += "\n" + k + " "*(space_len - len(k)) + v
        send_message += "```"

    return send_message


@client.event
def on_message(message):
    send_message = handle_command(message)
    if send_message:
        client.send_message(message.channel, message.author.mention() + " " + send_message)


@client.event
def on_message_edit(before, after):
    send_message = handle_command(after)
    if send_message:
        client.send_message(after.channel, after.author.mention() + " " + send_message)


@client.event
def on_ready():
    print('\nLogged in as')
    print(client.user.name)
    print(client.user.id)
    print('------')


client.run()
