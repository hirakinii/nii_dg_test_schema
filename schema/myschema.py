"""myschema.py
A test set of validation rules for MySchema.
"""


import json
from pathlib import Path
from typing import TYPE_CHECKING, Any, Dict, List
from urllib.request import urlopen

from nii_dg.check_functions import (check_entity_values, is_absolute_path,
                                    is_content_size, is_email,
                                    is_encoding_format, is_iso8601, is_orcid,
                                    is_phone_number, is_relative_path,
                                    is_sha256, is_url, is_url_accessible)
from nii_dg.entity import ContextualEntity, DataEntity, EntityDef
from nii_dg.error import EntityError
from nii_dg.utils import load_schema_file, generate_ctx
from nii_dg.module_info import GH_REF, GH_REPO

if TYPE_CHECKING:
    from nii_dg.ro_crate import ROCrate


SCHEMA_NAME = Path(__file__).stem
SCHEMA_FILE_PATH = Path(__file__).resolve().parent.joinpath(f"{SCHEMA_NAME}.yml")
SCHEMA_DEF = load_schema_file(SCHEMA_FILE_PATH)

PACKAGE_INFO_PATH = Path(__file__).resolve().parent.resolve().parent.joinpath("package_info.json")


class MySchema(DataEntity):
    """MySchema
    """
    def __init__(
        self,
        id_: str,
        props: Dict[str, Any] = {},
        schema_name: str = SCHEMA_NAME,
        entity_def: EntityDef = SCHEMA_DEF["MySchema"],
    ):
        super().__init__(id_, props, schema_name, entity_def)

        # because the super.__init__() force to set GH_REPO and GH_REF, we should replace them.
        package_info: dict = None
        with open(PACKAGE_INFO_PATH, "r", encoding="utf-8") as ff:
            package_info = json.load(ff)
        repo_owner = package_info.get("REPO_OWNER")
        repo_name = package_info.get("REPO_NAME")
        gh_repo = ""
        if repo_owner is None or repo_name is None:
            gh_repo = f"{repo_owner}/{repo_name}"
        else:
            gh_repo = GH_REPO
        gh_ref = package_info.get("REPO_REF", GH_REF)
        self.data["@context"] = generate_ctx(gh_repo, gh_ref, schema_name=schema_name)

    def check_props(self) -> None:
        super().check_props()

        error = check_entity_values(
            self,
            {
                "url": is_url,
            },
        )
        if not self.id.endswith("/"):
            error.add("@id", "The id MUST end with `/`.")
        if not is_relative_path(self.id):
            error.add("@id", "The id MUST be a relative path.")

        if error.has_error():
            raise error

    def validate(self, crate: "ROCrate") -> None:
        super().validate(crate)

        error = EntityError(self)

        if self.message is not None and not isinstance(self.message, str):
            error.add("message", "Invalid type of `message.`")

        if error.has_error():
            raise error
