from worlds.LauncherComponents import Component, Type, components, launch, icon_paths

from .world import PAYDAY2World as PAYDAY2World

def run_client(*args: str) -> None:
    from .client import launch_client
    launch(launch_client, name="PAYDAY 2: Criminal Dawn Client", args=args)

components.append(
    Component(
        "PAYDAY 2: Criminal Dawn Client",
        func=run_client,
        game_name="PAYDAY 2",
        component_type=Type.CLIENT,
        supports_uri=True,
        description="Launch the client for the Criminal Dawn mod.",
        icon="PAYDAY 2: Criminal Dawn"
    )
)

icon_paths["PAYDAY 2: Criminal Dawn"] = f"ap:{__name__}/pd2-logo.png"