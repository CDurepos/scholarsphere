header_id_options = "h1"


def get_headers(header_id: str):
    match header_id:
        case "h1":
            return {
                "User-Agent": (
                    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                    "AppleWebKit/537.36 (KHTML, like Gecko) "
                    "Chrome/126.0.0.0 Safari/537.36"
                ),
                "Accept-Language": "en-US,en;q=0.9",
            }
        case _:
            raise NameError(
                f"The provided header_id {header_id} is not an option. Valid ids: {header_id_options}"
            )
