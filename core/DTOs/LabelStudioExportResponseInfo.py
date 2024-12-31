from typing import Annotated

from pydantic import BaseModel
from fastapi.param_functions import Doc


class LabelStudioExportResponseInfo(BaseModel):
    label_studio_import_id: Annotated[int, Doc("The ID of the Label Studio import")]
    num_urls_imported: Annotated[int, Doc("The number of URLs imported")]