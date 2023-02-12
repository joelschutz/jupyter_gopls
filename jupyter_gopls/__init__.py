from ._version import __version__
import json
from jupyter_lsp.manager import LanguageServerManager
from jupyterlab.labapp import LabApp
from .dispatcher import ShadowGoFileSystem

def _jupyter_labextension_paths():
    return [{
        "src": "labextension",
        "dest": "jupyter-gopls"
    }]


def _jupyter_server_extension_points():
    return [{
        "module": "jupyter_gopls"
    }]

async def initialize(manager :LanguageServerManager):  # pragma: no cover
    """Perform lazy initialization."""

    if await manager.ready():
        session = manager.sessions.get("gopls")
    
        language_servers = manager.language_servers
        manager.log.error(
            "[gopls] The following Language Servers will be available: {}".format(
                json.dumps(language_servers, indent=2, sort_keys=True)
            )
        )

        # Adds new file dispatcher
        session.file_dispatcher = ShadowGoFileSystem()

def _load_jupyter_server_extension(nbapp: LabApp):
    """create a LanguageServerManager and add handlers"""

    def start_init(change):
        nbapp.log.error(change)
        nbapp.io_loop.call_later(0, initialize, change["new"])

    nbapp.observe(start_init, names=["language_server_manager"])


# For backward compatibility with notebook server - useful for Binder/JupyterHub
load_jupyter_server_extension = _load_jupyter_server_extension

