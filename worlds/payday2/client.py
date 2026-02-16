from CommonClient import CommonContext, ClientCommandProcessor, server_loop, get_base_parser, handle_url_arg, gui_enabled, logger
import Utils, asyncio, colorama, logging, json, os, math
from .version import version
from . import PAYDAY2World
from . import items
from .item_types import itemType, itemData
from collections.abc import Sequence

from BaseClasses import ItemClassification as IC
from NetUtils import ClientStatus

path = "."

def load_json_file(file_name: str) -> dict:
    try:
        with open(file_name, 'r', encoding='utf-8') as file:
            return json.load(file)
    except Exception as e:
        return {}

class PAYDAY2CommandProcessor(ClientCommandProcessor):

    def _score(self):
        """Prints a countdown."""
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

# scrungle likes to watch
class scrungle:
    def __init__(self, path, context):
        self.context = context
        self.path = path

    # function derived from Project Diva APWorld
    async def watch(self):
        print(f"Scrungle is watching {self.path}...")
        apd2_data = load_json_file(self.path)
        score = apd2_data["game"]["score"] / 100
        await self.context.check(score)
        lastModTime = os.path.getmtime(self.path) if os.path.isfile(self.path) else 0.0
        try:
            while True:
                await asyncio.sleep(1)
                if os.path.isfile(self.path):
                    modTime = os.path.getmtime(self.path)
                    if modTime > lastModTime:
                        lastModTime = modTime
                        try:
                            apd2_data = load_json_file(self.path)
                            score = apd2_data["game"]["score"] / 100
                            await self.context.check(score)

                            #print(apd2_data)
                        except (FileNotFoundError, json.decoder.JSONDecodeError) as e:
                            print(f"Couldn't load apyday2.txt: {e}")
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
        if version != args['slot_data']['version']:
            logger.error("Server and Client APWorld versions do not match.")
        else:
            logger.info(f"Client version {version}")

        self.path = os.path.dirname(PAYDAY2World.settings.payday2_path) + "/mods/saves/"

        if not os.path.isfile(PAYDAY2World.settings.payday2_path):
            logger.error('Scrungle no find payday2_win32_release.exe - Scrungle kindly requests that you remove path from host.yaml')

        if not os.path.exists(self.path):
            logger.error('Scrungle no find /mods/saves. Scrungle want you to check that you have SuperBLT installed.')

        self.scribble = scribble(self.path + "apyday2-client.txt")
        self.scrungle = scrungle(self.path + "apyday2.txt", self)
        scrungle_task = asyncio.create_task(self.scrungle.watch(), name='scrungle')

        self.itemDict = items.itemDict

        ClientInitialise.initialise(self, self.itemDict)

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
                logger.error(f"FATAL KEY ERROR: {entry.item}")
                continue

            sender = "You" if entry.player == self.slot else f"Player {entry.player}"
            # logger.info(f"From: {sender} | Item: {item.name}")

            self.scribble.run(item.name)

            if item.type == itemType.progression:
                pass
                #Remove pass and edit the correct line in your json

    def getN(self, score):
        return math.floor((math.sqrt(1 + 8 * (score)) - 1) / 2)

    async def check(self, score):
        try:
            #Solve your triangular number every time because you refuse to just save and read n.
            print(score)
            n = self.getN(score) #This needs to be the solving part, fuck you.
            print(n)
            for i in range(1, n + 1):
                #triangle = n * (n+1) / 2 #Because you refuse to save locations as n, we now need to make triangular numbers again, right after solving one.
                await self.check_locations([i])

            self.score = score

            #This line is for victory
            #await self.send_msgs([{"cmd": "StatusUpdate", "status": ClientStatus.CLIENT_GOAL}])
                
        except KeyError as e:
            logger.error(e)

    def run_gui(self):
        from kvui import GameManager

        class PAYDAY2Manager(GameManager):
            logging_pairs = [
                ("Client", "Archipelago")
            ]
            base_title = "Archipelago " + self.game + " Client"

        self.ui = PAYDAY2Manager(self)
        self.ui_task = asyncio.create_task(self.ui.async_run(), name="UI")

class ClientInitialise:

    @classmethod
    def initialise(self, context, itemDict):
        scribble = context.scribble


def launch_client(*args: Sequence[str]):
    Utils.init_logging('PAYDAY2Client')
    logging.getLogger().setLevel(logging.INFO)

    async def main(args):
        ctx = PAYDAY2Context(args.connect, args.password)
        ctx.server_task = asyncio.create_task(server_loop(ctx), name='ServerLoop')

        if gui_enabled:
            ctx.run_gui()
        ctx.run_cli()

        await ctx.exit_event.wait()
        ctx.server_address = None
        await ctx.shutdown()

    parser = get_base_parser()
    parser.add_argument("--name", default=None, help="Slot Name to connect as.")
    parser.add_argument("url", nargs="?", help="Archipelago connection url")

    launch_args = handle_url_arg(parser.parse_args(args))

    colorama.just_fix_windows_console()

    asyncio.run(main(launch_args))
    colorama.deinit()