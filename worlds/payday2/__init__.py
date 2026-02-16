from worlds.LauncherComponents import Component, Type, components, launch, icon_paths

from .world import PAYDAY2World as PAYDAY2World

def run_client(*args: str) -> None:
    from .client import launch_client
    launch(launch_client, name="PAYDAY 2 Client", args=args)

components.append(
    Component(
        "PAYDAY 2 Client",
        func=run_client,
        game_name="PAYDAY 2",
        component_type=Type.CLIENT,
        supports_uri=True,
        description="Launches the PAYDAY 2 client.",
        icon="PAYDAY 2"
    )
)

icon_paths["PAYDAY 2"] = f"ap:{__name__}/pd2-logo.png"