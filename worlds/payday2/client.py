from CommonClient import CommonContext, ClientCommandProcessor, server_loop, get_base_parser, handle_url_arg, logger
import Utils, asyncio, colorama, logging, json, os, math, shutil
from . import PAYDAY2World
from . import items
from .item_types import itemType, itemData
from collections.abc import Sequence
from .locations import LOCATION_NAME_TO_ID

from BaseClasses import ItemClassification as IC
from NetUtils import ClientStatus

path = "."

def load_json_file(fileName: str) -> dict:
    try:
        with open(fileName, 'r', encoding='utf-8') as file:
            return json.load(file)
    except Exception as e:
        return {}

class PAYDAY2CommandProcessor(ClientCommandProcessor):

    def _score(self):
        """Displays your current score."""
        if isinstance(self.ctx, PAYDAY2Context):
            logger.info(f"Current score: {1}")

# scribble likes to write
class scribble:
    def __init__(self, path):
        self.data = {}
        self.path = path
        print(f"Scribble is scribing {self.path}...")

    def run(self, key):
        try:
            self.data[key] += 1
        except KeyError:
            self.data[key] = 1
        with open(self.path, "w+") as f:
            json.dump(self.data, f)

    def writeSeed(self, seed):
        self.data["seed"] = seed
        with open(self.path, "w+") as f:
            json.dump(self.data, f)

# scrungle likes to watch
class scrungle:
    def __init__(self, path, context):
        self.context = context
        self.path = path

    # function derived from Project Diva APWorld
    async def watch(self):
        print(f"Scrungle is watching {self.path}...")
        modSave = load_json_file(self.path)
        prevScore = 0
        lastModTime = os.path.getmtime(self.path) if os.path.isfile(self.path) else 0.0
        lastModTime = 0

        try:
            while True:
                if os.path.isfile(self.path):
                    modTime = os.path.getmtime(self.path)

                    if modTime > lastModTime:
                        lastModTime = modTime

                        try:
                            modSave = load_json_file(self.path)
                            score = modSave["game"]["score"] / 100

                            # Has the game been won?
                            try:
                                modSave["game"]["victory"]
                                await self.send_msgs([{"cmd": "StatusUpdate", "status": ClientStatus.CLIENT_GOAL}])
                            except:
                                pass

                            # Not in the except so people that play without autorelease can continue getting checks
                            if score > prevScore:
                                await self.context.score_check(score)
                                prevScore = score

                        except (FileNotFoundError, json.decoder.JSONDecodeError) as e:
                            print(f"Couldn't load apyday2.txt: {e}")

                        try:
                            safehouseDict = modSave["safehouse"]
                            if safehouseDict != []:
                                await self.context.safehouse_check(safehouseDict)
                        except Exception as e:
                            print(f"Couldn't load apyday2.txt: {e}")

                await asyncio.sleep(1)

        except asyncio.CancelledError:
            print("Scrungle stopped watching. Scrungle bored.")

class PAYDAY2Context(CommonContext):
    game = 'PAYDAY 2'
    command_processor = PAYDAY2CommandProcessor
    items_handling = 0b111

    def __init__(self, server_address, password):
        super().__init__(server_address, password)
        self.initialized = False
        self.score = 0

    async def server_auth(self, password_requested: bool = False):
        if password_requested and not self.password:
            await super(PAYDAY2Context, self).server_auth(password_requested)
        await self.get_username()
        await self.send_connect()

    def on_package(self, cmd: str, args: dict):
        if cmd == 'Connected':
            self.on_connected(args)
        elif cmd == "ReceivedItems":
            self.on_received_items(args)

    def on_connected(self, args: dict):
        version = PAYDAY2World.world_version.as_simple_string()

        # Error checking
        if version != args['slot_data']['server_version']:
            logger.info(f"WARNING: Server ({args['slot_data']['server_version']}) and client ({version}) are using different versions!")

        self.path = os.path.dirname(PAYDAY2World.settings.payday2_path) + "/mods/saves/"
        self.scribble = scribble(self.path + "apyday2-client.txt")

        if not os.path.isfile(PAYDAY2World.settings.payday2_path):
            logger.error('ERROR: Scrungle no find payday2_win32_release.exe.\nScrungle kindly requests that you remove payday2_path from host.yaml')
            Utils.async_start(self.disconnect())

        elif not os.path.exists(self.path):
            logger.error('ERROR: Scrungle no find /mods/saves.\nScrungle want you to check that you have SuperBLT installed.')
            Utils.async_start(self.disconnect())

        # Check seed
        try:
            modSave = load_json_file(self.path + "apyday2.txt")
            modSeed = modSave["game"]["seed"]

        except KeyError as e:
            self.scribble.writeSeed(args['slot_data']['seed_name'])
            print(f"Couldn't find seed, wrote to client file")

        except (FileNotFoundError, json.decoder.JSONDecodeError) as e:
            print(f"Couldn't load apyday2.txt: {e}")

        ### MESS OF SAVE CHECKING STARTS HERE

        try:
            if modSeed != args['slot_data']['seed_name']:

                # Check operating system, if Windows we can handle different saves ourselves
                if os.name == "--nt": # DOESN'T ACTUALLY WORK SO I DISABLED IT
                    print("Seed mismatch! Fixing...")
                    abortFix = False

                    # Game save handler
                    paydaySaves = (os.getenv("LOCALAPPDATA").replace("\\", "/") + "/PAYDAY 2/saves/")
                    steamIds = [folder for folder in os.listdir(paydaySaves)
                                if os.path.isdir(os.path.join(paydaySaves, folder))]

                    saveCount = 0
                    for folder in steamIds:
                        if "save041.sav" in os.listdir(paydaySaves + folder):
                            saveCount += 1
                            saveDir = folder + "/"

                            if saveCount > 1:
                                logger.error("ERROR: Too much uncertainty to restore previous save.\n"
                                       "Reset your save manually with the following steps:\n"
                                       "1) Launch PAYDAY 2.\n"
                                       "2) Click 'OPTIONS'.\n"
                                       "3) Click 'ADVANCED'.\n"
                                       "4) Click 'RESET ACCOUNT PROGRESSION'.\n"
                                       "5) Click 'YES' and wait for the game to reload.\n"
                                       "You can reconnect after the game reloads.")
                                Utils.async_start(self.disconnect())
                                break

                        else:
                            logger.error("ERROR: No game save found to resume from.\n"
                                   "Reset your save manually with the following steps:\n"
                                   "1) Launch PAYDAY 2.\n"
                                   "2) Click 'OPTIONS'.\n"
                                   "3) Click 'ADVANCED'.\n"
                                   "4) Click 'RESET ACCOUNT PROGRESSION'.\n"
                                   "5) Click 'YES' and wait for the game to reload.\n"
                                   "You can reconnect after the game reloads.")
                            Utils.async_start(self.disconnect())

                    if saveCount == 1:
                        if os.path.isdir(paydaySaves + saveDir + "apyday2_backups"):
                            fileFound = True

                            for file in os.listdir(paydaySaves + saveDir + "apyday2_backups"):
                                if file == args['slot_data']['seed_name']:
                                    print("Found previous save data, restoring")

                                    # Copy current save to backup folder, copy old save back to continue playing
                                    shutil.copy(paydaySaves + saveDir + "save041.sav", paydaySaves + saveDir + "apyday2_backups/" + modSeed)
                                    shutil.copy(paydaySaves + saveDir + "apyday2_backups/" + args['slot_data']['seed_name'], paydaySaves + saveDir + "save041.sav")
                                    break
                                else:
                                    fileFound = False

                            if not fileFound or len(os.listdir(paydaySaves + saveDir + "apyday2_backups")) == 0:
                                print("No existing save found. Backing up")
                                shutil.copy(paydaySaves + saveDir + "save041.sav", paydaySaves + saveDir + "apyday2_backups/" + modSeed)
                                os.remove(paydaySaves + saveDir + "save041.sav")

                        else:
                            os.mkdir(paydaySaves + saveDir + "apyday2_backups")
                            print("Created backup save folder.")

                            # Copy save to backup folder, using the seed as the file name
                            shutil.copy(paydaySaves + saveDir + "save041.sav", paydaySaves + saveDir + "apyday2_backups/" + modSeed)
                            os.remove(paydaySaves + saveDir + "save041.sav")


                    if saveCount == 1:
                        # apyday2.txt handler
                        if os.path.isdir(self.path + "/apyday2_backups"):
                            fileFound = True

                            for file in os.listdir(self.path + "/apyday2_backups"):
                                if file == args['slot_data']['seed_name']:
                                    print("Found previous save data, restoring")
                                    # Copy current save to backup folder, copy old save back to continue playing
                                    shutil.copy(self.path + "apyday2.txt", self.path + "/apyday2_backups/" + modSeed)
                                    shutil.copy(self.path + "/apyday2_backups/" + args['slot_data']['seed_name'], self.path + "apyday2.txt")
                                    logger.info("Found and restored previous save.\n"
                                                "Old saves are in the following folders:\n"
                                                ".../PAYDAY 2/mods/saves/apyday2_backups\n"
                                                f"%LOCALAPPDATA%/PAYDAY 2/{saveDir}apyday2_backups\n"
                                                "Remember to clean them out from time to time!")
                                    break
                                else:
                                    fileFound = False
                            if not fileFound or len(os.listdir(self.path + "/apyday2_backups")) == 0:
                                print("No existing save found. Backing up")
                                shutil.copy(self.path + "apyday2.txt", self.path + "/apyday2_backups/" + modSeed)
                                os.remove(self.path + "apyday2.txt")
                                logger.info("Backed up previous save data for future sessions.\n"
                                            "Saves were moved to the following folders:\n"
                                            ".../PAYDAY 2/mods/saves/apyday2_backups\n"
                                            f"%LOCALAPPDATA%/PAYDAY 2/{saveDir}apyday2_backups\n"
                                            "Remember to clean them out from time to time!")

                        else:
                            os.mkdir(self.path + "/apyday2_backups")
                            print("Created backup save folder.")
                            # Copy save to backup folder, using the seed as the file name
                            shutil.copy(self.path + "apyday2.txt", self.path + "/apyday2_backups/" + modSeed)
                            os.remove(self.path + "apyday2.txt")
                            logger.info("Backed up previous save data for future sessions.\n"
                                        "Saves were moved to the following folders:\n"
                                        ".../PAYDAY 2/mods/saves/apyday2_backups\n"
                                        f"%LOCALAPPDATA%/PAYDAY 2/{saveDir}apyday2_backups\n"
                                        "Remember to clean them out from time to time!")

                # System isn't Windows, don't attempt anything
                else:
                    logger.error("ERROR: Your current save was made on a different seed.\n"
                                 "Only one multiworld can currently be played at a time.\n\n"
                                 "Delete your save with the following steps:\n"
                                 "1) Launch PAYDAY 2.\n"
                                 "2) Click 'OPTIONS'.\n"
                                 "3) Click 'ADVANCED'.\n"
                                 "4) Click 'RESET ACCOUNT PROGRESSION'.\n"
                                 "5) Click 'YES' and wait for the game to reload.\n\n"
                                 "You can reconnect after the game reloads.")
                    Utils.async_start(self.disconnect())

        except:
            pass

        ### MESS OF SAVE CHECKING HAS ENDED. THANK GOD

        self.scrungle = scrungle(self.path + "apyday2.txt", self)
        scrungle_task = asyncio.create_task(self.scrungle.watch(), name='scrungle')

        self.itemDict = items.itemDict

    def on_received_items(self, args: dict):
        # for entry in self.items_received:
        for entry in args["items"]:
            try:
                item = self.itemDict[entry.item]
            except KeyError as e:
                logger.error(e)
                logger.error(f"KEY ERROR: {entry.item}")
                continue
            except Exception as e:
                logger.error(f"FATAL ERROR: {entry.item}")
                continue

            self.scribble.run(item.name)

    def getN(self, score):
        return math.floor((math.sqrt(1 + 8 * (score)) - 1) / 2)

    async def score_check(self, score):
        try:
            #Solve your triangular number every time because you refuse to just save and read n.
            print(score)
            n = self.getN(score)
            print(n)
            for i in range(1, n + 1):
                await self.check_locations([i])

            self.score = score
                
        except KeyError as e:
            logger.error(e)

    async def safehouse_check(self, safehouseDict):
        try:
            safehouseIdToName = {
                "terry": "Scarface's Room",
                "russian": "Dallas' Office",
                "old_hoxton": "Hoxton's Files",
                "clover": "Clover's Surveillance Center",
                "myh": "Duke's Gallery",
                "sydney": "Sydney's Studio",
                "american": "Houston's Workshop",
                "wild": "Rust's Corner",
                "ecp": "h3h3",
                "joy": "Joy's Van",
                "bonnie": "Bonnie's Gambling Den",
                "dragon": "Jiro's Lounge",
                "dragan": "Dragan's Gym",
                "jimmy": "Jimmy's Bar",
                "livingroom": "Common Rooms",
                "max": "Sangres' Cave",
                "spanish": "Chains' Weapons Workshop",
                "bodhi": "Bodhi's Surfboard Workshop",
                "jacket": "Jacket's Hangout",
                "sokol": "Sokol's Hockey Gym",
                "vault": "Vault",
                "german": "Wolf's Workshop",
                "jowi": "Wick's Shooting Range"
            }

            for key, tier in safehouseDict.items():
                for i in range(2,tier+1):
                    Id = LOCATION_NAME_TO_ID[f"{safehouseIdToName[key]} - Tier {i}"]
                    await self.check_locations([Id])

        except KeyError as e:
            logger.error(e)

    def run_gui(self):
        from kvui import GameManager

        class PAYDAY2Manager(GameManager):
            logging_pairs = [
                ("Client", "Archipelago")
            ]
            base_title = self.game + " Client"

        self.ui = PAYDAY2Manager(self)
        self.ui_task = asyncio.create_task(self.ui.async_run(), name="UI")

def launch_client(*args: Sequence[str]):
    Utils.init_logging('PAYDAY2Client')
    logging.getLogger().setLevel(logging.INFO)

    async def main(args):
        ctx = PAYDAY2Context(args.connect, args.password)
        ctx.server_task = asyncio.create_task(server_loop(ctx), name='ServerLoop')

        if Utils.gui_enabled:
            ctx.run_gui()
        ctx.run_cli()

        await ctx.exit_event.wait()
        await ctx.shutdown()

    parser = get_base_parser()
    parser.add_argument("--name", default=None, help="Slot Name to connect as.")
    parser.add_argument("url", nargs="?", help="Archipelago connection url")

    launch_args = handle_url_arg(parser.parse_args(args))

    colorama.just_fix_windows_console()

    asyncio.run(main(launch_args))
    colorama.deinit()