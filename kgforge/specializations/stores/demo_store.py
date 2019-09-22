from abc import ABC, abstractmethod
from pathlib import Path
from typing import Dict, Optional, Union

from kgforge.core.commons.actions import run, Actions
from kgforge.core.storing.exceptions import RegistrationError
from kgforge.core.storing.store import Store
from kgforge.core.commons.attributes import not_supported
from kgforge.core.commons.typing import FilePath, Hjson, ManagedData, URL, dispatch
from kgforge.core.resources import Resource, Resources


class DemoStore(Store):

    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        # FIXME Should demo the loading of file_mapping from a Hjson, a file, or an URL.
        self.files_mapping = """
            FIXME
        """
        self._data = {}
        self._archives = {}

    # [C]RUD

    def register(self, data: ManagedData, update: bool) -> None:
        # POLICY Values of type LazyAction should be processed first.
        # POLICY Resource _last_action, _synchronized and _store_metadata should be updated.
        # POLICY Should notify of failures with exception RegistrationError including a message.
        # POLICY Should call actions.run() to update the status and deal with exceptions.
        # POLICY Should print Resource _last_action before returning.
        dispatch(data, self._register_many, self._register_one, update)

    def _register_many(self, resources: Resources, update: bool) -> None:
        for x in resources:
            run(self._register, "_synchronized", x, update)
        print(Actions.from_resources(resources))

    def _register_one(self, resource: Resource, update: bool) -> None:
        run(self._register, "_synchronized", resource, update)
        print(resource._last_action)

    # Demo implementation.
    def _register(self, resource: Resource, update: bool) -> Dict:
        rid = resource.id
        if rid in self._data.keys():
            if update:
                pr, pv = self._data[rid]
                self._archives[f"{rid}_{pv}"] = pr
                self._data[rid] = (resource, pv + 1)
            else:
                raise RegistrationError("resource already exists")
        else:
            self._data[rid] = (resource, 1)

    def upload(self, path: str) -> ManagedData:
        # POLICY Should use self.files_mapping to map Store metadata to Model metadata.
        # POLICY Resource _synchronized should be set to True.
        # POLICY Should notify of failures with exception UploadingError including a message.
        # POLICY Should be decorated with exceptions.catch() to deal with exceptions.
        p = Path(path)
        return self._upload_many(p) if p.is_dir() else self._upload_one(p)

    def _upload_many(self, dirpath: Path) -> Resources:
        # POLICY Follow upload() policies.
        not_supported()

    def _upload_one(self, filepath: Path) -> Resource:
        # POLICY Follow upload() policies.
        not_supported()

    # C[R]UD

    @abstractmethod
    def retrieve(self, id: str, version: Optional[Union[int, str]] = None) -> Resource:
        # POLICY Resource _synchronized should be set to True and _store_metadata should be set.
        # POLICY Should notify of failures with exception RetrievalError including a message.
        # POLICY Should be decorated with exceptions.catch() to deal with exceptions.
        pass

    def download(self, data: ManagedData, follow: str, path: str) -> None:
        # POLICY Should notify of failures with exception DownloadingError including a message.
        # POLICY Should be decorated with exceptions.catch() to deal with exceptions.
        not_supported()

    # CR[U]D

    def update(self, data: ManagedData) -> None:
        # POLICY Should call Store.register() with update=True.
        # POLICY Follow register() policies.
        self.register(data, update=True)

    def tag(self, data: ManagedData, value: str) -> None:
        # POLICY Resource _synchronized might be set to True and _store_metadata might be set.
        # POLICY Should notify of failures with exception TaggingError including a message.
        # POLICY Might call actions.run() if the specialization is modifying the resources.
        # POLICY In this case, should print Resource _last_action before returning.
        # POLICY Otherwise, should be decorated with exceptions.catch() to deal with exceptions.
        not_supported()

    # CRU[D]

    def deprecate(self, data: ManagedData) -> None:
        # POLICY Resource _last_action, _synchronized and _store_metadata should be updated.
        # POLICY Should notify of failures with exception DeprecationError including a message.
        # POLICY Should call actions.run() to update the status and deal with exceptions.
        # POLICY Should print Resource _last_action before returning.
        not_supported()

    # Query

    @abstractmethod
    def search(self, resolver, *filters, **params) -> Resources:
        # POLICY Resource _synchronized should be set to True and _store_metadata should be set.
        # POLICY Should notify of failures with exception QueryingError including a message.
        # POLICY Should be decorated with exceptions.catch() to deal with exceptions.
        pass

    def sparql(self, prefixes: Dict[str, str], query: str) -> Resources:
        # POLICY Follow search() policies.
        not_supported()

    # Versioning

    def freeze(self, resource: Resource) -> None:
        # POLICY Resource _synchronized and _validated should be set to False.
        # POLICY Should notify of failures with exception FreezingError including a message.
        # POLICY Should call actions.run() to update the status and deal with exceptions.
        # POLICY Should print Resource _last_action before returning.
        not_supported()