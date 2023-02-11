from ._version import __version__
import json
# from .handlers import setup_handlers
# from jupyter_lsp import lsp_message_listener
# from jupyter_lsp.paths import file_uri_to_path
from jupyter_lsp.manager import LanguageServerManager
from jupyterlab.labapp import LabApp
import traitlets

def extract_or_none(obj, path):
    for crumb in path:
        try:
            obj = obj[crumb]
        except (KeyError, TypeError):
            return None
    return obj

def _jupyter_labextension_paths():
    return [{
        "src": "labextension",
        "dest": "jupyter-gopls"
    }]


def _jupyter_server_extension_points():
    return [{
        "module": "jupyter_gopls"
    }]


def _load_jupyter_server_extension(server_app: LabApp):
    """Registers the API handler to receive HTTP requests from the frontend extension.

    Parameters
    ----------
    server_app: jupyterlab.labapp.LabApp
        JupyterLab application instance
    """
    # @lsp_message_listener("client")
    # async def my_listener(scope, message, language_server, manager:LanguageServerManager):
    #     a = manager.language_servers['go-language-server-implementation']
    #     uri = extract_or_none(message, ["params", "textDocument", "uri"])
    #     # print("received a {} {} message from {}".format(
    #     #   scope, message, file_uri_to_path(uri)
    #     # ))
    #     return uri
    # setup_handlers(server_app.web_app)
    name = "jupyter_gopls"
    server_app.log.info(f"Registered {name} server extension")



async def initialize(nbapp, virtual_documents_uri):  # pragma: no cover
    """Perform lazy initialization."""
    manager :LanguageServerManager = nbapp.language_server_manager

    nbapp.log.debug(
        "[lsp] The following Language Servers will be available: {}".format(
            json.dumps(manager.language_servers, indent=2, sort_keys=True)
        )
    )


def load_jupyter_server_extension(nbapp):
    """create a LanguageServerManager and add handlers"""
    nbapp.add_traits(language_server_manager=traitlets.Instance(LanguageServerManager))
    manager = nbapp.language_server_manager = LanguageServerManager(parent=nbapp)

    contents = nbapp.contents_manager
    page_config = nbapp.web_app.settings.setdefault("page_config_data", {})

    root_uri = ""
    virtual_documents_uri = ""

    # try to set the rootUri from the contents manager path
    if hasattr(contents, "root_dir"):
        root_uri = normalized_uri(contents.root_dir)
        nbapp.log.debug("[lsp] rootUri will be %s", root_uri)
        virtual_documents_uri = normalized_uri(
            Path(contents.root_dir) / manager.virtual_documents_dir
        )
        nbapp.log.debug("[lsp] virtualDocumentsUri will be %s", virtual_documents_uri)
    else:  # pragma: no cover
        nbapp.log.warn(
            "[lsp] %s did not appear to have a root_dir, could not set rootUri",
            contents,
        )
    page_config.update(rootUri=root_uri, virtualDocumentsUri=virtual_documents_uri)

    nbapp.io_loop.call_later(0, initialize, nbapp, virtual_documents_uri)


# For backward compatibility with notebook server - useful for Binder/JupyterHub
load_jupyter_server_extension = _load_jupyter_server_extension

