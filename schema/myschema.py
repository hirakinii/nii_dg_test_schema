"""myschema.py
A test set of validation rules for MySchema.
"""


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
from nii_dg.utils import load_schema_file

if TYPE_CHECKING:
    from nii_dg.ro_crate import ROCrate


SCHEMA_NAME = Path(__file__).stem
SCHEMA_FILE_PATH = Path(__file__).resolve().parent.joinpath(f"{SCHEMA_NAME}.yml")
SCHEMA_DEF = load_schema_file(SCHEMA_FILE_PATH)


class MySchema(DataEntity):
    def __init__(
        self,
        id_: str,
        props: Dict[str, Any] = {},
        schema_name: str = SCHEMA_NAME,
        entity_def: EntityDef = SCHEMA_DEF["MySchema"],
    ):
        super().__init__(id_, props, schema_name, entity_def)

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
