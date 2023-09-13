from dataclasses import dataclass, field

from guardian_lib.models.settings import SETTINGS_NAME_METADATA


@dataclass
class FastAPIOAuth2AdapterSettings:
    well_known_url: str = field(
        metadata={SETTINGS_NAME_METADATA: "oauth_adapter.well_known_url"}
    )
    well_known_url_secure: bool = field(
        metadata={SETTINGS_NAME_METADATA: "oauth_adapter.well_known_url_secure"}
    )
