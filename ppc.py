#!/usr/bin/env python3
import os
print("  |  |")
print(" \\____/\n\n")
print("Welcome to the Palgrave Package Center!\nDo you want to (I)nstall or (U)ninstall a package? (or (Q)uit PPC) ",end="")
x = input()
x = x.lower()
if x == "i":
    print("OK! What's the name of the package? (user/repo format, should be on github and branch main should exist)")
    pkg = input()
    print("[",end="")
    try:
        import requests
    except ModuleNotFoundError:
        print("\nPPC: error! please pip install requests")
        quit()
    print("#",end="")
    ppcdotjson = requests.get("https://raw.githubusercontent.com/{}/main/ppc.json".format(pkg))
    print("#]")
    import json
    ppcdotjson = ppcdotjson.text
    ppcdotjson = json.loads(ppcdotjson)
    print("You're about to install {} by {}. Is that right? (Y/n) ".format(ppcdotjson["name"],ppcdotjson["author"]),end="")
    y = input()
    if y.lower() != "n":
        commands = requests.get("https://raw.githubusercontent.com/{}/main/commands.json".format(pkg))
        with open("{}/InstantPalgrave/commands.json".format(os.environ.get("HOME")),"w") as commandfile:
            commandfile.write(commands.text)
        print("All done! Installed successfully.")
    else:
        print("Cancelled, nothing has been installed.")
elif x == "u":
    print("[",end="")
    z = open("commands.json","w")
    z.write("{{}}")
    z.close()
    print("#]\nPackages have been uninstalled.")
