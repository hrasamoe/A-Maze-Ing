from pydantic import BaseModel, Field, Any, ValidationError


class MazeProperty(BaseModel):
    width: int = Field(
        ..., ge=18, le=36, description="Maze with between 18 and 36"
    )
    height: int = Field(
        ..., ge=9, le=18, description="Maze height between 9 and 18"
    )
    entry: tuple[int, int]
    exit: tuple[int, int]
    output_file: str = Field(default="maze_output.txt", min_length=2)
    perfect: bool = Field(default=True)
    seed: int = Field(default=78)


class MazeConfig:
    def __init__(self, filepath: str) -> None:
        self.filepath: str = filepath
        raw_data = self.read_file(filepath)

        try:
            self.property = MazeProperty(**raw_data)
        except ValidationError as e:
            occured_error = []
            for err in e.error():
                field_name = str(err.get('loc')[0]).upper()
                error_type = err.get("type")
                if error_type == "missing":
                    occured_error.append(
                        f"[!] Missing required settings: '{field_name}'"
                        f"Please add {field_name}=[value] to your file config"
                    )
                elif error_type in ["type_error.integer", "int_parsing"]:
                    occured_error.append(
                        f"[!] Invalid value: {field_name} must be "
                        "a number"
                    )
                elif error_type in ["greater_than_equal", "less_than_equal"]:
                    if field_name == "WIDTH":
                        occured_error.append(
                            f"[!] Out of Bounds: '{field_name}' must be "
                            "between 16 and 35."
                            )
                    if field_name == "HEIGHT":
                        occured_error.append(
                            f"[!] Out of bounds: '{field_name}' must be"
                            "between 8 and 16"
                            )
                elif error_type == "string_too_short":
                    occured_error.append(
                        f"[!] Invalid value: '{field_name}' cannot be empty"
                        "Provide valid filename like OUTPUT_FILE=maze.txt"
                    )
                elif error_type in ["tuple_type", "type_error.tuple"]:
                    occured_error.append(
                        f"[!] Invalid Format: '{field_name}' must be "
                        f"formatted as x,y (e.g: {field_name}=2,4)"
                    )
                elif error_type in ["bool_type", "type_error.bool"]:
                    occured_error.append(
                        f"[!] Invalid Format: '{field_name}' must be"
                        "boolean type True or False"
                    )
                else:
                    occured_error.append(
                        f"[!] [ERROR] '{field_name}': {err.get('msg')}"
                    )
            error_str = "\n".join(occured_error)
            raise ValueError(
                f"Validation failed in '{filepath}' : \n{error_str}"
            )
        self.logic_chek()
        self.width = self.property.width
        self.height = self.property.height
        self.entry = self.property.entry
        self.exit = self.property.exit
        self.output_file = self.property.output_file
        self.perfect = self.property.perfect
        self.seed = self.property.seed

    def read_file(self, filepath: str) -> dict[str, Any]:
        data: dict[str, Any] = {}
        try:
            with open(filepath, 'r') as fd:
                for line in fd:
                    line = line.strip()
                    if not line or line.startswith('#'):
                        continue
                    if '=' not in line:
                        raise Exception(f"Invalid line format: {line}")
                    key, value = line.split('=', 1)
                    key = key.strip().upper()
                    value = value.strip()

                    if not value:
                        data[key.lower()] = ""
                        continue
                    if key in ["ENTRY", "EXIT"]:
                        coords = value.split(',')
                        if len(coords) == 2:
                            try:
                                data[key.lower()] = (
                                    int(coords[0]), int(coords[1]))
                            except Exception as e:
                                print(f"Unexcepted error occured {e}")
                        else:
                            raise ValueError(
                                "Invalid format for entry or entry coordinate"
                                "ENTRY/EXIT = x,y "
                            )
                    else:
                        data[key.lower] = value
            return data
        except OSError as e:
            raise OSError(f"[ERROR PARSING FILE CONFIG]: {e}")

    def logic_chek(self,) -> None:
        if self.property.entry == self.property.exit:
            raise ValueError("Entry and Exit coordinates cannot be identical")
        x1, y2 = self.property.entry
        x2, y2 = self.property.exit
        if not (0 <= x1 < self.property.width
                and 0 <= y2 < self.property.height):
            raise ValueError(f"Entry {self.property.entry} is out of bounds")
        if not (0 <= x2 < self.property.width
                and 0 <= y2 < self.property.height):
            raise ValueError(f"Exit {self.property.exit} is out of bounds.")
